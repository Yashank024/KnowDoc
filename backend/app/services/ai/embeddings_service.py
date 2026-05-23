import logging
import google.generativeai as genai
from app.core import config

logger = logging.getLogger("embeddings_service")

# Lightweight local SentenceTransformer configuration (120MB download, extremely fast CPU vector computation)
LOCAL_MODEL_NAME = "all-MiniLM-L6-v2"

class EmbeddingsService:
    def __init__(self):
        self.local_model = None
        self._initialized = False

    def _get_local_model(self):
        if not self._initialized:
            self._initialized = True
            logger.info("Initializing EmbeddingsService (lazy-loading on demand)...")
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading local SentenceTransformer model '{LOCAL_MODEL_NAME}'...")
                self.local_model = SentenceTransformer(LOCAL_MODEL_NAME)
                logger.info("Local SentenceTransformer model loaded successfully.")
            except Exception as e:
                logger.warning(f"Could not load local sentence-transformers model: {e}. Falling back to Google Embeddings API.")
        return self.local_model

    def get_embedding(self, text: str) -> list:
        """
        Generates a 1D vector representation for the given text snippet.
        """
        if not text.strip():
            return []

        # Try computing locally first
        local_model = self._get_local_model()
        if local_model:
            try:
                embedding = local_model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            except Exception as e:
                logger.error(f"Error computing embedding locally: {e}. Attempting fallback...")

        # Fallback: Call Google Generative AI embeddings model
        try:
            logger.info("Calling Google Generative AI text-embedding-004 API...")
            response = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_query"
            )
            return response["embedding"]
        except Exception as e:
            logger.error(f"Error calling Google Generative AI embedding endpoint: {e}", exc_info=True)
            raise e

    def get_embeddings(self, texts: list) -> list:
        """
        Generates 1D vector representations for a list of text chunks.
        """
        if not texts:
            return []

        # Try computing locally first
        local_model = self._get_local_model()
        if local_model:
            try:
                embeddings = local_model.encode(texts, convert_to_numpy=True)
                return embeddings.tolist()
            except Exception as e:
                logger.error(f"Error computing bulk embeddings locally: {e}. Attempting fallback...")

        # Fallback: Page-by-page calling of Google Embeddings API
        try:
            logger.info("Calling Google Generative AI bulk text-embedding-004 API...")
            response = genai.embed_content(
                model="models/text-embedding-004",
                content=texts,
                task_type="retrieval_document"
            )
            return response["embedding"]
        except Exception as e:
            logger.error(f"Error calling Google bulk embedding endpoint: {e}", exc_info=True)
            raise e

# Initialize singleton EmbeddingsService (lazy loader is ready, but no models are loaded yet)
embeddings_service = EmbeddingsService()
