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
    import os
    docs = metadata_store.get_documents()
    filtered_docs = []
    for doc in docs:
        file_path = doc.get("path")
        if file_path and os.path.exists(file_path):
            filtered_docs.append(doc)
    return filtered_docs


@router.get("/documents/{doc_id}")
def get_document(doc_id: str):
    """
    Retrieves complete layout OCR text coordinates for a given document.
    """
    import os
    doc = metadata_store.get_document_by_id(doc_id)
    if not doc or not doc.get("path") or not os.path.exists(doc.get("path")):
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    """
    Deletes the document registry from documents metadata list, physical file from disk, and ChromaDB vector chunks.
    """
    logger.info(f"Deleting document registry, physical file, and chunks for ID: {doc_id}")
    import os
    
    # Fetch metadata first to get path
    doc = metadata_store.get_document_by_id(doc_id)
    if doc and doc.get("path"):
        file_path = doc["path"]
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Successfully deleted physical file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete physical file {file_path}: {e}")

    try:
        from app.services.ai.rag_pipeline import rag_pipeline
        rag_pipeline.delete_document_chunks(doc_id)
    except Exception as e:
        logger.error(f"Failed to clear ChromaDB vector chunks for {doc_id}: {e}")
        
    success = metadata_store.delete_document(doc_id)
    return {"status": "success", "message": f"Document {doc_id} and its physical file/vector indices deleted successfully."}
