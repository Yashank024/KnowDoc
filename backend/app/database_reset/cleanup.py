import os
import shutil
import glob
import gc
import logging
from typing import Dict, Any

from app.core import config
from app.database_reset.validators import is_path_safe_for_deletion
from app.db.chroma import chroma_wrapper
from app.services.ai.rag_pipeline import rag_pipeline

logger = logging.getLogger("database_reset.cleanup")

def clear_uploads() -> int:
    """
    Deletes all files in the uploads directory except for the .gitkeep file.
    Returns the count of deleted files.
    """
    logger.info("Deleting uploads...")
    deleted_count = 0
    uploads_dir = config.UPLOADS_DIR
    
    if not os.path.exists(uploads_dir):
        logger.warning(f"Uploads directory {uploads_dir} does not exist.")
        return 0
        
    for filename in os.listdir(uploads_dir):
        if filename == ".gitkeep":
            continue
            
        file_path = os.path.join(uploads_dir, filename)
        if is_path_safe_for_deletion(file_path):
            try:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                deleted_count += 1
                logger.info(f"Deleted uploaded file: {filename}")
            except Exception as e:
                logger.error(f"Failed to delete uploaded file {file_path}: {e}")
                raise e
        else:
            logger.warning(f"Skipping deletion of upload file {file_path} due to safety validator.")
            
    return deleted_count

def clear_ocr_cache_and_temps() -> int:
    """
    Clears all files in the processed directory and removes runtime temp files like *.tmp, *.temp.
    Returns the count of deleted items.
    """
    logger.info("Deleting OCR cache and temp files...")
    deleted_count = 0
    
    # 1. Clear processed directory
    processed_dir = config.PROCESSED_DIR
    if os.path.exists(processed_dir):
        for filename in os.listdir(processed_dir):
            if filename == ".gitkeep":
                continue
            file_path = os.path.join(processed_dir, filename)
            if is_path_safe_for_deletion(file_path):
                try:
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)
                    deleted_count += 1
                    logger.info(f"Deleted processed file: {filename}")
                except Exception as e:
                    logger.error(f"Failed to delete processed file {file_path}: {e}")
                    raise e
                    
    # 2. Clear temp / tmp files in backend/app/
    # We will safely search for *.tmp, *.temp inside the APP_DIR (recursively, but excluding prohibited directories)
    search_patterns = [
        os.path.join(config.APP_DIR, "**", "*.tmp"),
        os.path.join(config.APP_DIR, "**", "*.temp")
    ]
    
    for pattern in search_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            if is_path_safe_for_deletion(file_path):
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"Deleted temp file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete temp file {file_path}: {e}")
                    raise e
                    
    return deleted_count

def clear_vector_db() -> int:
    """
    Resets the Chroma Vector DB by programmatically deleting and recreating the collection.
    Avoids deleting SQLite files on disk to prevent file handle lock issues on Linux/Render.
    Returns the count of deleted vectors.
    """
    logger.info("Deleting vector database collection...")
    
    deleted_vectors = 0
    try:
        # Get count if collection exists
        if chroma_wrapper.collection:
            try:
                deleted_vectors = chroma_wrapper.collection.count()
            except Exception as count_err:
                logger.warning(f"Could not get vector count: {count_err}")
            
            logger.info(f"Deleting collection 'document_chunks' with {deleted_vectors} vectors.")
            chroma_wrapper.client.delete_collection("document_chunks")
    except Exception as e:
        logger.warning(f"Could not delete collection programmatically: {e}")

    # Recreate the collection to ensure it is immediately available
    try:
        logger.info("Re-creating ChromaDB collection...")
        chroma_wrapper.collection = chroma_wrapper.client.get_or_create_collection(
            name="document_chunks",
            metadata={"hnsw:space": "cosine"}
        )
        # Update rag_pipeline reference to ensure it points to the new collection
        rag_pipeline.collection = chroma_wrapper.collection
        logger.info("ChromaDB vector collection successfully re-created and references updated.")
    except Exception as e:
        logger.error(f"Failed to re-create ChromaDB collection: {e}")
        raise e
        
    return deleted_vectors

def clear_metadata() -> int:
    """
    Clears all metadata documents.json, folders.json, chats.json back to empty arrays [].
    Returns the count of deleted documents from metadata.
    """
    logger.info("Deleting metadata...")
    import json
    
    docs_file = os.path.join(config.DATA_DB_DIR, "documents.json")
    folders_file = os.path.join(config.DATA_DB_DIR, "folders.json")
    chats_file = os.path.join(config.DATA_DB_DIR, "chats.json")
    
    deleted_docs = 0
    
    # Read count of documents before resetting
    if os.path.exists(docs_file):
        try:
            with open(docs_file, "r", encoding="utf-8") as f:
                docs = json.load(f)
                deleted_docs = len(docs)
        except Exception:
            pass
            
    # Reset all files to empty array
    for file_path in [docs_file, folders_file, chats_file]:
        if is_path_safe_for_deletion(file_path):
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                logger.info(f"Reset metadata file to empty array: {os.path.basename(file_path)}")
            except Exception as e:
                logger.error(f"Failed to reset metadata file {file_path}: {e}")
                raise e
        else:
            logger.warning(f"Skipping metadata reset for path {file_path} due to safety constraints.")
            
    return deleted_docs

def clear_runtime_memory():
    """
    Clears runtime caches and calls garbage collection.
    """
    logger.info("Clearing runtime cache...")
    try:
        rag_pipeline._query_cache.clear()
        logger.info("RAG query cache cleared successfully.")
    except Exception as e:
        logger.warning(f"Could not clear RAG query cache: {e}")
        
    logger.info("Garbage collection...")
    gc.collect()
    logger.info("Garbage collection complete.")
