import os
import uuid
import logging
import json
from datetime import datetime
from fastapi import UploadFile, HTTPException, BackgroundTasks
from app.core import config
from app.db.metadata_store import metadata_store
from app.services.storage.file_service import file_service
from app.services.ocr.paddle_service import paddle_service
from app.services.ocr.pdf_service import pdf_service
from app.services.ai.rag_pipeline import rag_pipeline
from app.utils.hash_utils import compute_md5

logger = logging.getLogger("upload_service")

import time

def async_process_file_task(doc_id: str, saved_file_path: str, filename: str, file_hash: str, file_ext: str):
    logger.info(f"Background Task: Starting extraction and indexing for doc_id={doc_id}, hash={file_hash}")
    processed_file_path = os.path.join(config.PROCESSED_DIR, f"{file_hash}.json")
    
    total_start_time = time.time()
    try:
        # Step 1: Update status to "processing" (running OCR/extraction)
        metadata_store.update_document_status(doc_id, "processing")
        
        ocr_result = None
        ocr_start_time = time.time()
        # Check if the text extraction is already cached
        if os.path.exists(processed_file_path):
            logger.info(f"Background Task: MD5 hash match found in cache! Loading pre-extracted text for {filename}...")
            try:
                with open(processed_file_path, "r", encoding="utf-8") as f:
                    ocr_result = json.load(f)
                ocr_duration = time.time() - ocr_start_time
                logger.info(f"METRIC: Cache lookup duration for {filename}: {ocr_duration:.3f} seconds (duplicate OCR bypassed)")
            except Exception as e:
                logger.error(f"Error reading cached processed JSON {processed_file_path}: {e}")
                
        if not ocr_result:
            logger.info(f"Background Task: Executing active text extraction/OCR parsing for {filename}...")
            if file_ext == ".pdf":
                ocr_result = pdf_service.extract_pdf_ocr(saved_file_path)
            else:
                ocr_result = paddle_service.extract_text(saved_file_path)
                
            ocr_duration = time.time() - ocr_start_time
            logger.info(f"METRIC: OCR/Extraction time for {filename}: {ocr_duration:.3f} seconds")
            
            if ocr_result.get("status") == "error":
                raise Exception(ocr_result.get("message", "Extraction failed"))
                
            # Save extraction to hash cache directory
            try:
                with open(processed_file_path, "w", encoding="utf-8") as f:
                    json.dump(ocr_result, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved extracted text cache to {processed_file_path}")
            except Exception as e:
                logger.error(f"Error saving processed cache for hash {file_hash}: {e}")

        # Step 2: Update status to "indexing"
        metadata_store.update_document_status(doc_id, "indexing")
        
        # Save details in documents.json
        metadata_store.update_document_details(
            doc_id=doc_id,
            text_lines=ocr_result.get("text_lines", []),
            full_text=ocr_result.get("full_text", "")
        )
        
        # Trigger RAG pipeline indexing in local ChromaDB
        indexing_start_time = time.time()
        logger.info(f"Background Task: Triggering ChromaDB RAG indexing for {filename}...")
        success = rag_pipeline.index_document(
            doc_id=doc_id,
            filename=filename,
            text_lines=ocr_result.get("text_lines", [])
        )
        
        indexing_duration = time.time() - indexing_start_time
        logger.info(f"METRIC: ChromaDB Indexing time for {filename}: {indexing_duration:.3f} seconds")
        
        if not success:
            raise Exception("ChromaDB vector indexing failed")
            
        # Step 3: Update status to "completed"
        metadata_store.update_document_status(doc_id, "completed")
        
        total_duration = time.time() - total_start_time
        logger.info(f"METRIC: Total background task duration for {filename}: {total_duration:.3f} seconds (SUCCESS)")
        
    except Exception as e:
        logger.error(f"Background Task Error processing file {filename}: {e}", exc_info=True)
        metadata_store.update_document_status(doc_id, "failed")

class UploadService:
    def format_size(self, size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    async def ingest_uploaded_file(self, file: UploadFile, background_tasks: BackgroundTasks) -> dict:
        """
        Coordinates full upload ingestion: saving the file raw, generating metadata
        with status 'uploading', and deferring processing to background tasks.
        """
        allowed_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".pdf"}
        _, file_ext = os.path.splitext(file.filename.lower())
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{file_ext}'. Allowed formats: {', '.join(allowed_extensions)}"
            )

        # Generate a unique uuid filename to avoid naming conflicts on disk
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        
        try:
            # Read binary file content in memory
            file_content = await file.read()
            file_size_bytes = len(file_content)
            
            # Save raw file locally inside uploads folder
            saved_file_path = file_service.save_file(file_content, unique_filename)
            logger.info(f"Uploaded file saved at: {saved_file_path}")
            
            # Compute MD5 Hash
            file_hash = compute_md5(file_content)
            logger.info(f"Computed file MD5 hash: {file_hash}")

            # Scaffold document metadata model
            doc_id = f"doc_{uuid.uuid4().hex[:8]}"
            date_str = datetime.now().strftime("%b %d, %Y")
            
            doc_metadata = {
                "id": doc_id,
                "filename": file.filename,
                "size": self.format_size(file_size_bytes),
                "date": date_str,
                "tags": ["Uploaded", file_ext.replace(".", "").upper()],
                "status": "uploading",
                "hash": file_hash,
                "path": saved_file_path,
                "full_text": "",
                "text_lines": []
            }

            # Save metadata locally into documents.json using MetadataStore
            metadata_store.add_document(doc_metadata)

            # Enqueue asynchronous processing task
            background_tasks.add_task(
                async_process_file_task,
                doc_id,
                saved_file_path,
                file.filename,
                file_hash,
                file_ext
            )
            
            return {
                "status": "success",
                "document_id": doc_id,
                "filename": file.filename,
                "size": doc_metadata["size"],
                "tags": doc_metadata["tags"],
                "processing_state": "uploading"
            }

        except Exception as e:
            logger.error(f"Error handling file upload ingestion: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await file.close()

upload_service = UploadService()
