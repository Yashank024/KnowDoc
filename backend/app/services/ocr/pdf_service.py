import os
import logging
import fitz # PyMuPDF
from app.services.ocr.paddle_service import paddle_service

logger = logging.getLogger("pdf_service")

class PDFService:
    def extract_pdf_ocr(self, pdf_path: str, temp_dir: str = None) -> dict:
        """
        Renders each page of a PDF as a temporary image, runs PaddleOCR,
        and accumulates text lines with page numbers mapped.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found at: {pdf_path}")

        if not temp_dir:
            temp_dir = os.path.dirname(pdf_path)

        logger.info(f"Opening PDF for OCR processing: {pdf_path}")
        text_lines = []
        full_text_list = []

        try:
            doc = fitz.open(pdf_path)
            total_pages = doc.page_count
            logger.info(f"PDF opened successfully. Total pages: {total_pages}")

            # Check if there is selectable text in the document
            is_searchable = False
            for page_idx in range(min(total_pages, 5)):
                page = doc.load_page(page_idx)
                if page.get_text("text").strip():
                    is_searchable = True
                    break

            if is_searchable:
                logger.info("PDF has selectable text. Bypassing slow PaddleOCR and performing direct PyMuPDF text block extraction...")
                for page_idx in range(total_pages):
                    page_num = page_idx + 1
                    page = doc.load_page(page_idx)
                    page_width = page.rect.width
                    page_height = page.rect.height
                    
                    page_text_blocks = []
                    page_dict = page.get_text("dict")
                    for block in page_dict.get("blocks", []):
                        if block.get("type") == 0:  # Text block
                            for line in block.get("lines", []):
                                line_text = "".join([span.get("text", "") for span in line.get("spans", [])]).strip()
                                if line_text:
                                    x0, y0, x1, y1 = line.get("bbox", (0, 0, 0, 0))
                                    # Scale coordinates to standard 1000x1000 grid
                                    x0_s = int((x0 / page_width) * 1000)
                                    y0_s = int((y0 / page_height) * 1000)
                                    x1_s = int((x1 / page_width) * 1000)
                                    y1_s = int((y1 / page_height) * 1000)
                                    
                                    box = [
                                        [x0_s, y0_s],
                                        [x1_s, y0_s],
                                        [x1_s, y1_s],
                                        [x0_s, y1_s]
                                    ]
                                    page_text_blocks.append(line_text)
                                    text_lines.append({
                                        "text": line_text,
                                        "confidence": 1.0,
                                        "box": box,
                                        "page": page_num
                                    })
                    full_text_list.append("\n".join(page_text_blocks))
            else:
                logger.info("PDF has no selectable text. Falling back to multi-page image rendering + PaddleOCR engine...")
                for page_idx in range(total_pages):
                    page_num = page_idx + 1
                    logger.info(f"Processing PDF page {page_num}/{total_pages}...")
                    page = doc.load_page(page_idx)
                    
                    # Render page at standard high-resolution (150 DPI)
                    pix = page.get_pixmap(dpi=150)
                    temp_page_img = os.path.join(temp_dir, f"temp_page_{page_num}_{os.path.basename(pdf_path)}.png")
                    
                    pix.save(temp_page_img)
                    
                    try:
                        # Run PaddleOCR on the page image
                        page_result = paddle_service.extract_text(temp_page_img)
                        
                        if page_result.get("status") == "success":
                            # Map page metadata to each block
                            for line in page_result.get("text_lines", []):
                                line["page"] = page_num
                                text_lines.append(line)
                                
                            full_text_list.append(page_result.get("full_text", ""))
                        else:
                            logger.error(f"Failed to OCR page {page_num}: {page_result.get('message')}")
                            
                    finally:
                        # Cleanup temporary image file to free up space
                        if os.path.exists(temp_page_img):
                            try:
                                os.remove(temp_page_img)
                            except Exception as e:
                                logger.warning(f"Could not remove temp page image {temp_page_img}: {e}")

            full_text = "\n".join(full_text_list)
            
            return {
                "status": "success",
                "filename": os.path.basename(pdf_path),
                "text_lines": text_lines,
                "full_text": full_text,
                "total_pages": total_pages
            }
            
        except Exception as e:
            logger.error(f"Error during PDF multi-page OCR execution: {e}", exc_info=True)
            return {
                "status": "error",
                "filename": os.path.basename(pdf_path),
                "message": str(e)
            }

pdf_service = PDFService()
