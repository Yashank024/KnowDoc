import re
import logging

logger = logging.getLogger("chunking")

def chunk_text(text: str, chunk_size: int = 900, chunk_overlap: int = 150) -> list:
    """
    Splits input text into structured overlapping chunks.
    Attempts to break chunks cleanly at sentences or line breaks.
    """
    if not text or not text.strip():
        return []

    # Clean text to remove double whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    words = text.split(" ")
    chunks = []
    
    i = 0
    while i < len(words):
        chunk_words = words[i : i + chunk_size]
        chunk_text_str = " ".join(chunk_words).strip()
        
        if chunk_text_str:
            chunks.append(chunk_text_str)
            
        if len(words) <= i + chunk_size:
            break
        i += (chunk_size - chunk_overlap)
        
    logger.info(f"Chunked document text ({len(words)} words) into {len(chunks)} overlapping chunks.")
    return chunks

def chunk_document_lines(text_lines: list, chunk_word_size: int = 900, overlap_word_size: int = 150) -> list:
    """
    Advanced layout-aware chunker that groups original PaddleOCR coordinate lines
    together while retaining page metadata.
    """
    chunks = []
    current_words = []
    current_lines_ref = []
    current_pages = set()
    
    for line in text_lines:
        txt = line.get("text", "")
        page = line.get("page", 1)
        words = txt.split(" ")
        
        current_words.extend(words)
        current_lines_ref.append(line)
        current_pages.add(page)
        
        if len(current_words) >= chunk_word_size:
            chunk_txt = " ".join([l.get("text", "") for l in current_lines_ref])
            
            # Extract combined bounding box covering the entire chunk
            chunk_box = []
            for l in current_lines_ref:
                box = l.get("box", [])
                if box:
                    chunk_box.extend(box)
            
            chunks.append({
                "text": chunk_txt,
                "pages": list(current_pages),
                "box": chunk_box
            })
            
            # Slide window back by overlap_word_size
            # Calculate how many words to keep
            words_to_keep = overlap_word_size
            
            # Walk backwards through the lines to find where to start the next chunk
            kept_words_count = 0
            kept_lines = []
            for l in reversed(current_lines_ref):
                l_words = l.get("text", "").split(" ")
                kept_words_count += len(l_words)
                kept_lines.insert(0, l)
                if kept_words_count >= words_to_keep:
                    break
            
            current_lines_ref = kept_lines
            current_words = []
            for l in current_lines_ref:
                current_words.extend(l.get("text", "").split(" "))
            
            current_pages = set([l.get("page", 1) for l in current_lines_ref])
            
    # Add remaining text lines as a final chunk
    if current_lines_ref:
        chunk_txt = " ".join([l.get("text", "") for l in current_lines_ref])
        chunk_box = []
        for l in current_lines_ref:
            box = l.get("box", [])
            if box:
                chunk_box.extend(box)
        chunks.append({
            "text": chunk_txt,
            "pages": list(current_pages),
            "box": chunk_box
        })
        
    logger.info(f"Chunked Visual OCR lines into {len(chunks)} layout-aware chunks.")
    return chunks