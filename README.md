# KnowDoc | AI Document Intelligence Workspace

> **Upload → OCR → Embed → Store → Chat.** Every stage verified. No silent failures.

KnowDoc is a production-ready **RAG (Retrieval-Augmented Generation)** document intelligence platform. Upload any PDF, DOCX, image, or text file, and KnowDoc extracts the text, generates Jina semantic embeddings, stores them in ChromaDB, and lets you have a context-aware AI conversation with your documents — all through a premium Next.js interface.

---

## 🏗️ System Architecture

```text
[ Next.js Frontend (Vercel) ]
          │
          ▼  POST /api/upload  (multipart)
[ FastAPI Backend (Render) ]
          │
          ├── Returns 202 Accepted & {"status": "processing"} immediately
          │
          ▼  [ BackgroundTask: Asynchronous Ingestion ]
[ Stage 1: Extract Text ]
     ├── PDF with selectable text → PyMuPDF (fast, no API call)
     ├── Scanned PDF / Image     → PaddleOCR Cloud API (VL-1.6)
     ├── DOCX                    → xml.etree.ElementTree
     └── TXT                     → plain read
          │
          ▼
[ Stage 2: Chunk Text ]
     └── 300-word chunks, 50-word overlap
          │
          ▼
[ Stage 3: Jina Embeddings ]
     └── jina-embeddings-v4 (cloud API)
          │
          ▼
[ Stage 4: ChromaDB Insert ]
     └── Upsert vectors + metadata
          │
          ▼
[ Stage 5: Finalize Status ]
     └── Update documents.json → status: "completed", save text coordinates

[ Frontend Polling ]
     └── GET /api/documents every 2s → Syncs UI when status == "completed"

[ RAG Chat: POST /api/chat ]
     ├── Embed query → ChromaDB cosine search (top 5)
     ├── Build context block (max 12,000 chars)
     ├── Sliding memory window (last 6 turns)
     └── OpenRouter LLM → structured markdown reply
```

---

## 📂 Documentation

