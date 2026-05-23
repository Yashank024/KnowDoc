import logging
import chromadb
from app.core import config

logger = logging.getLogger("chroma_db")

class ChromaDBWrapper:
    def __init__(self):
        logger.info(f"Initializing local persistent ChromaDB client at: {config.VECTOR_DB_DIR}")
        try:
            # Set up persistent database folder
            self.client = chromadb.PersistentClient(path=config.VECTOR_DB_DIR)
            # Fetch or bootstrap default vector collection index for document chunks
            self.collection = self.client.get_or_create_collection(
                name="document_chunks",
                metadata={"hnsw:space": "cosine"} # Use standard cosine similarity metric
            )
            logger.info("ChromaDB vector collection index initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to bootstrap ChromaDB persistent vector storage: {e}")
            raise e

    def get_collection(self):
        return self.collection

# Instantiate singleton wrapper eagerly
chroma_wrapper = ChromaDBWrapper()
