# KnowDoc — REST API Reference

Base URL (production): `https://knowdoc-backend.onrender.com`  
Base URL (local): `http://127.0.0.1:8000`  
Interactive docs: `http://127.0.0.1:8000/docs`

---

## Health

### `GET /api/health`

Returns backend status.

**Response**
```json
{ "status": "ok" }
```

---

## Document Ingestion

### `POST /api/upload`

Upload and register a document. **Asynchronous** — returns HTTP 200 immediately with status `"processing"` and schedules the ingestion pipeline in the background.

**Request** — `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | File | Document to upload (PDF, DOCX, TXT, JPG, PNG, BMP, TIFF, WEBP) |

**Success Response** `HTTP 200`

```json
{
  "status": "success",
  "document_id": "doc_a1b2c3d4",
  "id": "doc_a1b2c3d4",
  "filename": "report.pdf",
  "size": "1.2 MB",
  "status": "processing",
  "text_lines": [],
  "full_text": ""
}
```

*Note: Since the ingestion pipeline runs in the background, failures are marked dynamically inside the document's `"status": "failed"` field in the metadata registry, rather than returning HTTP 422 immediately.*

**Supported file types**: `.pdf`, `.docx`, `.txt`, `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.webp`

---

### `POST /api/ocr`

Alias for `/api/upload`. Identical behaviour.

---

### `POST /api/debug-index`

Runs the complete pipeline and returns every stage count. Does **not** register the document in the metadata store.

**Request** — `multipart/form-data` (same as `/api/upload`)

**Response** `HTTP 200`

```json
{
  "filename": "document.pdf",
  "extraction_source": "pymupdf",
  "text_lines": 186,
  "chunks": 23,
  "embeddings": 23,
  "vectors_inserted": 23,
  "collection_count": 23,
  "success": true,
  "error": null,
  "pipeline_stopped_at": null
}
```

On failure:
```json
{
  "success": false,
  "error": "Jina API error: 401 Unauthorized",
  "pipeline_stopped_at": "Stage 3: Embed",
  "text_lines": 186,
  "chunks": 23,
  "embeddings": 0
}
```

**cURL example**
```bash
curl -X POST https://knowdoc-backend.onrender.com/api/debug-index \
  -F "file=@my_document.pdf"
```

---

## Documents

### `GET /api/documents`

Returns all registered documents in the metadata store.

**Response** `HTTP 200`
```json
[
  {
    "id": "doc_a1b2c3d4",
    "filename": "report.pdf",
    "size": "1.2 MB",
    "date": "Jul 12, 2026",
    "tags": ["Uploaded", "PDF"],
    "status": "completed",
    "hash": "abc123...",
    "path": "/path/to/uploads/report.pdf"
  }
]
```

---

### `GET /api/documents/{doc_id}`

Returns a single document record.

**Response** `HTTP 200` — same schema as above  
**Error** `HTTP 404` — `{ "detail": "Document not found" }`

---

### `DELETE /api/documents/{doc_id}`

Deletes the document from:
- `documents.json` metadata registry
- Disk uploads directory (physically deletes the file)
- ChromaDB vector collection (all chunks with matching `doc_id`)

**Response** `HTTP 200`
```json
{
  "status": "success",
  "message": "Document doc_a1b2c3d4 and its physical file/vector indices deleted successfully."
}
```

---

## Chat

### `POST /api/chat`

Send a RAG query. Returns an AI reply with citations.

**Request body**
```json
{
  "message": "What is the main topic of the uploaded document?",
  "chat_id": "chat_abc123",
  "session_id": "browser-session-uuid",
  "doc_ids": ["doc_a1b2c3d4"],
  "history": [
    { "sender": "user", "text": "Hello" },
    { "sender": "ai", "text": "Hi, how can I help?" }
  ]
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | str | ✅ | User query |
| `chat_id` | str | ✅ | Chat session identifier |
| `session_id` | str | ❌ | Browser session UUID |
| `doc_ids` | list[str] | ❌ | Scope search to specific docs (omit for global) |
| `history` | list | ❌ | Last N conversation turns for memory context |

**Response** `HTTP 200`
```json
{
  "reply": "The document discusses **Retrieval-Augmented Generation** (RAG)...",
  "citations": [
    {
      "source_index": 1,
      "filename": "report.pdf",
      "pages": [1, 2, 5]
    }
  ],
  "chunks_searched": 4,
  "chat_title": "RAG Architecture Overview"
}
```

---

### `GET /api/chats`

List chat sessions, optionally filtered by `session_id`.

**Query params**: `?session_id=browser-uuid`

**Response** — array of chat session objects

---

### `POST /api/chats`

Create a new chat session.

**Request body**
```json
{
  "session_id": "browser-uuid",
  "title": "Document Chat Session"
}
```

---

### `GET /api/chats/{chat_id}`

Get full message history for a chat session.

---

### `PUT /api/chats/{chat_id}`

Rename a chat session.

**Request body**
```json
{ "title": "New Name" }
```

---

### `DELETE /api/chats/{chat_id}`

Delete a chat session. Removes the chat thread from `chats.json` and clears all associated conversational QA memory vectors from ChromaDB (all vectors with `doc_id: chat_memory_{chat_id}`).

---

## Folders

### `GET /api/folders`

List all workspace folders.

### `POST /api/folders`

Create a new folder.

### `DELETE /api/folders/{folder_id}`

Delete a folder.

---

## Error Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 400 | Bad request (unsupported file type, missing fields) |
| 404 | Resource not found |
| 409 | Conflict (document with this filename already exists on disk) |
| 422 | Pipeline failure — check `detail.pipeline_stopped_at` (returned by `/api/debug-index` only) |
| 429 | Rate limit exceeded (60 req/min per IP) |
| 500 | Server error |
