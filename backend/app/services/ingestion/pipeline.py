"""
Document Ingestion Pipeline — Single Linear Flow.

run_pipeline(doc_id, filename, file_path, file_ext) -> PipelineResult

Stages (in order):
  1  Extract text      → FAIL if text_lines == 0
  2  Chunk text        → FAIL if chunks == 0
  3  Generate Jina embeddings → FAIL if len(embeddings) != len(chunks)
  4  Insert into ChromaDB
  5  Verify insertion  → FAIL if retrieved count != inserted count

No background tasks. No async indexing.
Returns only after ChromaDB is verified.
"""

import os
import json
import time
import logging
import traceback
import uuid
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Optional

from app.core import config
from app.services.ocr import pdf_service
from app.services.ocr import paddle_service
from app.services.ai.embeddings_service import embeddings_service
from app.db.chroma import chroma_wrapper

logger = logging.getLogger("ingestion_pipeline")

CHUNK_SIZE = 300   # words per chunk (smaller = more granular retrieval)
CHUNK_OVERLAP = 50  # word overlap between chunks


# ── Result type ────────────────────────────────────────────────────────────────

@dataclass
class PipelineResult:
    success: bool
    error: str = ""
    failed_stage: str = ""
    # Stage diagnostics
    text_lines_count: int = 0
    chunks_count: int = 0
    embeddings_count: int = 0
    vectors_inserted: int = 0
    collection_count: int = 0
    extraction_source: str = ""
    text_lines: List[dict] = field(default_factory=list)
    full_text: str = ""


# ── Chunking (plain text lines) ────────────────────────────────────────────────

