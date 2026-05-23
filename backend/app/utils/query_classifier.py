import re

RAG_KEYWORDS = [
    "document", "policy", "invoice", "file", "pdf", "database", "what does", 
    "search", "find", "tell me about", "summarize", "summary", "contract",
    "report", "analysis", "audit", "retrieve", "lookup", "info", "data", "sheet"
]

GREETING_PATTERNS = [
    r"^\s*(hi|hello|hey|hola|greetings|good\s+morning|good\s+afternoon|good\s+evening)\s*[?!.]*$",
    r"^\s*(thanks|thank\s+you|ty)\s*[?!.]*$",
    r"^\s*(ok|okay|got\s+it|sure|yes|no)\s*[?!.]*$",
    r"^\s*(help|who\s+are\s+you|what\s+is\s+this|what\s+can\s+you\s+do)\s*[?!.]*$"
]

def needs_rag(query: str) -> bool:
    """
    Identifies if a prompt requires RAG context retrieval or is a simple local reply.
    """
    if not query or not query.strip():
        return False
        
    cleaned_query = query.strip().lower()
    
    # Check if it matches simple greeting/conversational pattern
    for pattern in GREETING_PATTERNS:
        if re.match(pattern, cleaned_query):
            return False
            
    # Check for keyword matches that explicitly request information
    for kw in RAG_KEYWORDS:
        if kw in cleaned_query:
            return True
            
    # Default: if query is very short (e.g. < 15 chars) and doesn't match RAG keywords, probably a generic conversation
    if len(cleaned_query) < 15:
        return False
        
    return True

def get_local_response(query: str) -> dict:
    """
    Returns an instant local response to greetings and conversational prompts
    to bypass LLM and RAG overhead completely.
    """
    cleaned_query = query.strip().lower()
    
    # Hello / Hi
    if any(re.match(p, cleaned_query) for p in [r"^\s*(hi|hello|hey|hola|greetings|good\s+morning|good\s+afternoon|good\s+evening)\s*[?!.]*$"]):
        return {
            "reply": "Hello! I am KnowDoc AI, your premium conversational document intelligence workspace. How can I assist you with your documents today?",
            "citations": [],
            "chunks_searched": 0
        }
    
    # Thanks
    if any(re.match(p, cleaned_query) for p in [r"^\s*(thanks|thank\s+you|ty)\s*[?!.]*$"]):
        return {
            "reply": "You're very welcome! Let me know if you need help analyzing or auditing any other files.",
            "citations": [],
            "chunks_searched": 0
        }
        
    # Ok / Okay
    if any(re.match(p, cleaned_query) for p in [r"^\s*(ok|okay|got\s+it|sure|yes|no)\s*[?!.]*$"]):
        return {
            "reply": "Understood! Let me know when you are ready to audit or query your documents.",
            "citations": [],
            "chunks_searched": 0
        }
        
    # Help / What is this
    if any(re.match(p, cleaned_query) for p in [r"^\s*(help|who\s+are\s+you|what\s+is\s+this|what\s+can\s+you\s+do)\s*[?!.]*$"]):
        return {
            "reply": "I am KnowDoc AI, a production-grade Document RAG Intelligence workspace. Here is what I can do:\n\n"
                     "1. **Direct PyMuPDF Text Extraction (0.2s Bypass)**: Bypasses OCR for selectable PDFs, extracting text instantly.\n"
                     "2. **PaddleOCR Engine**: Scans images and non-selectable PDFs for complete text parsing.\n"
                     "3. **ChromaDB Vector Store**: Generates layout-aware chunks with overlap and indexes them permanently.\n"
                     "4. **AI Citation Audits**: Answers complex questions citing specific sources and pages with visual bounding boxes.\n\n"
                     "Simply upload your documents in the sidebar to get started!",
            "citations": [],
            "chunks_searched": 0
        }
        
    # Fallback
    return {
        "reply": "I am ready to help you analyze your documents. Please upload a file in the sidebar or ask a question about your documents to begin!",
        "citations": [],
        "chunks_searched": 0
    }
