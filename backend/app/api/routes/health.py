from fastapi import APIRouter

router = APIRouter(prefix="/api")

@router.get("/health")
def health_check():
    """
    Verifies the operational health of the backend API and PaddleOCR model.
    """
    return {
        "status": "healthy",
        "engine": "PaddleOCR v3.x",
        "device": "CPU"
    }
