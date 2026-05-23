import logging
from fastapi import APIRouter, HTTPException
from app.db.metadata_store import metadata_store

logger = logging.getLogger("document_routes")

router = APIRouter(prefix="/api")

@router.get("/documents")
def list_documents():
    """
    Returns lists of all uploaded, OCR-processed documents in global memory.
    """
    logger.info("Listing all document catalogs metadata...")
    return metadata_store.get_documents()

@router.get("/documents/{doc_id}")
def get_document(doc_id: str):
    """
    Retrieves complete layout OCR text coordinates for a given document.
    """
    doc = metadata_store.get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    """
    Deletes the document registry from documents metadata list.
    """
    logger.info(f"Deleting document registry for ID: {doc_id}")
    success = metadata_store.delete_document(doc_id)
    return {"status": "success", "message": f"Document {doc_id} deleted successfully."}
