import logging
import uuid
from datetime import datetime
from app.db.chat_store import chat_store

logger = logging.getLogger("chat_service")

class ChatService:
    def list_chat_sessions(self, session_id: str = None):
        if session_id:
            return chat_store.get_chats_by_session(session_id)
        return chat_store.get_chats()

    def get_chat_session(self, chat_id: str):
        return chat_store.get_chat_by_id(chat_id)

    def create_chat_session(self, session_id: str, title: str = "Document Chat Session"):
        chat_id = f"chat_{uuid.uuid4().hex[:8]}"
        chat_data = {
            "id": chat_id,
            "session_id": session_id,
            "title": title,
            "timestamp": "Just now",
            "messages": []
        }
        return chat_store.add_chat(chat_data)

    def append_message_to_chat(self, chat_id: str, sender: str, text: str, session_id: str = None):
        session = self.get_chat_session(chat_id)
        if not session:
            if not session_id:
                session_id = "default_session"
            session = self.create_chat_session(session_id=session_id)
            chat_id = session["id"]

        messages = session.get("messages", [])
        messages.append({
            "id": f"msg_{uuid.uuid4().hex[:8]}",
            "sender": sender,
            "text": text,
            "timestamp": datetime.now().strftime("%I:%M %p")
        })
        chat_store.update_chat_messages(chat_id, messages)
        return session

    def delete_chat_session(self, chat_id: str):
        return chat_store.delete_chat(chat_id)

    def rename_chat_session(self, chat_id: str, new_title: str):
        return chat_store.rename_chat(chat_id, new_title)

chat_service = ChatService()
