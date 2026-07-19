import logging
import requests
from app.core import config

logger = logging.getLogger("embeddings_service")

class EmbeddingsService:
    def __init__(self):
        self.api_key = config.JINA_API_KEY
        self.model = "jina-embeddings-v4"
        self.endpoint = "https://api.jina.ai/v1/embeddings"

    def get_embedding(self, text: str) -> list:
        """
        Generates a 1D vector representation for the given text snippet.
        """
        if not text.strip():
            return []

        embeddings = self.get_embeddings([text])
        return embeddings[0] if embeddings else []

    def get_embeddings(self, texts: list) -> list:
        """
        Generates 1D vector representations for a list of text chunks.
        """
        if not texts:
            return []

        api_key = config.JINA_API_KEY or self.api_key
        if not api_key:
            logger.error("JINA_API_KEY is not configured.")
            raise ValueError("JINA_API_KEY is not configured.")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": self.model,
            "input": texts,
            "embedding_type": "float"
        }

        logger.info(f"Requesting embeddings from Jina API for {len(texts)} chunks...")
        try:
            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=30)
            if response.status_code != 200:
                logger.error(f"Jina API returned error {response.status_code}: {response.text}")
                raise RuntimeError(f"Jina API error: {response.text}")

            res_json = response.json()
            data_list = res_json.get("data", [])
            
            # Sort by index to maintain original order
            sorted_data = sorted(data_list, key=lambda x: x.get("index", 0))
            embeddings = [item["embedding"] for item in sorted_data]
            
            logger.info(f"Successfully retrieved {len(embeddings)} embeddings from Jina API.")
            return embeddings
        except Exception as e:
            logger.error(f"Error computing Jina embeddings: {e}")
            raise e

embeddings_service = EmbeddingsService()
