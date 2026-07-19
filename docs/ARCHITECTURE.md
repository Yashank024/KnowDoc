# KnowDoc — System Architecture

## Overview

KnowDoc is a document intelligence platform built on an **asynchronous, stage-validated ingestion pipeline**. Every stage produces a measurable output that is verified before the next stage begins. No stage silently fails.

---

## Data Flow

```
User Upload (POST /api/upload)
         │
         ▼
[Upload Service]
  • Validate file extension & name collision
  • Save file using original name to backend/app/uploads/
  • Register document in documents.json (status: "processing")
  • Schedule run_pipeline() asynchronously in BackgroundTasks
  • Return success/processing status immediately to Frontend
         │
         ▼
[Ingestion Pipeline — app/services/ingestion/pipeline.py]
         │
    Stage 1: Extract Text
    ┌────────────────────────────────────────────────┐
    │  .pdf with selectable text  →  PyMuPDF fitz    │
    │  .pdf scanned / image       →  PaddleOCR Cloud │
    │  .docx                      →  xml.etree       │
    │  .txt                       →  plain read      │
    │  .jpg/.png/.bmp/etc.        →  PaddleOCR Cloud │
    └────────────────────────────────────────────────┘
    VALIDATE: text_lines > 0  →  else FAIL
         │
    Stage 2: Chunk Text
    • 300-word chunks, 50-word overlap
    • Layout-aware: groups page lists and scales box coordinates to [0, 1000]
    VALIDATE: chunks > 0  →  else FAIL
         │
    Stage 3: Jina Embeddings
    • Model: jina-embeddings-v4
    • Bulk API call to api.jina.ai/v1/embeddings
    VALIDATE: len(embeddings) == len(chunks)  →  else FAIL
         │
    Stage 4: ChromaDB Insert
    • collection.upsert(ids, documents, embeddings, metadatas)
    • Metadata: {doc_id, filename, type:"document", chunk_index, pages, box_coords}
         │
    Stage 5: Verify Insertion
    • collection.get(ids=[...])
    • collection.count()
    VALIDATE: retrieved_count == inserted_count  →  else FAIL
         │
         ▼
[Background Worker Task]
  • Update status: "completed" (or "failed" on error)
  • Persist full_text and text_lines coordinates to documents.json registry
  • Frontend polling interval syncs activeDoc coordinates automatically
```

---

## RAG Chat Flow

```
User Query (POST /api/chat)
         │
         ▼
[RAG Pipeline — rag_pipeline.py]
  1. Check in-memory query cache (skip API calls on repeat queries)
  2. Build memory context from last 6 conversation turns
  3. Embed query → Jina API
  4. ChromaDB cosine search (top 5 chunks, distance ≤ 1.65)
  5. Build context block (max 12,000 characters)
  6. Invoke OpenRouter (model: tencent/hy3:free) under markdown contract
  7. Map retrieved chunks → citation objects
  8. Index QA turn → ChromaDB (type: chat_memory)
         │
         ▼
Return: { reply, citations, chunks_searched }
```

---

## ChromaDB Schema

**Collection name**: `document_chunks`  
**Distance metric**: cosine similarity

| Field | Type | Description |
|---|---|---|
| `id` | str | `{doc_id}_chunk_{index}` |
| `document` | str | Raw chunk text (300 words) |
| `embedding` | list[float] | Jina v4 dense vector |
| `doc_id` | str | Parent document identifier |
| `filename` | str | Original filename |
| `type` | str | `"document"` or `"chat_memory"` |
| `chunk_index` | str | Position within document |
| `pages` | str | Comma-separated list of pages where chunk resides |
| `box_coords` | str | Stringified layout coordinates for bounding box rendering |

**Retrieval filter logic:**
- When `doc_ids` provided: `WHERE doc_id IN [...]`
- Global search: `WHERE type == "document"`
- With `chat_id`: `OR WHERE doc_id == "chat_memory_{chat_id}"`

---

## PaddleOCR Cloud Integration

**API**: `https://paddleocr.aistudio-app.com/api/v2/ocr/jobs`  
**Model**: `PaddleOCR-VL-1.6`

```
Submit job (POST)
       │
       ▼
Poll state every 5s (max 120 attempts = 10 min)
       │ state == "done"
       ▼
Download JSONL from resultUrl.jsonUrl
       │
       ▼
Parse: layoutParsingResults[*].markdown.text
       │
       ▼
Split markdown into text_lines (strip markdown tokens)
       │
       ▼
Return PaddleResult(text_lines, markdown, page_count)
```

The **full raw JSONL** is logged to the server console on every call for debugging.

---

## Document Metadata Lifecycle

```
Upload received
    status: "processing"
         │
    pipeline runs...
         │
    success        failure
    status: "completed"   status: "failed"
```

Documents are stored in `backend/app/db/data/documents.json` with a `threading.Lock()` protecting all reads and writes.

---

## External API Dependencies

| API | Purpose | Key variable |
|---|---|---|
| PaddleOCR Cloud | OCR for scanned PDFs and images | `PADDLEOCR_API_KEY` |
| Jina AI | Text embeddings (`jina-embeddings-v4`) | `JINA_API_KEY` |
| OpenRouter | LLM completions | `OPENROUTER_API_KEY` |

---

## Middleware Stack

Applied in `app/main.py` in this order (outermost → innermost):

1. **CORSMiddleware** — dynamically whitelists Vercel domains (`*.vercel.app`), `localhost`, and local private subnets
2. **SecurityHeadersMiddleware** — X-Frame-Options, CSP, XSS-Protection
3. **RateLimiterMiddleware** — 60 requests/minute per IP
