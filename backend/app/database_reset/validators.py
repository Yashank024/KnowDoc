import os
import logging
from app.core import config

logger = logging.getLogger("database_reset.validators")

# Core files and directories that must NEVER be deleted
FORBIDDEN_KEYWORDS = [
    ".git",
    "venv",
    "node_modules",
    "__pycache__",
    ".env",
    "requirements.txt",
    "Dockerfile",
    "README",
    "package.json",
    "next.config",
    "tailwind.config"
]

def is_path_safe_for_deletion(target_path: str) -> bool:
    """
    Validates if a target path is safe for database reset deletion.
    Ensures the path is inside either the uploads directory, processed directory,
    vector_db directory, or is one of the metadata files, and does not contain any forbidden keywords.
    """
    if not target_path:
        return False

    abs_target = os.path.abspath(target_path)
    
    # Resolve valid reset paths
    allowed_dirs = [
        os.path.abspath(config.UPLOADS_DIR),
        os.path.abspath(config.VECTOR_DB_DIR),
        os.path.abspath(config.DATA_DB_DIR),
        os.path.abspath(config.PROCESSED_DIR)
    ]
    
    # Check if target is inside (or is) one of the allowed directories
    is_in_allowed = False
    for allowed in allowed_dirs:
        if abs_target.startswith(allowed):
            is_in_allowed = True
            break
            
    if not is_in_allowed:
        logger.warning(f"Path safety violation: target path '{abs_target}' is outside allowed reset directories.")
        return False

    # Check for forbidden keywords in path segments
    path_parts = abs_target.replace("\\", "/").split("/")
    for part in path_parts:
        if part in FORBIDDEN_KEYWORDS:
            logger.warning(f"Path safety violation: segment '{part}' of '{abs_target}' is forbidden.")
            return False
            
    # Check that we are not deleting application code folders
    app_dir = os.path.abspath(config.APP_DIR)
    backend_root = os.path.dirname(app_dir)
    project_root = os.path.dirname(backend_root)
    
    if abs_target == app_dir or abs_target == backend_root or abs_target == project_root:
        logger.warning(f"Path safety violation: attempting to delete application root directory '{abs_target}'.")
        return False
        
    # Additional guard: Check if path ends in .py or .js or .json (excluding allowed DB json files)
    basename = os.path.basename(abs_target)
    if basename.endswith((".py", ".js", ".html", ".css", ".jsx")):
        logger.warning(f"Path safety violation: attempting to delete source code file '{abs_target}'.")
        return False
        
    return True
