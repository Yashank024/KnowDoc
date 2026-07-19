import logging
from typing import Dict, Any

from app.database_reset import cleanup

logger = logging.getLogger("database_reset.service")

def execute_database_reset() -> Dict[str, Any]:
    """
    Orchestrates the entire database reset process stage-by-stage.
    Captures stage successes, logs them clearly, and handles detailed error reporting.
    """
    logger.info("========== DATABASE RESET START ==========")
    
    stages = {
        "Uploads": ("Deleting uploads...", cleanup.clear_uploads),
        "OCR Cache": ("Deleting OCR cache...", cleanup.clear_ocr_cache_and_temps),
        "Vector Database": ("Deleting vector database...", cleanup.clear_vector_db),
        "Metadata": ("Deleting metadata...", cleanup.clear_metadata),
        "Runtime Cache": ("Clearing runtime cache...", cleanup.clear_runtime_memory)
    }
    
    results = {}
    
    try:
        # 1. Uploads
        logger.info(stages["Uploads"][0])
        results["deleted_uploaded_files"] = stages["Uploads"][1]()
        logger.info("SUCCESS")
        
        # 2. OCR Cache
        logger.info(stages["OCR Cache"][0])
        results["cache_cleared"] = True
        stages["OCR Cache"][1]()
        logger.info("SUCCESS")
        
        # 3. Vector Database
        logger.info(stages["Vector Database"][0])
        results["deleted_vectors"] = stages["Vector Database"][1]()
        logger.info("SUCCESS")
        
        # 4. Metadata
        logger.info(stages["Metadata"][0])
        results["deleted_documents"] = stages["Metadata"][1]()
        logger.info("SUCCESS")
        
        # 5. Runtime Cache & Garbage Collection
        logger.info(stages["Runtime Cache"][0])
        stages["Runtime Cache"][1]()
        logger.info("SUCCESS")
        
        logger.info("========== DATABASE RESET COMPLETE ==========")
        
        return {
            "success": True,
            "deleted_documents": results["deleted_documents"],
            "deleted_vectors": results["deleted_vectors"],
            "deleted_uploaded_files": results["deleted_uploaded_files"],
            "cache_cleared": results["cache_cleared"],
            "message": "Database successfully reset."
        }
        
    except Exception as e:
        # Determine which stage failed based on what results were populated
        failed_stage = "Unknown"
        if "deleted_uploaded_files" not in results:
            failed_stage = "Uploads"
        elif "cache_cleared" not in results:
            failed_stage = "OCR Cache"
        elif "deleted_vectors" not in results:
            failed_stage = "Vector Database"
        elif "deleted_documents" not in results:
            failed_stage = "Metadata"
        else:
            failed_stage = "Runtime Cache"
            
        logger.error(f"DATABASE RESET FAILED at stage '{failed_stage}': {e}", exc_info=True)
        logger.info("========== DATABASE RESET FAILED ==========")
        
        return {
            "success": False,
            "stage": failed_stage,
            "error": str(e)
        }