def _chunk_lines(text_lines: List) -> List[dict]:
    """
    Split a flat list of text line dicts (or strings) into overlapping chunks.
    Each chunk dict has:
      "text": chunk_text,
      "pages": list of page numbers,
      "box": list of coordinates
    """
    normalized = []
    for idx, line in enumerate(text_lines):
        if isinstance(line, dict):
            normalized.append(line)
        else:
            normalized.append({
                "text": str(line),
                "page": 1,
                "box": [],
                "confidence": 1.0
            })

    chunks = []
    line_word_counts = [len(l["text"].split()) for l in normalized]

    i = 0
    while i < len(normalized):
        current_words_count = 0
        chunk_lines = []
        j = i
        while j < len(normalized) and current_words_count < CHUNK_SIZE:
            current_words_count += line_word_counts[j]
            chunk_lines.append(normalized[j])
            j += 1

        if not chunk_lines:
            break

        chunk_text = " ".join([l["text"] for l in chunk_lines]).strip()
        pages = sorted(list(set([l.get("page", 1) for l in chunk_lines])))

        box = []
        for l in chunk_lines:
            if l.get("box"):
                box.extend(l["box"])

        if chunk_text:
            chunks.append({
                "text": chunk_text,
                "pages": pages,
                "box": box
            })

        overlap_words = 0
        overlap_lines_count = 0
        for l in reversed(chunk_lines):
            overlap_words += len(l["text"].split())
            overlap_lines_count += 1
            if overlap_words >= CHUNK_OVERLAP:
                break

        next_i = j - overlap_lines_count
        if next_i <= i:
            next_i = i + 1

        if j >= len(normalized):
            break

        i = next_i

    logger.info(f"[Pipeline] Chunked {sum(line_word_counts)} words → {len(chunks)} chunks "
                f"(size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks


# ── File-type extractors ───────────────────────────────────────────────────────

def _extract_pdf(file_path: str) -> dict:
    return pdf_service.extract(file_path)


def _extract_docx(file_path: str) -> dict:
    try:
        text_lines = []
        with zipfile.ZipFile(file_path) as z:
            xml_content = z.read("word/document.xml")
        root = ET.fromstring(xml_content)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paras = root.findall(".//w:p", ns)
        for idx, para in enumerate(paras):
            runs = para.findall(".//w:t", ns)
            text = "".join(t.text for t in runs if t.text).strip()
            if text:
                y0 = int((idx / max(len(paras), 1)) * 1000)
                y1 = int(((idx + 1) / max(len(paras), 1)) * 1000)
                box = [[100, y0], [900, y0], [900, y1], [100, y1]]
                text_lines.append({
                    "text": text,
                    "box": box,
                    "confidence": 1.0,
                    "page": 1
                })
        if not text_lines:
            return {"success": False, "error": "DOCX contained no text paragraphs."}
        full_text = "\n".join([line["text"] for line in text_lines])
        return {"success": True, "text_lines": text_lines,
                "full_text": full_text, "source": "docx"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _extract_txt(file_path: str) -> dict:
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        lines = [l.strip() for l in content.splitlines() if l.strip()]
        if not lines:
            return {"success": False, "error": "TXT file is empty."}
        
        text_lines = []
        for idx, l in enumerate(lines):
            y0 = int((idx / max(len(lines), 1)) * 1000)
            y1 = int(((idx + 1) / max(len(lines), 1)) * 1000)
            box = [[100, y0], [900, y0], [900, y1], [100, y1]]
            text_lines.append({
                "text": l,
                "box": box,
                "confidence": 1.0,
                "page": 1
            })
            
        return {"success": True, "text_lines": text_lines,
                "full_text": content, "source": "txt"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _extract_image(file_path: str) -> dict:
    result = paddle_service.run(file_path)
    if not result.success:
        return {"success": False, "error": result.error}
    if not result.text_lines:
        return {"success": False,
                "error": f"PaddleOCR returned 0 text lines for image. "
                         f"Markdown chars={len(result.markdown)}."}
    return {"success": True, "text_lines": result.text_lines,
            "full_text": result.markdown, "source": "paddleocr"}


# ── Main pipeline ──────────────────────────────────────────────────────────────

def run_pipeline(doc_id: str, filename: str, file_path: str, file_ext: str) -> PipelineResult:
    """
    Execute the full synchronous ingestion pipeline for one document.
    Returns PipelineResult. Never raises — all errors are captured.
    """
    pipeline_start = time.time()

    logger.info("=" * 60)
    logger.info(f"PIPELINE START")
    logger.info(f"  doc_id   : {doc_id}")
    logger.info(f"  filename : {filename}")
    logger.info(f"  file_ext : {file_ext}")
    logger.info(f"  file_path: {file_path}")
    try:
        logger.info(f"  file_size: {os.path.getsize(file_path)} bytes")
    except Exception:
        logger.info("  file_size: unknown")
    logger.info("=" * 60)

    # ── Stage 1: Extract text ─────────────────────────────────────────────────
    logger.info("")
    logger.info("========== STAGE 1 START: Extract Text ==========")
    logger.info(f"  filename : {filename}")
    logger.info(f"  file_ext : {file_ext.lower()}")
    stage1_start = time.time()

    ext = file_ext.lower()
    try:
        if ext == ".pdf":
            logger.info("  extractor: pdf_service.extract()")
            extraction = _extract_pdf(file_path)
        elif ext == ".docx":
            logger.info("  extractor: _extract_docx()")
            extraction = _extract_docx(file_path)
        elif ext == ".txt":
            logger.info("  extractor: _extract_txt()")
            extraction = _extract_txt(file_path)
        elif ext in {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}:
            logger.info("  extractor: paddle_service.run() [image]")
            extraction = _extract_image(file_path)
        else:
            logger.error(f"  FAIL: Unsupported extension: {ext}")
            return PipelineResult(
                success=False,
                failed_stage="Stage 1: Extract",
                error=f"Unsupported file extension: {ext}"
            )
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"  EXCEPTION in Stage 1 extractor: {type(e).__name__}: {e}")
        logger.error(f"  TRACEBACK:\n{tb}")
        return PipelineResult(
            success=False,
            failed_stage="Stage 1: Extract",
            error=f"Extractor raised {type(e).__name__}: {e}"
        )

    stage1_elapsed = time.time() - stage1_start

    logger.info(f"  extractor returned: success={extraction.get('success')}")
    logger.info(f"  source            : {extraction.get('source', 'N/A')}")
    logger.info(f"  text_lines count  : {len(extraction.get('text_lines', []))}")
    if not extraction.get("success"):
        logger.error(f"  error             : {extraction.get('error', 'unknown')}")

    if not extraction.get("success"):
        logger.error(f"  FAIL — Stage 1 returned success=False")
        logger.error(f"  reason: {extraction.get('error', 'Unknown extraction error.')}")
        logger.info(f"========== STAGE 1 END (FAILED) — elapsed={stage1_elapsed:.3f}s ==========")
        return PipelineResult(
            success=False,
            failed_stage="Stage 1: Extract",
            error=extraction.get("error", "Unknown extraction error.")
        )

    text_lines: List[str] = extraction["text_lines"]
    extraction_source: str = extraction.get("source", "unknown")

    if not text_lines:
        logger.error(f"  FAIL — extraction success=True but text_lines is empty")
        logger.info(f"========== STAGE 1 END (FAILED) — elapsed={stage1_elapsed:.3f}s ==========")
        return PipelineResult(
            success=False,
            failed_stage="Stage 1: Extract",
            error="Extraction succeeded but returned 0 text lines.",
            extraction_source=extraction_source,
        )

    preview_str = text_lines[0].get("text", "") if isinstance(text_lines[0], dict) else str(text_lines[0])
    total_chars = sum(len(l.get("text", "")) if isinstance(l, dict) else len(str(l)) for l in text_lines)
    logger.info(f"  text_lines[0] preview: {preview_str[:120]!r}")
    logger.info(f"  total chars in all lines: {total_chars}")
    logger.info(f"========== STAGE 1 END (OK) — text_lines={len(text_lines)}, source={extraction_source}, elapsed={stage1_elapsed:.3f}s ==========")

    # ── Stage 2: Chunk text ───────────────────────────────────────────────────
    logger.info("")
    logger.info("========== STAGE 2 START: Chunk Text ==========")
    logger.info(f"  input text_lines : {len(text_lines)}")
    logger.info(f"  total input chars: {total_chars}")
    stage2_start = time.time()

    chunks = _chunk_lines(text_lines)

    stage2_elapsed = time.time() - stage2_start
    logger.info(f"  chunks produced  : {len(chunks)}")
    for i, c in enumerate(chunks[:3]):
        logger.info(f"  chunk[{i}] ({len(c['text'])} chars): {c['text'][:80]!r}...")

    if not chunks:
        logger.error(f"  FAIL — chunker produced 0 chunks")
        logger.info(f"========== STAGE 2 END (FAILED) — elapsed={stage2_elapsed:.3f}s ==========")
        return PipelineResult(
            success=False,
            failed_stage="Stage 2: Chunk",
            error="Chunker produced 0 chunks from non-empty text_lines.",
            text_lines_count=len(text_lines),
            extraction_source=extraction_source,
        )

    logger.info(f"========== STAGE 2 END (OK) — chunks={len(chunks)}, elapsed={stage2_elapsed:.3f}s ==========")

    # ── Stage 3: Generate embeddings ──────────────────────────────────────────
    logger.info("")
    logger.info("========== STAGE 3 START: Jina Embeddings ==========")
    logger.info(f"  chunks to embed  : {len(chunks)}")
    logger.info(f"  Jina model       : jina-embeddings-v4")
    logger.info(f"  Jina endpoint    : https://api.jina.ai/v1/embeddings")
    logger.info(f"  JINA_API_KEY set : {'yes' if config.JINA_API_KEY else 'NO — KEY MISSING'}")
    stage3_start = time.time()

    try:
        embeddings = embeddings_service.get_embeddings([c["text"] for c in chunks])
    except Exception as e:
        tb = traceback.format_exc()
        stage3_elapsed = time.time() - stage3_start
        logger.error(f"  EXCEPTION in Stage 3: {type(e).__name__}: {e}")
        logger.error(f"  TRACEBACK:\n{tb}")
        logger.info(f"========== STAGE 3 END (FAILED) — elapsed={stage3_elapsed:.3f}s ==========")
        return PipelineResult(
            success=False,
            failed_stage="Stage 3: Embed",
            error=f"Jina embeddings API error: {type(e).__name__}: {e}",
            text_lines_count=len(text_lines),
            chunks_count=len(chunks),
            extraction_source=extraction_source,
        )

    stage3_elapsed = time.time() - stage3_start
    logger.info(f"  embeddings returned: {len(embeddings)}")
    logger.info(f"  expected           : {len(chunks)}")
    if embeddings:
        logger.info(f"  embedding[0] dims  : {len(embeddings[0])}")

    if len(embeddings) != len(chunks):
        logger.error(f"  FAIL — embedding count mismatch: got={len(embeddings)}, expected={len(chunks)}")
        logger.info(f"========== STAGE 3 END (FAILED) — elapsed={stage3_elapsed:.3f}s ==========")
        return PipelineResult(
            success=False,
            failed_stage="Stage 3: Embed",
            error=f"Embedding count mismatch: got {len(embeddings)}, expected {len(chunks)}.",
            text_lines_count=len(text_lines),
            chunks_count=len(chunks),
            extraction_source=extraction_source,
        )

    logger.info(f"========== STAGE 3 END (OK) — embeddings={len(embeddings)}, dims={len(embeddings[0])}, elapsed={stage3_elapsed:.3f}s ==========")

    # ── Stage 4: Insert into ChromaDB ─────────────────────────────────────────
    logger.info("")
    logger.info("========== STAGE 4 START: ChromaDB Insert ==========")
    collection = chroma_wrapper.get_collection()
    count_before = collection.count()
    logger.info(f"  collection count BEFORE insert: {count_before}")
    logger.info(f"  vectors to insert             : {len(chunks)}")

    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = []
    for i, chunk in enumerate(chunks):
        pages_str = ",".join([str(p) for p in chunk["pages"]])
        metadatas.append({
            "doc_id": doc_id,
            "filename": filename,
            "type": "document",
            "chunk_index": str(i),
            "pages": pages_str,
            "box_coords": json.dumps(chunk["box"])
        })

    logger.info(f"  IDs to upsert: {ids[:3]}{'...' if len(ids) > 3 else ''}")
    logger.info(f"  metadata[0]  : {metadatas[0]}")
    stage4_start = time.time()

    try:
        collection.upsert(
            ids=ids,
            documents=[c["text"] for c in chunks],
            embeddings=embeddings,
            metadatas=metadatas,
        )
    except Exception as e:
        tb = traceback.format_exc()
        stage4_elapsed = time.time() - stage4_start
        logger.error(f"  EXCEPTION in Stage 4: {type(e).__name__}: {e}")
        logger.error(f"  TRACEBACK:\n{tb}")
        logger.info(f"========== STAGE 4 END (FAILED) — elapsed={stage4_elapsed:.3f}s ==========")
        return PipelineResult(
            success=False,
            failed_stage="Stage 4: Insert",
            error=f"ChromaDB upsert error: {type(e).__name__}: {e}",
            text_lines_count=len(text_lines),
            chunks_count=len(chunks),
            embeddings_count=len(embeddings),
            extraction_source=extraction_source,
        )

    stage4_elapsed = time.time() - stage4_start
    count_after = collection.count()
    logger.info(f"  collection count AFTER insert : {count_after}")
    logger.info(f"  delta                         : {count_after - count_before}")
    logger.info(f"========== STAGE 4 END (OK) — {len(chunks)} vectors upserted, elapsed={stage4_elapsed:.3f}s ==========")

    # ── Stage 5: Verify insertion ─────────────────────────────────────────────
    logger.info("")
    logger.info("========== STAGE 5 START: Verify Insertion ==========")
    logger.info(f"  fetching IDs: {ids[:3]}{'...' if len(ids) > 3 else ''}")
    stage5_start = time.time()

    try:
        fetched = collection.get(ids=ids)
        retrieved_count = len(fetched.get("ids", []))
        collection_total = collection.count()
    except Exception as e:
        tb = traceback.format_exc()
        stage5_elapsed = time.time() - stage5_start
        logger.error(f"  EXCEPTION in Stage 5: {type(e).__name__}: {e}")
        logger.error(f"  TRACEBACK:\n{tb}")
        logger.info(f"========== STAGE 5 END (FAILED) — elapsed={stage5_elapsed:.3f}s ==========")
        return PipelineResult(
            success=False,
            failed_stage="Stage 5: Verify",
            error=f"ChromaDB verification error: {type(e).__name__}: {e}",
            text_lines_count=len(text_lines),
            chunks_count=len(chunks),
            embeddings_count=len(embeddings),
            vectors_inserted=len(chunks),
            extraction_source=extraction_source,
        )

    stage5_elapsed = time.time() - stage5_start
    retrieved_ids = fetched.get("ids", [])
    missing_ids = [i for i in ids if i not in retrieved_ids]
    logger.info(f"  inserted            : {len(chunks)}")
    logger.info(f"  retrieved           : {retrieved_count}")
    logger.info(f"  missing IDs         : {missing_ids}")
    logger.info(f"  collection total    : {collection_total}")

    if retrieved_count != len(chunks):
        logger.error(f"  FAIL — inserted {len(chunks)} but only {retrieved_count} found")
        logger.error(f"  missing IDs: {missing_ids}")
        logger.info(f"========== STAGE 5 END (FAILED) — elapsed={stage5_elapsed:.3f}s ==========")
        return PipelineResult(
            success=False,
            failed_stage="Stage 5: Verify",
            error=(
                f"Verification failed: inserted {len(chunks)} vectors "
                f"but only {retrieved_count} found in ChromaDB."
            ),
            text_lines_count=len(text_lines),
            chunks_count=len(chunks),
            embeddings_count=len(embeddings),
            vectors_inserted=retrieved_count,
            collection_count=collection_total,
            extraction_source=extraction_source,
        )

    logger.info(f"========== STAGE 5 END (OK) — verified={retrieved_count}, total={collection_total}, elapsed={stage5_elapsed:.3f}s ==========")

    pipeline_elapsed = time.time() - pipeline_start
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"PIPELINE COMPLETE — doc_id={doc_id}")
    logger.info(f"  text_lines       : {len(text_lines)}")
    logger.info(f"  chunks           : {len(chunks)}")
    logger.info(f"  embeddings       : {len(embeddings)}")
    logger.info(f"  vectors_inserted : {retrieved_count}")
    logger.info(f"  collection_total : {collection_total}")
    logger.info(f"  total elapsed    : {pipeline_elapsed:.3f}s")
    logger.info("=" * 60)

    return PipelineResult(
        success=True,
        text_lines_count=len(text_lines),
        chunks_count=len(chunks),
        embeddings_count=len(embeddings),
        vectors_inserted=retrieved_count,
        collection_count=collection_total,
        extraction_source=extraction_source,
        text_lines=text_lines,
        full_text=extraction.get("full_text", ""),
    )
