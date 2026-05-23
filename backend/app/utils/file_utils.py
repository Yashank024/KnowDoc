import os

def get_file_extension(filename: str) -> str:
    """
    Returns the lowercased extension of a filename including the dot (e.g. '.pdf').
    """
    _, ext = os.path.splitext(filename.lower())
    return ext

def clean_filename(filename: str) -> str:
    """
    Sanitizes filenames to prevent path traversal issues.
    """
    return os.path.basename(filename).replace(" ", "_")
