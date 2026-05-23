import re
import logging

logger = logging.getLogger("chunking")

def chunk_text(text: str, chunk_size: int = 600, chunk_overlap: int = 120) -> list:
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
        # Take a slice of words
        chunk_words = words[i : i + chunk_size]
        chunk_text = " ".join(chunk_words).strip()
        
        if chunk_text:
            chunks.append(chunk_text)
            
        # Move forward by sliding window width (size minus overlap)
        if len(words) <= i + chunk_size:
            break
        i += (chunk_size - chunk_overlap)
        
    logger.info(f"Chunked document text ({len(words)} words) into {len(chunks)} overlapping chunks.")
    return chunks

def chunk_document_lines(text_lines: list, chunk_word_size: int = 120, overlap_word_size: int = 30) -> list:
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
            chunks.append({
                "text": chunk_txt,
                "pages": list(current_pages),
                "box": current_lines_ref[0].get("box", []) # Retain start boundary box coordinates
            })
            
            # Keep overlap words & lines
            overlap_count = min(len(current_lines_ref), 2)
            current_lines_ref = current_lines_ref[-overlap_count:]
            current_words = []
            for l in current_lines_ref:
                current_words.extend(l.get("text", "").split(" "))
            current_pages = {l.get("page", 1) for l in current_lines_ref}
            
    # Clean up trailing lines
    if current_lines_ref:
        chunk_txt = " ".join([l.get("text", "") for l in current_lines_ref])
        chunks.append({
            "text": chunk_txt,
            "pages": list(current_pages),
            "box": current_lines_ref[0].get("box", [])
        })
        
    return chunks
