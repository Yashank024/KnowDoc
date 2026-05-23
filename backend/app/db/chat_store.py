import os
import json
import threading
import logging
from app.core import config

logger = logging.getLogger("chat_store")

class ChatStore:
    _lock = threading.Lock()

    def __init__(self):
        self.chats_file = os.path.join(config.DATA_DB_DIR, "chats.json")
        self._init_file(self.chats_file, [])

    def _init_file(self, file_path: str, default_val):
        if not os.path.exists(file_path):
            with self._lock:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(default_val, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    logger.error(f"Error initializing local chats DB file {file_path}: {e}")

    def _read_json(self):
        with self._lock:
            try:
                if os.path.exists(self.chats_file):
                    with open(self.chats_file, "r", encoding="utf-8") as f:
                        return json.load(f)
            except Exception as e:
                logger.error(f"Error reading chats JSON from {self.chats_file}: {e}")
            return []

    def _write_json(self, data):
        with self._lock:
            try:
                with open(self.chats_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                logger.error(f"Error writing chats JSON to {self.chats_file}: {e}")
                return False

    def get_chats(self):
        return self._read_json()

    def get_chat_by_id(self, chat_id: str):
        chats = self.get_chats()
        for chat in chats:
            if chat.get("id") == chat_id:
                return chat
        return None

    def get_chats_by_session(self, session_id: str):
        chats = self.get_chats()
        return [chat for chat in chats if chat.get("session_id") == session_id]

    def add_chat(self, chat_data: dict):
        chats = self.get_chats()
        chats.insert(0, chat_data) # Recent first
        self._write_json(chats)
        return chat_data

    def update_chat_messages(self, chat_id: str, messages: list):
        chats = self.get_chats()
        for chat in chats:
            if chat.get("id") == chat_id:
                chat["messages"] = messages
                break
        self._write_json(chats)
        return True

    def delete_chat(self, chat_id: str):
        chats = self.get_chats()
        updated_chats = [c for c in chats if c.get("id") != chat_id]
        self._write_json(updated_chats)
        return True

    def rename_chat(self, chat_id: str, new_title: str):
        chats = self.get_chats()
        for chat in chats:
            if chat.get("id") == chat_id:
                chat["title"] = new_title
                break
        self._write_json(chats)
        return True

chat_store = ChatStore()
