"""
Upload API Routes.

POST /api/upload        — main upload endpoint (synchronous pipeline)
POST /api/debug-index   — full pipeline with all stage counts visible
"""

import os
import logging
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks

from app.services.storage.upload_service import ingest_uploaded_file
from app.services.ingestion.pipeline import run_pipeline

logger = logging.getLogger("upload_routes")
router = APIRouter()


@router.post("/api/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Asynchronous document ingestion.
    Saves file and schedules the pipeline in the background.
    """
    logger.info(f"[Route] POST /api/upload — file={file.filename}")
    return await ingest_uploaded_file(file, background_tasks)


@router.post("/api/ocr")  # legacy alias
async def upload_ocr(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    logger.info(f"[Route] POST /api/ocr (alias) — file={file.filename}")
    return await ingest_uploaded_file(file, background_tasks)


@router.post("/api/debug-index")
async def debug_index(file: UploadFile = File(...)):
    """
    Debug endpoint: runs the full ingestion pipeline and returns every
    stage count explicitly. Nothing is hidden.

    Response shape:
    {
      "filename": "...",
      "extraction_source": "pymupdf|paddleocr|...",
      "text_lines": 186,
      "chunks": 23,
      "embeddings": 23,
      "vectors_inserted": 23,
      "collection_count": 23,
      "success": true,
      "error": null,
      "pipeline_stopped_at": null
    }
    """
    logger.info(f"[Route] POST /api/debug-index — file={file.filename}")

    _, file_ext = os.path.splitext((file.filename or "").lower())

    content = await file.read()
    await file.close()

    # Write to temp file so pipeline can use real path
    suffix = file_ext or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        import uuid
        debug_doc_id = f"debug_{uuid.uuid4().hex[:8]}"
        result = run_pipeline(
            doc_id=debug_doc_id,
            filename=file.filename or "unknown",
            file_path=tmp_path,
            file_ext=file_ext,
        )
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    return {
        "filename": file.filename,
        "extraction_source": result.extraction_source,
        "text_lines": result.text_lines_count,
        "chunks": result.chunks_count,
        "embeddings": result.embeddings_count,
        "vectors_inserted": result.vectors_inserted,
        "collection_count": result.collection_count,
        "success": result.success,
        "error": result.error if not result.success else None,
        "pipeline_stopped_at": result.failed_stage if not result.success else None,
    }
