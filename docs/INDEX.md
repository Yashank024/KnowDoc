# KnowDoc — Documentation Index

> Use this page as the entry point to all KnowDoc documentation.

---

## Guides

| Document | Description |
|---|---|
| [README.md](../README.md) | Project overview, setup instructions, deployment guide |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Full data flow diagrams, pipeline stages, ChromaDB schema, external API integrations |
| [API_REFERENCE.md](API_REFERENCE.md) | All REST endpoints with request/response schemas and cURL examples |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Directory map, file responsibilities, what changed in v3 |
| [SECURITY.md](SECURITY.md) | CORS policy, rate limiting, security headers, API key handling |

---

## Quick Links

### For Developers

- **Start here**: [README.md → Local Setup](../README.md#-local-setup)
- **API exploration**: `http://127.0.0.1:8000/docs` (Swagger UI when running locally)
- **Debug a pipeline issue**: [POST /api/debug-index](API_REFERENCE.md#post-apidebug-index)
- **Understand the ingestion flow**: [ARCHITECTURE.md → Data Flow](ARCHITECTURE.md#data-flow)

### For Deployment

- **Environment variables**: [PROJECT_STRUCTURE.md → Environment Variables](PROJECT_STRUCTURE.md#environment-variables)
- **CORS configuration**: [SECURITY.md](SECURITY.md)
- **Backend**: Render → `knowdoc-backend.onrender.com`
- **Frontend**: Vercel → `knowdoc.vercel.app`

---

## Version

**KnowDoc v3.1** — Asynchronous Ingestion & Visual Sync Update (July 2026)

Key changes in v3.1:
- Asynchronous pipeline (runs in background via FastAPI BackgroundTasks with status polling)
- Layout-aware OCR (coordinates mapped to PyMuPDF blocks and PaddleOCR points)
- Interactive Visual Canvas (bounding boxes scaled and synchronized dynamically)
- Name collision protection & clean file-delete sync on disk
- PaddleOCR Cloud API + Jina Embeddings Cloud (no local models)
- 5-stage validation with exact error reporting
