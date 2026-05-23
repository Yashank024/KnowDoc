import os
import shutil
import logging
from app.core import config

logger = logging.getLogger("file_service")

class FileService:
    def __init__(self):
        self.upload_dir = config.UPLOADS_DIR

    def save_file(self, file_content, filename: str) -> str:
        """
        Saves raw binary file content locally and returns its absolute path.
        """
        target_path = os.path.join(self.upload_dir, filename)
        logger.info(f"Saving binary file to disk: {target_path}")
        
        try:
            with open(target_path, "wb") as buffer:
                buffer.write(file_content)
            return target_path
        except Exception as e:
            logger.error(f"Failed to write file to local disk {filename}: {e}")
            raise e

    def delete_file(self, filename: str) -> bool:
        """
        Deletes a local file from uploads.
        """
        target_path = os.path.join(self.upload_dir, filename)
        if os.path.exists(target_path):
            try:
                os.remove(target_path)
                logger.info(f"Deleted local file from disk: {target_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete local file {filename}: {e}")
                return False
        return False

file_service = FileService()
