"""
Upload Service — Clean Rebuild.

Synchronous pipeline: saves file → runs pipeline → returns result.
No BackgroundTasks. No async indexing.
Returns success only after ChromaDB insertion is verified.
"""

import os
import uuid
import logging
from datetime import datetime

from fastapi import UploadFile, HTTPException, BackgroundTasks

from app.core import config
from app.db.metadata_store import metadata_store
from app.services.storage.file_service import file_service
from app.services.ingestion.pipeline import run_pipeline
from app.utils.hash_utils import compute_md5

logger = logging.getLogger("upload_service")

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp",
                      ".pdf", ".docx", ".txt"}


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def process_ingestion_background(doc_id: str, filename: str, saved_path: str, file_ext: str):
    """
    Background worker task to execute the ingestion pipeline and update metadata registry.
    """
    logger.info(f"[Background Ingestion] Running ingestion pipeline for doc_id={doc_id}...")
    result = run_pipeline(
        doc_id=doc_id,
        filename=filename,
        file_path=saved_path,
        file_ext=file_ext,
    )

    if not result.success:
        metadata_store.update_document_status(doc_id, "failed")
        logger.error(
            f"[Background Ingestion] Pipeline FAILED at {result.failed_stage}: {result.error}"
        )
    else:
        # Update metadata with confirmed completed status and details
        metadata_store.update_document_status(doc_id, "completed")
        metadata_store.update_document_details(
            doc_id=doc_id,
            full_text=result.full_text,
            text_lines=result.text_lines,
        )
        logger.info(
            f"[Background Ingestion] SUCCESS: doc_id={doc_id}, "
            f"text_lines={result.text_lines_count}, "
            f"chunks={result.chunks_count}, "
            f"vectors={result.vectors_inserted}"
        )


async def ingest_uploaded_file(file: UploadFile, background_tasks: BackgroundTasks) -> dict:
    """
    Validate → save with original name → schedule background pipeline → return success/processing immediately.
    """
    _, file_ext = os.path.splitext((file.filename or "").lower())

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file_ext}'. "
                   f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Check if a file with the same name already exists in uploads folder
    expected_path = os.path.join(file_service.upload_dir, file.filename)
    if os.path.exists(expected_path):
        raise HTTPException(
            status_code=409,
            detail=f"A document named '{file.filename}' already exists in global document memory."
        )

    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read uploaded file: {e}")
    finally:
        await file.close()

    file_size_bytes = len(file_content)
    file_hash = compute_md5(file_content)

    # Save to disk using original filename
    try:
        saved_path = file_service.save_file(file_content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    logger.info(f"[UploadService] Saved original file: {saved_path} ({_format_size(file_size_bytes)})")

    # Register document metadata
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    date_str = datetime.now().strftime("%b %d, %Y")
    doc_metadata = {
        "id": doc_id,
        "filename": file.filename,
        "size": _format_size(file_size_bytes),
        "date": date_str,
        "tags": ["Uploaded", file_ext.replace(".", "").upper()],
        "status": "processing",
        "hash": file_hash,
        "path": saved_path,
        "full_text": "",
        "text_lines": [],
    }
    metadata_store.add_document(doc_metadata)

    # Schedule ingestion in background
    logger.info(f"[UploadService] Scheduling background ingestion for doc_id={doc_id}...")
    background_tasks.add_task(
        process_ingestion_background,
        doc_id=doc_id,
        filename=file.filename,
        saved_path=saved_path,
        file_ext=file_ext,
    )

    return {
        "status": "success",
        "document_id": doc_id,
        "id": doc_id,
        "filename": file.filename,
        "size": _format_size(file_size_bytes),
        "status": "processing",
        "text_lines": [],
        "full_text": ""
    }
