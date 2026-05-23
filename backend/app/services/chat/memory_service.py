import logging

logger = logging.getLogger("memory_service")

class MemoryService:
    def build_chat_history_context(self, messages: list, max_turns: int = 5) -> str:
        """
        Builds a sliding window chat history context string to feed to the LLM.
        """
        if not messages:
            return ""

        context_turns = messages[-max_turns * 2:]
        history_parts = []
        for msg in context_turns:
            sender = "User" if msg.get("sender") == "user" else "Assistant"
            text = msg.get("text", "")
            history_parts.append(f"{sender}: {text}")
            
        return "\n".join(history_parts)

memory_service = MemoryService()
