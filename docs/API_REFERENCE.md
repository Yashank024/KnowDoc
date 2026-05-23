# 🔌 REST API Reference - KnowDoc Platform

The FastAPI backend exposes standard, performance-tuned REST endpoints mapped under the `/api` namespace to coordinate workspace resources and generative RAG conversational sessions.

---

## 🚦 Endpoint Quick Registry

| HTTP Method | Route | Description | Input Parameters |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/health` | PaddleOCR service status check | None |
| **POST** | `/api/ocr` | Asynchronous file upload ingestion | `file` (Binary Multipart Form) |
| **GET** | `/api/documents` | Retrieve all document metadata logs | None |
| **DELETE** | `/api/documents/{doc_id}` | Purge document from JSON registry and ChromaDB | `doc_id` (Path Parameter) |
| **GET** | `/api/chats` | List all persistent chat threads | `session_id` (Query String) |
| **POST** | `/api/chats` | Create a new session thread in `chats.json` | `session_id`, `title` (JSON Body) |
| **DELETE** | `/api/chats/{chat_id}` | Purge a specific chat history thread | `chat_id` (Path Parameter) |
| **POST** | `/api/chat` | Send conversational query through RAG pipeline | `message`, `chat_id`, `session_id`, `doc_ids`, `history` (JSON Body) |

---

## ⚡ Detail Specifications & Payloads

### 1. PaddleOCR System Health Status
Checks operational availability of Python libraries, configuration variables, and model files.

*   **Endpoint**: `GET /api/health`
*   **Response Payload (`200 OK`)**:
    ```json
    {
      "status": "healthy",
      "paddleocr": "loaded",
      "device": "cpu",
      "embeddings": "active"
    }
    ```
*   **cURL Example**:
    ```bash
    curl -X GET http://127.0.0.1:8000/api/health
    ```

---

### 2. Asynchronous Ingestion Upload
Uploads select images or PDF documents. The file is analyzed, cached by MD5 checksum, and parsed asynchronously inside background worker queues.

*   **Endpoint**: `POST /api/ocr`
*   **Content Type**: `multipart/form-data`
*   **Response Payload (`200 OK`)**:
    ```json
    {
      "id": "doc_e4c5b32f",
      "filename": "annual_hr_leave_2026.pdf",
      "hash": "7a35e29fa417b1b59074811b7d5ec92f",
      "status": "uploading",
      "message": "Document registered successfully. Processing text extraction in background."
    }
    ```
*   **cURL Example**:
    ```bash
    curl -X POST http://127.0.0.1:8000/api/ocr \
      -F "file=@/C:/Users/Lenovo/Desktop/Invoices/invoice_102.pdf"
    ```

---

### 3. List Dynamic Documents
Lists all currently registered files along with their current background task statuses.

*   **Endpoint**: `GET /api/documents`
*   **Response Payload (`200 OK`)**:
    ```json
    [
      {
        "id": "doc_e4c5b32f",
        "filename": "annual_hr_leave_2026.pdf",
        "size": "1.2 MB",
        "date": "May 23, 2026",
        "status": "completed",
        "full_text": "Extracted document context...",
        "text_lines": [
          {
            "text": "Annual standard vacation leave allocation is 20 days.",
            "box": [120, 240, 680, 280],
            "confidence": 0.99
          }
        ]
      }
    ]
    ```
*   **cURL Example**:
    ```bash
    curl -X GET http://127.0.0.1:8000/api/documents
    ```

---

### 4. Create Chat Session Thread
Instantiates a persistent conversation session linked to the unique browser session.

*   **Endpoint**: `POST /api/chats`
*   **Request JSON Body**:
    ```json
    {
      "session_id": "3136071e-b5ea-4d8e-9570-1cba831b83b5",
      "title": "Invoice Audit Thread"
    }
    ```
*   **Response Payload (`200 OK`)**:
    ```json
    {
      "id": "chat_f3e9a1b0",
      "session_id": "3136071e-b5ea-4d8e-9570-1cba831b83b5",
      "title": "Invoice Audit Thread",
      "timestamp": "Just now",
      "messages": []
    }
    ```
*   **cURL Example**:
    ```bash
    curl -X POST http://127.0.0.1:8000/api/chats \
      -H "Content-Type: application/json" \
      -d '{"session_id": "3136071e-b5ea-4d8e-9570-1cba831b83b5", "title": "Invoice Audit Thread"}'
    ```

---

### 5. Unified Conversational RAG Engine
Routes a query through the classifier and semantic context vector matching layers, returning a response string and matching citations. Also, saves the messages inside the database.

*   **Endpoint**: `POST /api/chat`
*   **Request JSON Body**:
    ```json
    {
      "message": "What is the holiday vacation leave limit?",
      "chat_id": "chat_f3e9a1b0",
      "session_id": "3136071e-b5ea-4d8e-9570-1cba831b83b5",
      "doc_ids": ["doc_e4c5b32f"],
      "history": [
        {
          "sender": "user",
          "text": "Hello KnowDoc AI"
        },
        {
          "sender": "ai",
          "text": "Hello Yashank! How can I help audit your document catalog today?"
        }
      ]
    }
    ```
*   **Response Payload (`200 OK`)**:
    ```json
    {
      "reply": "According to the HR manual, standard vacation allocation is **20 days** per calendar year [Doc 1, Page 1].",
      "citations": [
        {
          "text": "Annual standard vacation leave allocation is 20 days.",
          "metadata": {
            "source": "annual_hr_leave_2026.pdf",
            "doc_index": 0,
            "page_index": 1,
            "box": [120, 240, 680, 280]
          }
        }
      ]
    }
    ```
*   **cURL Example**:
    ```bash
    curl -X POST http://127.0.0.1:8000/api/chat \
      -H "Content-Type: application/json" \
      -d '{"message": "What is the holiday vacation leave limit?", "chat_id": "chat_f3e9a1b0", "session_id": "3136071e-b5ea-4d8e-9570-1cba831b83b5", "doc_ids": ["doc_e4c5b32f"], "history": []}'
    ```
