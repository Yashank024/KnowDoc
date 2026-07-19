"""
PDF Text Extraction Service — Clean Rebuild.

Two-path router:
  1. PyMuPDF  → if the PDF has selectable text (text_lines > 0), use it.
  2. PaddleOCR Cloud → for scanned / image PDFs with no selectable text.

Returns a list of text_line dicts compatible with the ingestion pipeline.
No bounding boxes, no coordinate scaling, no fallback chains.
"""

import os
import logging
import fitz  # PyMuPDF

from app.services.ocr import paddle_service as paddle

logger = logging.getLogger("pdf_service")


def extract(pdf_path: str) -> dict:
    """
    Extract text from a PDF.

    Returns:
        {
            "success": bool,
            "error": str,          # only on failure
            "text_lines": [str],
            "full_text": str,
            "source": "pymupdf" | "paddleocr",
        }
    """
    if not os.path.exists(pdf_path):
        return {"success": False, "error": f"PDF not found: {pdf_path}"}

    # ── Path A: PyMuPDF selectable text ───────────────────────────────────────
    logger.info(f"[PDFService] Attempting PyMuPDF extraction: {os.path.basename(pdf_path)}")
    try:
        doc = fitz.open(pdf_path)
        text_lines = []

        for page_idx in range(doc.page_count):
            page = doc.load_page(page_idx)
            rect = page.rect
            W_page = rect.width if rect.width > 0 else 1000
            H_page = rect.height if rect.height > 0 else 1000
            # get_text("blocks") gives one entry per text block
            for block in page.get_text("blocks"):
                # block: (x0, y0, x1, y1, text, block_no, block_type)
                if block[6] != 0:  # skip image blocks
                    continue
                block_text = block[4].strip()
                if block_text:
                    x0_s = (block[0] / W_page) * 1000
                    y0_s = (block[1] / H_page) * 1000
                    x1_s = (block[2] / W_page) * 1000
                    y1_s = (block[3] / H_page) * 1000
                    box = [[x0_s, y0_s], [x1_s, y0_s], [x1_s, y1_s], [x0_s, y1_s]]
                    text_lines.append({
                        "text": block_text,
                        "box": box,
                        "confidence": 1.0,
                        "page": page_idx + 1
                    })

        logger.info(f"[PDFService] PyMuPDF extracted {len(text_lines)} text blocks.")

        if text_lines:
            full_text = "\n".join([line["text"] for line in text_lines])
            return {
                "success": True,
                "text_lines": text_lines,
                "full_text": full_text,
                "source": "pymupdf",
            }
    except Exception as e:
        logger.warning(f"[PDFService] PyMuPDF extraction failed: {e}. Falling back to PaddleOCR.")

    # ── Path B: PaddleOCR Cloud API ────────────────────────────────────────────
    logger.info(f"[PDFService] PyMuPDF returned 0 lines. Submitting to PaddleOCR Cloud API...")
    result = paddle.run(pdf_path)

    if not result.success:
        return {"success": False, "error": result.error}

    if not result.text_lines:
        return {
            "success": False,
            "error": (
                f"PaddleOCR returned 0 text lines. "
                f"Raw markdown length: {len(result.markdown)} chars. "
                f"Pages processed: {result.page_count}. "
                "Check Render logs for full raw JSONL response."
            )
        }

    return {
        "success": True,
        "text_lines": result.text_lines,
        "full_text": result.markdown,
        "source": "paddleocr",
    }
