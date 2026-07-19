import os
import sys

# Ensure the backend directory is in the Python search path on boot
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import logging
import time
from collections import defaultdict
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
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

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.request_history = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Only rate limit API endpoints, exempting CORS preflight OPTIONS requests
        if request.url.path.startswith("/api") and request.method != "OPTIONS":
            self.request_history[client_ip] = [
                t for t in self.request_history[client_ip] if current_time - t < 60
            ]
            
            if len(self.request_history[client_ip]) >= self.calls_per_minute:
                return Response(
                    content="Rate limit exceeded. Please try again in a minute.",
                    status_code=429
                )
                
            self.request_history[client_ip].append(current_time)
            
        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "connect-src 'self' *; "
            "font-src 'self' data:; "
            "frame-ancestors 'none'"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

app = FastAPI(
    title="KnowDoc AI RAG Stack",
    description="Immersive AI workspace engine combining OpenRouter LLM completions and PaddleOCR inside a clean RAG stack.",
    version="3.0.0"
)

# Add custom security and throttling middlewares first (innermost)
app.add_middleware(RateLimiterMiddleware, calls_per_minute=60)
app.add_middleware(SecurityHeadersMiddleware)

# Enable secure CORS middleware LAST (outermost) to ensure it wraps all responses
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+|[a-zA-Z0-9-]+\.vercel\.app)(:\d+)?",
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
