import re

def clean_whitespaces(text: str) -> str:
    """
    Cleans multiple consecutive spaces or linebreaks into single linebreaks.
    """
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()
