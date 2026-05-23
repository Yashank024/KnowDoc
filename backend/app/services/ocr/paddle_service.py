import os
import logging

# Disable MKLDNN before importing paddle to avoid Windows CPU crashes
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT'] = '0'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("paddle_service")

try:
    from paddleocr import PaddleOCR
except ImportError as e:
    logger.error(f"Failed to import paddleocr: {e}")
    raise e

class PaddleService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            logger.info("Initializing PaddleOCR engine (this might take a moment)...")
            cls._instance = super(PaddleService, cls).__new__(cls, *args, **kwargs)
            try:
                # Initialize PaddleOCR engine with Windows-safe configurations
                cls._instance.ocr_engine = PaddleOCR(
                    use_angle_cls=True,
                    lang='en',
                    enable_mkldnn=False
                )
                logger.info("PaddleOCR engine initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize PaddleOCR engine: {e}")
                raise e
        return cls._instance

    def extract_text(self, file_path: str) -> dict:
        """
        Processes the image document at file_path and extracts text lines,
        confidence scores, and bounding boxes.
        Returns a structured dictionary of the results.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at: {file_path}")

        logger.info(f"Running OCR on file: {file_path}")
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                img_w, img_h = img.size
            logger.info(f"Loaded image dimensions for OCR scaling: {img_w}x{img_h}")
            
            # Run inference
            raw_results = self.ocr_engine.ocr(file_path)
            
            # Format output response
            text_lines = []
            full_text_list = []
            
            # Ensure raw_results is iterable
            if raw_results:
                for page_res in raw_results:
                    if isinstance(page_res, dict):
                        rec_texts = page_res.get('rec_texts', [])
                        rec_scores = page_res.get('rec_scores', [])
                        rec_polys = page_res.get('rec_polys', [])
                        
                        for text, score, poly in zip(rec_texts, rec_scores, rec_polys):
                            box_coords = []
                            if poly is not None:
                                try:
                                    box_coords = [[int((pt[0] / img_w) * 1000), int((pt[1] / img_h) * 1000)] for pt in poly]
                                except Exception:
                                    box_coords = [[int((pt[0] / img_w) * 1000), int((pt[1] / img_h) * 1000)] for pt in poly]
                            
                            text_lines.append({
                                "text": str(text),
                                "confidence": float(score),
                                "box": box_coords
                            })
                            full_text_list.append(str(text))
                    
                    elif isinstance(page_res, list):
                        for line in page_res:
                            if isinstance(line, list) and len(line) == 2:
                                poly = line[0]
                                text, score = line[1]
                                box_coords = [[int((pt[0] / img_w) * 1000), int((pt[1] / img_h) * 1000)] for pt in poly]
                                
                                text_lines.append({
                                    "text": str(text),
                                    "confidence": float(score),
                                    "box": box_coords
                                })
                                full_text_list.append(str(text))

            full_text = "\n".join(full_text_list)
            
            return {
                "status": "success",
                "filename": os.path.basename(file_path),
                "text_lines": text_lines,
                "full_text": full_text
            }
            
        except Exception as e:
            logger.error(f"Error during OCR processing: {e}", exc_info=True)
            return {
                "status": "error",
                "filename": os.path.basename(file_path),
                "message": str(e)
            }

# Initialize singleton instance eagerly
paddle_service = PaddleService()