| Doc | Contents |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Pipeline stages, data flow, ChromaDB schema |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | All endpoints, request/response schemas |
| [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Directory map, file responsibilities |
| [SECURITY.md](docs/SECURITY.md) | CORS, rate limiting, CSP, API key handling |

---

## 🛠️ File Responsibilities

### Backend — Core Pipeline

| File | Role |
|---|---|
| [pipeline.py](backend/app/services/ingestion/pipeline.py) | **Master ingestion pipeline** — 5 validated stages |
| [paddle_service.py](backend/app/services/ocr/paddle_service.py) | PaddleOCR Cloud API wrapper — submits job, polls, downloads JSONL, extracts markdown |
| [pdf_service.py](backend/app/services/ocr/pdf_service.py) | Two-path PDF router: PyMuPDF (selectable) → PaddleOCR (scanned) |
| [upload_service.py](backend/app/services/storage/upload_service.py) | Validates file, saves to disk under original name (prevents collisions), queues `BackgroundTasks`, returns immediate response |
| [embeddings_service.py](backend/app/services/ai/embeddings_service.py) | Jina `jina-embeddings-v4` API client — bulk embedding generation |
| [rag_pipeline.py](backend/app/services/ai/rag_pipeline.py) | ChromaDB semantic search, OpenRouter completion, citation mapping, chat memory indexing & purging |
| [openrouter_service.py](backend/app/services/ai/openrouter_service.py) | OpenRouter API client — lazy-loaded singleton, markdown contract prompts |
| [chroma.py](backend/app/db/chroma.py) | ChromaDB persistent client — cosine similarity collection |
| [metadata_store.py](backend/app/db/metadata_store.py) | Thread-safe JSON store for document metadata |
| [main.py](backend/app/main.py) | FastAPI app entrypoint — configured with dynamic CORS regex for Vercel & local subnets |

### Backend — API Routes

| Route | Method | Description |
|---|---|---|
| `/api/upload` | POST | Upload document, queue ingestion in background, return 202 Accepted |
| `/api/debug-index` | POST | Full pipeline — returns all stage counts in response |
| `/api/chat` | POST | RAG chat query |
| `/api/chats` | GET/POST | List / create chat sessions |
| `/api/chats/{id}` | GET/PUT/DELETE | Get / rename / delete chat (wipes ChromaDB memory on delete) |
| `/api/documents` | GET | List all indexed documents (validates physical file existence) |
| `/api/documents/{id}` | GET/DELETE | Get / delete document (physically removes disk file + vectors) |
| `/api/admin/reset-database` | POST | Administrative system reset — programmatically purges vector collections and wipes all local uploaded files, registry stores, and chat threads. |
| `/api/health` | GET | Backend health check |

### Frontend

| File | Role |
|---|---|
| `frontend/app/workspace/page.js` | Main workspace — upload, sidebar, chat |
| `frontend/components/workspace/Chat/MessageBubble.jsx` | Markdown rendering, citation badges |
| `frontend/lib/api.js` | REST API client layer |

---

## 🚀 Local Setup

### Prerequisites

- **Python 3.11.9** — [download](https://www.python.org/downloads/release/python-3119/)
- **Node.js 18+** — [download](https://nodejs.org/)

### 1. Clone

```bash
git clone https://github.com/Yashank024/KnowDoc.git
cd KnowDoc
```

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

Create `backend/.env`:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=tencent/hy3:free
PADDLEOCR_API_KEY=your_paddleocr_api_key
JINA_API_KEY=your_jina_api_key
```

Start backend:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Workspace | http://localhost:3000/workspace |
| Backend | http://127.0.0.1:8000 |
| Swagger | http://127.0.0.1:8000/docs |

---

## 🧪 Debug & Validation

Use the debug endpoint to verify the full pipeline without storing metadata:

```bash
curl -X POST http://127.0.0.1:8000/api/debug-index \
  -F "file=@your_document.pdf"
```

Expected response:

```json
{
  "filename": "your_document.pdf",
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

If any stage fails, the response shows `success: false` with the exact `pipeline_stopped_at` stage and `error` message.

---

## 🗄️ Data Storage

```
backend/app/
├── uploads/          ← uploaded files (served locally)
├── vector_db/        ← ChromaDB persistent store (chroma.sqlite3)
└── db/data/
    ├── documents.json ← document metadata registry
    ├── chats.json     ← chat session threads
    └── folders.json   ← workspace folder groupings
```

---

## 🌐 Production Deployment

| Component | Platform |
|---|---|
| Frontend | [Vercel](https://knowdoc.vercel.app) |
| Backend | [Render](https://knowdoc-backend.onrender.com) |
| Version Control | GitHub |

Required environment variables on Render:

```env
OPENROUTER_API_KEY=...
OPENROUTER_MODEL=tencent/hy3:free
PADDLEOCR_API_KEY=...
JINA_API_KEY=...
```

---

## ⚡ Key Design Decisions

| Decision | Rationale |
|---|---|
| **Asynchronous Background Processing** | Prevents Vercel/Render timeouts. File uploads return immediately, frontend polls for completion. |
| **Physical File Integrity** | Deleting a document or chat physically purges the source file from disk and wipes its ChromaDB memory. Duplicate names on upload are blocked. |
| **Dynamic CORS Regex** | Automatically handles Vercel's dynamic branch preview subdomains without manual reconfiguration. |
| **PaddleOCR Cloud API** | Eliminates heavy local GPU/CPU model loading on Render's free tier |
| **Jina Embeddings Cloud** | High-quality `jina-embeddings-v4` without local model storage |
| **PyMuPDF first** | Sub-millisecond text extraction for selectable PDFs — PaddleOCR only for scanned |
| **HTTP 422 on failure** | Frontend receives exact stage name + reason if pipeline encounters error. |
| **Zero-Downtime Database Resets** | Programmatically drops the ChromaDB document collection instead of attempting folder deletions. This prevents process locks and SQLite "readonly database" write errors on Render containers without container restarts. |
| **Dynamic Viewport Locks & Scoped Scroll Anchors** | Locks root document scrollable offsets to `100dvh` and uses scoped element scrolling inside message lists. This blocks mobile browser visual viewport shifts when virtual keyboards trigger. |
| **Mobile Catalog Viewport Refactoring** | Converts Explorer tag filters into dynamic horizontal chip sliders and unifies page-level layout scrolls, preventing layout overflows and separate viewport scroll shifts on phone resolutions. |

---

## 🔗 Links

- **Live App**: https://knowdoc.vercel.app
- **GitHub**: https://github.com/Yashank024/KnowDoc
- **Demo Video**: https://drive.google.com/file/d/1zkwUhqDMrG_B--oI4CV4dLKv1DiHSVaS/view

---

## 👨‍💻 Developed By

**Yashank Gupta** — AI Architect & Full Stack Developer