from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from app.database_reset.reset_service import execute_database_reset

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/reset-database", response_model=Dict[str, Any])
async def reset_database():
    """
    Endpoint to trigger a complete application database and cache reset.
    Returns details about deleted files and vectors, or structured errors if a stage fails.
    """
    res = execute_database_reset()
    
    if not res.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "stage": res.get("stage"),
                "error": res.get("error")
            }
        )
        
    return res
