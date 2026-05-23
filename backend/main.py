import os
import sys

# Ensure the backend folder is in Python's search path for resolving 'app' imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import uvicorn
from app.main import app

if __name__ == "__main__":
    # Execute backend locally on port 8000 when main.py is run directly
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
