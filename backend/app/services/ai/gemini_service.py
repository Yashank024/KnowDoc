import logging
import google.generativeai as genai
from app.core import config

logger = logging.getLogger("gemini_service")

class GeminiService:
    _instance = None
    model = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GeminiService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def _get_model(self):
        if self.model is None:
            logger.info("Initializing Google Gemini Generative Model client (lazy-loading on demand)...")
            try:
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel("gemini-2.5-flash")
                logger.info("Gemini Model client configured successfully.")
            except Exception as e:
                logger.error(f"Failed to configure Gemini Generative API: {e}")
                raise e
        return self.model

    def generate_response(self, prompt: str, system_instruction: str = None) -> str:
        """
        Executes a prompt completion using gemini-2.5-flash model.
        """
        if not prompt.strip():
            return "Please provide a valid query."

        try:
            # Lazy-load model
            model = self._get_model()
            
            # Set up instructions or constraints if provided
            if system_instruction:
                model_with_instruction = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    system_instruction=system_instruction
                )
                response = model_with_instruction.generate_content(prompt)
            else:
                response = model.generate_content(prompt)
                
            return response.text
        except Exception as e:
            logger.error(f"Error calling Google Generative AI API: {e}", exc_info=True)
            return f"Error: Failed to process request via Gemini model. {str(e)}"

# Initialize singleton gemini_service (no client configure or model load happens yet)
gemini_service = GeminiService()
