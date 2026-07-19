import os
import sys
from dotenv import load_dotenv

# Ensure the backend directory is in Python's search path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Locate and load the environment variables from the backend/.env file
env_path = os.path.join(backend_dir, ".env")
load_dotenv(env_path)

# Unified configurations
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "tencent/hy3:free")
PADDLEOCR_API_KEY = os.getenv("PADDLEOCR_API_KEY")
JINA_API_KEY = os.getenv("JINA_API_KEY")

# Application base folder (backend/app/)
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Modular directory paths
UPLOADS_DIR = os.path.abspath(os.path.join(APP_DIR, "uploads"))
VECTOR_DB_DIR = os.path.abspath(os.path.join(APP_DIR, "vector_db"))
DATA_DB_DIR = os.path.abspath(os.path.join(APP_DIR, "db", "data"))
PROCESSED_DIR = os.path.abspath(os.path.join(DATA_DB_DIR, "processed"))

# Dynamic scaffolding of directories on startup
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)
os.makedirs(DATA_DB_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
