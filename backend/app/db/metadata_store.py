import os
import json
import threading
import logging
from app.core import config

logger = logging.getLogger("metadata_store")

class MetadataStore:
    _lock = threading.Lock()

    def __init__(self):
        # Local JSON paths mapping
        self.docs_file = os.path.join(config.DATA_DB_DIR, "documents.json")
        self.folders_file = os.path.join(config.DATA_DB_DIR, "folders.json")
        
        # Initialize default files if missing
        self._init_file(self.docs_file, [])
        self._init_file(self.folders_file, [])

    def _init_file(self, file_path: str, default_val):
        if not os.path.exists(file_path):
            with self._lock:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(default_val, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    logger.error(f"Error initializing local DB file {file_path}: {e}")

    def _read_json(self, file_path: str):
        with self._lock:
            try:
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        return json.load(f)
            except Exception as e:
                logger.error(f"Error reading JSON from {file_path}: {e}")
            return []

    def _write_json(self, file_path: str, data):
        with self._lock:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                logger.error(f"Error writing JSON to {file_path}: {e}")
                return False

    # ── Document Methods ──
    def get_documents(self):
        return self._read_json(self.docs_file)

    def get_document_by_id(self, doc_id: str):
        docs = self.get_documents()
        for doc in docs:
            if doc.get("id") == doc_id:
                return doc
        return None

    def get_document_by_hash(self, file_hash: str):
        docs = self.get_documents()
        for doc in docs:
            if doc.get("hash") == file_hash:
                return doc
        return None

    def add_document(self, doc_data: dict):
        docs = self.get_documents()
        docs.insert(0, doc_data) # Add to the front of list (recent first)
        self._write_json(self.docs_file, docs)
        return doc_data

    def update_document_status(self, doc_id: str, status: str):
        docs = self.get_documents()
        for doc in docs:
            if doc.get("id") == doc_id:
                doc["status"] = status
                break
        self._write_json(self.docs_file, docs)
        return True

    def update_document_details(self, doc_id: str, size: str = None, tags: list = None, text_lines: list = None, full_text: str = None):
        docs = self.get_documents()
        for doc in docs:
            if doc.get("id") == doc_id:
                if size is not None:
                    doc["size"] = size
                if tags is not None:
                    doc["tags"] = tags
                if text_lines is not None:
                    doc["text_lines"] = text_lines
                if full_text is not None:
                    doc["full_text"] = full_text
                break
        self._write_json(self.docs_file, docs)
        return True

    def delete_document(self, doc_id: str):
        docs = self.get_documents()
        updated_docs = [d for d in docs if d.get("id") != doc_id]
        self._write_json(self.docs_file, updated_docs)
        return True

    # ── Folder Methods ──
    def get_folders(self):
        return self._read_json(self.folders_file)

    def get_folder_by_id(self, folder_id: str):
        folders = self.get_folders()
        for folder in folders:
            if folder.get("id") == folder_id:
                return folder
        return None

    def add_folder(self, folder_data: dict):
        folders = self.get_folders()
        folders.append(folder_data)
        self._write_json(self.folders_file, folders)
        return folder_data

    def add_doc_to_folder(self, folder_id: str, doc_id: str):
        folders = self.get_folders()
        for folder in folders:
            if folder.get("id") == folder_id:
                doc_ids = folder.setdefault("document_ids", [])
                if doc_id not in doc_ids:
                    doc_ids.append(doc_id)
                break
        self._write_json(self.folders_file, folders)
        return True

metadata_store = MetadataStore()
