import os
import logging
import requests
import json
from app.core import config

logger = logging.getLogger("openrouter_service")

class OpenRouterService:
    _instance = None
    api_key = None
    model_name = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(OpenRouterService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def _init_client(self):
        if self.api_key is None:
            logger.info("Initializing OpenRouter Service client (lazy-loading configuration)...")
            self.api_key = config.OPENROUTER_API_KEY
            self.model_name = config.OPENROUTER_MODEL
            
            if not self.api_key:
                logger.error("OpenRouter API key is not configured in environment variables (.env).")
            else:
                logger.info(f"OpenRouter configured with model: {self.model_name}")

    def generate_response(self, prompt: str, system_instruction: str = None) -> str:
        """
        Executes a prompt completion using OpenRouter completions API.
        """
        if not prompt.strip():
            return "Please provide a valid query."

        self._init_client()

        if not self.api_key:
            return "Cannot connect to the API."

        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://knowdoc.ai",
                "X-Title": "KnowDoc AI"
            }

            # Build messages array
            messages = []
            if system_instruction:
                messages.append({
                    "role": "system",
                    "content": system_instruction
                })
            messages.append({
                "role": "user",
                "content": prompt
            })

            # Retrieve max tokens from environment, defaulting to 2048 to prevent budget over-allocation errors
            max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "2048"))

            data = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": max_tokens
            }

            logger.info(f"Sending request to OpenRouter ({self.model_name}) with max_tokens={max_tokens}...")
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=60)
            
            if response.status_code != 200:
                logger.error(f"OpenRouter API returned error status {response.status_code}: {response.text}")
                return "Cannot connect to the API."

            res_payload = response.json()
            choices = res_payload.get("choices", [])
            if not choices:
                logger.error(f"OpenRouter returned empty choices: {res_payload}")
                return "Cannot connect to the API."

            message_content = choices[0].get("message", {}).get("content", "")
            return message_content

        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}", exc_info=True)
            return "Cannot connect to the API."

# Initialize singleton openrouter_service (no configuration happens yet)
openrouter_service = OpenRouterService()
