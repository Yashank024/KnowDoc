import os
from app.core import constants

def is_allowed_file(filename: str) -> bool:
    """
    Asserts if an uploaded filename extension is accepted in global constants.
    """
    _, ext = os.path.splitext(filename.lower())
    return ext in constants.ALLOWED_EXTENSIONS
