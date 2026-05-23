import logging
from app.db.metadata_store import metadata_store

logger = logging.getLogger("folder_service")

class FolderService:
    def list_folders(self):
        return metadata_store.get_folders()

    def add_folder(self, name: str, description: str = ""):
        logger.info(f"Adding new category folder via service: {name}")
        import uuid
        folder_id = f"folder_{uuid.uuid4().hex[:8]}"
        folder_data = {
            "id": folder_id,
            "name": name,
            "description": description,
            "document_ids": []
        }
        return metadata_store.add_folder(folder_data)

folder_service = FolderService()
