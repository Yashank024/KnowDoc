# KnowDoc — Project Structure

```
KnowDoc/
├── README.md                          ← Project overview + setup guide
├── docs/
│   ├── INDEX.md                       ← Documentation index
│   ├── ARCHITECTURE.md                ← Data flow, pipeline stages, ChromaDB schema
│   ├── API_REFERENCE.md               ← All REST endpoints with schemas
│   ├── PROJECT_STRUCTURE.md           ← This file
│   └── SECURITY.md                    ← CORS, rate limiting, headers, key handling
│
├── frontend/                          ← Next.js application (deployed on Vercel)
│   ├── app/
│   │   └── workspace/
│   │       └── page.js                ← Main workspace: upload, sidebar, chat
│   ├── components/
│   │   └── workspace/
│   │       └── Chat/
│   │           └── MessageBubble.jsx  ← Markdown rendering + citation badges
│   └── lib/
│       └── api.js                     ← REST API client
│
└── backend/                           ← FastAPI application (deployed on Render)
    ├── .env                           ← API keys (NOT committed)
    ├── requirements.txt               ← Python dependencies
    │
    └── app/
        ├── main.py                    ← FastAPI app, middleware, router registration
        │
        ├── core/
        │   └── config.py              ← ENV variable loading, directory scaffolding
        │
        ├── api/
        │   └── routes/
        │       ├── health.py          ← GET /api/health
        │       ├── upload.py          ← POST /api/upload, /api/ocr, /api/debug-index
        │       ├── chat.py            ← POST /api/chat, /chat  +  chat CRUD
        │       ├── documents.py       ← GET/DELETE /api/documents
        │       └── folders.py         ← GET/POST/DELETE /api/folders
        │
        ├── services/
        │   │
        │   ├── ingestion/             ← ★ Core pipeline (new in v3)
        │   │   ├── __init__.py
        │   │   └── pipeline.py        ← run_pipeline(): 5 validated stages, layout-aware coordinate mapping
        │   │
        │   ├── ocr/
        │   │   ├── paddle_service.py  ← PaddleOCR Cloud API — job submit/poll/parse + coordinate scaling
        │   │   └── pdf_service.py     ← PDF router: PyMuPDF (blocks) → PaddleOCR (points) + coordinate scaling
        │   │
        │   ├── ai/
        │   │   ├── embeddings_service.py  ← Jina jina-embeddings-v4 API client
        │   │   ├── rag_pipeline.py        ← Search + OpenRouter + citation + QA memory indexing
        │   │   └── openrouter_service.py  ← OpenRouter completions (singleton)
        │   │
        │   ├── storage/
        │   │   ├── upload_service.py  ← File save (original name) + background task pipeline execution
        │   │   └── file_service.py    ← Raw disk I/O (save / delete)
        │   │
        │   └── chat/
        │       ├── chat_service.py    ← Session CRUD, message append, auto-rename
        │       ├── citation_service.py ← Citation normalization for frontend
        │       └── memory_service.py  ← Sliding window (last 6 turns)
        │
        ├── db/
        │   ├── chroma.py              ← ChromaDB persistent client (singleton)
        │   ├── metadata_store.py      ← Thread-safe JSON store (documents + folders)
        │   ├── chat_store.py          ← Thread-safe chat session JSON store
        │   └── data/
        │       ├── documents.json     ← Document metadata registry
        │       ├── chats.json         ← Chat sessions
        │       └── folders.json       ← Workspace folders
        │
        ├── utils/
        │   ├── chunking.py            ← Legacy chunker (used by rag_pipeline)
        │   ├── hash_utils.py          ← MD5 computation
        │   ├── file_utils.py          ← File path utilities
        │   ├── text_utils.py          ← Text cleaning helpers
        │   └── validators.py          ← Input validators
        │
        ├── uploads/                   ← Saved uploaded files
        └── vector_db/                 ← ChromaDB persistent storage (chroma.sqlite3)
```

---

## Key Architectural Rules

### What the pipeline.py does

`run_pipeline(doc_id, filename, file_path, file_ext) -> PipelineResult`

1. **Stage 1** — Routes file extension to the correct extractor. Returns `text_lines: list[str]`.
2. **Stage 2** — Splits `text_lines` into overlapping word-count chunks (300w / 50w overlap).
3. **Stage 3** — Calls Jina API in bulk. Validates count matches.
4. **Stage 4** — Upserts into ChromaDB with `type: "document"` metadata.
5. **Stage 5** — Fetches the inserted IDs back. Validates count. Gets `collection.count()`.

Returns `PipelineResult` dataclass — never raises.

### What was removed in v3 (and updated in v3.1)

- `image_service.py` — dead code (pipeline uses `paddle_service.run()` directly)
- `debug_ocr.py` — replaced by `/api/debug-index`
- Background task processing — Restored (runs asynchronously via FastAPI BackgroundTasks with status polling)
- Coordinate / bounding box parsing — Restored (mapped to PyMuPDF block coords, scaled layout points, and dummy DOCX/TXT segments)
- MD5 cache check — removed (was causing stale cache hits)
- `query_classifier.py` — removed (was bypassing RAG for short queries)

### What was not changed

- `rag_pipeline.py` search and answer logic — clean, working
- `openrouter_service.py` — clean, working
- `embeddings_service.py` — clean, working
- `chroma.py` — clean, working
- `metadata_store.py` — clean, working
- Frontend components — updated to support real-time status polling, activeDoc synchronization, and custom status indicators

---

## Environment Variables

All set in `backend/.env` (never committed to git).

| Variable | Description | Required |
|---|---|---|
| `OPENROUTER_API_KEY` | OpenRouter completions | ✅ |
| `OPENROUTER_MODEL` | Model name (default: `tencent/hy3:free`) | ✅ |
| `PADDLEOCR_API_KEY` | PaddleOCR Cloud API token | ✅ |
| `JINA_API_KEY` | Jina Embeddings API key | ✅ |
| `OPENROUTER_MAX_TOKENS` | Max response tokens (default: 2048) | ❌ |
