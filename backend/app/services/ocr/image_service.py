import logging
from PIL import Image
from app.services.ocr.paddle_service import paddle_service

logger = logging.getLogger("image_service")

class ImageService:
    def extract_image_ocr(self, image_path: str) -> dict:
        """
        Processes image layout, asserts sizing, and extracts coordinates.
        """
        logger.info(f"Loading image for OCR diagnostics: {image_path}")
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                logger.info(f"Image loaded. Sizing: {width}x{height} pixels.")
            
            # Directly forward to core paddle_service for extraction
            return paddle_service.extract_text(image_path)
        except Exception as e:
            logger.error(f"Image pre-processing failed: {e}")
            return {"status": "error", "message": str(e)}

image_service = ImageService()
