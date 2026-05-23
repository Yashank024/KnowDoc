import os
import sys

# Ensure the backend directory is in the Python search path on boot
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.health import router as health_router
from app.api.routes.upload import router as upload_router
from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.folders import router as folders_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")

app = FastAPI(
    title="KnowDoc AI RAG Stack",
    description="Immersive AI workspace engine combining Google Gemini 2.5 Flash and PaddleOCR inside a clean RAG stack.",
    version="3.0.0"
)

# Enable CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(health_router)
app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(folders_router)

@app.get("/")
async def root():
    """
    Default diagnostic ping endpoint.
    """
    return {
        "status": "KnowDoc backend running"
    }

if __name__ == "__main__":
    import uvicorn
    # Execute backend locally on port 8000 when main.py is run directly
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
