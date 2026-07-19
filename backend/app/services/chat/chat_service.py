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

    def append_message_to_chat(self, chat_id: str, sender: str, text: str, citations: list = None, session_id: str = None):
        session = self.get_chat_session(chat_id)
        if not session:
            if not session_id:
                session_id = "default_session"
            session = self.create_chat_session(session_id=session_id)
            chat_id = session["id"]

        messages = session.get("messages", [])
        msg_obj = {
            "id": f"msg_{uuid.uuid4().hex[:8]}",
            "sender": sender,
            "text": text,
            "timestamp": datetime.now().strftime("%I:%M %p")
        }
        if citations is not None:
            msg_obj["citations"] = citations
            
        messages.append(msg_obj)
        chat_store.update_chat_messages(chat_id, messages)
        return session

    def auto_rename_chat(self, chat_id: str, first_query: str):
        """
        Auto-generates a short, descriptive 3-5 word title based on the first query using OpenRouter,
        and saves it to the chat session in chats.json.
        """
        session = self.get_chat_session(chat_id)
        if not session:
            return None
            
        current_title = session.get("title", "")
        if not current_title or current_title.startswith("Document Chat Session"):
            try:
                from app.services.ai.openrouter_service import openrouter_service
                prompt = (
                    f"Generate a short, descriptive 3-5 word title for a chat thread that starts with this user query:\n"
                    f"\"{first_query}\"\n\n"
                    f"Strict Constraint: Return ONLY the title text itself. Do not write explanations, introductions, markdown tags, quotes, or punctuation. Make it concise and professional."
                )
                system_instruction = "You are a concise thread titling assistant."
                logger.info(f"Auto-titling: Generating title for chat {chat_id}...")
                new_title = openrouter_service.generate_response(prompt, system_instruction=system_instruction)
                new_title = new_title.strip().strip('"').strip("'").strip()
                
                # Truncate if too long
                if len(new_title) > 40:
                    new_title = new_title[:37] + "..."
                    
                if new_title:
                    logger.info(f"Auto-titling: Renaming chat {chat_id} to '{new_title}'")
                    self.rename_chat_session(chat_id, new_title)
                    return new_title
            except Exception as e:
                logger.error(f"Failed to auto-generate chat title: {e}")
        return None

    def delete_chat_session(self, chat_id: str):
        return chat_store.delete_chat(chat_id)

    def rename_chat_session(self, chat_id: str, new_title: str):
        return chat_store.rename_chat(chat_id, new_title)

chat_service = ChatService()
