import logging
from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from app.services.storage.upload_service import upload_service

logger = logging.getLogger("upload_routes")

router = APIRouter()

@router.post("/api/ocr")
async def perform_ocr(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Standard multipart upload endpoint parsing documents and running OCR text extraction.
    """
    logger.info(f"Received OCR request for file: {file.filename}")
    return await upload_service.ingest_uploaded_file(file, background_tasks)

@router.post("/api/upload")
async def perform_upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Alias upload endpoint.
    """
    logger.info(f"Received upload request for file: {file.filename}")
    return await upload_service.ingest_uploaded_file(file, background_tasks)
