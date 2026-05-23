import uuid
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.metadata_store import metadata_store

logger = logging.getLogger("folder_routes")

router = APIRouter(prefix="/api")

class FolderCreateRequest(BaseModel):
    name: str
    description: str = ""

@router.get("/folders")
def list_folders():
    """
    Lists all folders in global AI index database.
    """
    logger.info("Listing folder hierarchies...")
    return metadata_store.get_folders()

@router.post("/folders")
def create_folder(request: FolderCreateRequest):
    """
    Creates a new structural folder.
    """
    logger.info(f"Creating new category folder '{request.name}'...")
    folder_id = f"folder_{uuid.uuid4().hex[:8]}"
    folder_data = {
        "id": folder_id,
        "name": request.name,
        "description": request.description,
        "document_ids": []
    }
    return metadata_store.add_folder(folder_data)

@router.post("/folders/{folder_id}/documents/{doc_id}")
def bind_document_to_folder(folder_id: str, doc_id: str):
    """
    Maps an indexed document to a folder category hierarchy.
    """
    logger.info(f"Binding document {doc_id} to folder {folder_id}...")
    folder = metadata_store.get_folder_by_id(folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
        
    metadata_store.add_doc_to_folder(folder_id, doc_id)
    return {"status": "success", "message": f"Document {doc_id} successfully mapped to folder {folder_id}."}
