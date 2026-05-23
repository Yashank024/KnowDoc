import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services.ai.rag_pipeline import rag_pipeline
from app.services.chat.chat_service import chat_service

logger = logging.getLogger("chat_routes")

router = APIRouter()

class ChatMessageSchema(BaseModel):
    sender: str
    text: str

class ChatRequest(BaseModel):
    message: str
    chat_id: str
    session_id: Optional[str] = None
    doc_ids: Optional[List[str]] = None
    history: Optional[List[ChatMessageSchema]] = None

class ChatSessionCreate(BaseModel):
    session_id: str
    title: Optional[str] = "Document Chat Session"

@router.get("/api/chats")
def list_chats(session_id: Optional[str] = Query(None)):
    """
    Lists all chat sessions, optionally filtered by browser session_id.
    """
    logger.info(f"Listing chat sessions for session_id: {session_id}")
    return chat_service.list_chat_sessions(session_id)

@router.get("/api/chats/{chat_id}")
def get_chat(chat_id: str):
    """
    Retrieves message history of a specific chat session thread.
    """
    logger.info(f"Retrieving chat session thread: {chat_id}")
    session = chat_service.get_chat_session(chat_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session

@router.post("/api/chats")
def create_chat(request: ChatSessionCreate):
    """
    Creates a new chat session thread linked to browser session_id.
    """
    logger.info(f"Creating new chat session thread for browser session_id: {request.session_id}")
    return chat_service.create_chat_session(session_id=request.session_id, title=request.title)

@router.delete("/api/chats/{chat_id}")
def delete_chat(chat_id: str):
    """
    Erase a chat session thread from local persistence chats.json store.
    """
    logger.info(f"Deleting chat session thread: {chat_id}")
    success = chat_service.delete_chat_session(chat_id)
    return {"status": "success", "message": f"Chat thread {chat_id} deleted successfully."}

class ChatRenameSchema(BaseModel):
    title: str

@router.put("/api/chats/{chat_id}")
def rename_chat(chat_id: str, request: ChatRenameSchema):
    """
    Rename a specific chat session thread and persist it to chats.json.
    """
    logger.info(f"Renaming chat session thread {chat_id} to '{request.title}'")
    success = chat_service.rename_chat_session(chat_id, request.title)
    if not success:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return {"status": "success", "title": request.title}

@router.get("/api/chat/history/{session_id}")
def get_chat_history_alias(session_id: str):
    """
    Alias route for browser session compatibility.
    """
    logger.info(f"Retrieving alias chat history for session: {session_id}")
    return chat_service.list_chat_sessions(session_id)

@router.post("/chat")
async def chat_direct(request: ChatRequest):
    """
    Direct endpoint for RAG chat audits (Step 6 compatibility).
    """
    logger.info(f"Received direct chat query for chat_id: {request.chat_id}")
    
    # 1. Save User Message
    chat_service.append_message_to_chat(request.chat_id, "user", request.message, session_id=request.session_id)
    
    # 2. Run RAG Pipeline
    result = rag_pipeline.answer_user_query(request.message, doc_ids=request.doc_ids, history=request.history)
    
    # 3. Save Assistant Message
    chat_service.append_message_to_chat(request.chat_id, "ai", result.get("reply", ""), session_id=request.session_id)
    
    return result

@router.post("/api/chat")
async def chat_api(request: ChatRequest):
    """
    Standardized /api namespace endpoint for RAG conversational audits.
    """
    logger.info(f"Received API chat query for chat_id: {request.chat_id}")
    
    # 1. Save User Message
    chat_service.append_message_to_chat(request.chat_id, "user", request.message, session_id=request.session_id)
    
    # 2. Run RAG Pipeline
    result = rag_pipeline.answer_user_query(request.message, doc_ids=request.doc_ids, history=request.history)
    
    # 3. Save Assistant Message
    chat_service.append_message_to_chat(request.chat_id, "ai", result.get("reply", ""), session_id=request.session_id)
    
    return result
