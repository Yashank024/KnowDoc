# KnowDoc AI - Production-Grade RAG Backend Engine

A highly optimized, modular, and senior-level practical **RAG (Retrieval-Augmented Generation)** backend engine designed for the **KnowDoc Workspace**. This engine is engineered for production-grade responsiveness, permanent persistence, and high-performance scalability, bypassing premature enterprise complexity by leveraging lightweight local stores and cutting-edge ingestion optimization.

---

## 🏗️ Folder Architecture

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py        # CPU PaddleOCR health check router
│   │   │   ├── upload.py        # Non-blocking PDF & Image upload ingestion router
│   │   │   ├── documents.py     # Documents catalog listing & deletes router
│   │   │   ├── folders.py       # Custom categories folder binds router
│   │   │   └── chat.py          # Session-synced Gemini RAG chatbot router
│   │   └── deps/
│   │       └── session.py       # Session dependency stubs
│   ├── core/
│   │   ├── config.py            # Environment directory bootstrap setups
│   │   ├── logger.py            # Unified logging manager
│   │   ├── constants.py         # Extensions & sliding chunk width constraints
│   │   └── prompts.py           # Gemini rigid markdown system prompt contract
│   ├── db/
│   │   ├── chroma.py            # Local ChromaDB persistent client wrapper (app/vector_db)
│   │   ├── chat_store.py        # Thread-safe JSON chat sessions store (chats.json)
│   │   └── metadata_store.py    # Thread-safe JSON documents metadata store (documents.json)
│   ├── services/
│   │   ├── ai/
│   │   │   ├── gemini_service.py     # Gemini generative completions client
│   │   │   ├── embeddings_service.py # Local SentenceTransformers (all-MiniLM-L6-v2) singleton
│   │   │   └── rag_pipeline.py       # Unified chunking, indexing, semantic search, & citation mapping
│   │   ├── ocr/
│   │   │   ├── paddle_service.py     # CPU PaddleOCR engine wrapper (singleton loader)
│   │   │   ├── pdf_service.py        # PyMuPDF fast extractor & layout analyzer
│   │   │   └── image_service.py      # Image dimension validator ocr parser
│   │   ├── storage/
│   │   │   ├── file_service.py       # Disk file writer & delete helper
│   │   │   ├── folder_service.py     # Category folder service layer
│   │   │   └── upload_service.py     # Ingest orchestrator (save, ocr, rag index, metadata register)
│   │   └── chat/
│   │       ├── chat_service.py       # Session log appender service
│   │       ├── citation_service.py   # Citation sources page formatter service
│   │       └── memory_service.py     # Sliding chat history builder service
│   ├── uploads/                 # Scoped document files storage directory
│   ├── vector_db/               # ChromaDB index local databases directory
│   └── main.py                  # Core FastAPI startup app entrypoint
├── tests/
├── .env
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

---

## ⚡ Setup & Launch Instructions

### 1. Prerequisites Configuration
Ensure you have a Python virtual environment configured and active:
```bash
# Activate Virtual Environment (Windows)
venv\Scripts\activate
```

Install production dependencies:
```bash
pip install -r requirements.txt
```

### 2. Environment Variables Setup
Configure your Google Gemini API key inside `backend/.env`:
```env
GEMINI_API_KEY=AIzaSy...your_gemini_key
```

### 3. Server Startup
Start the FastAPI server from your `backend/` directory:
```bash
..\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

*   **API Root URL**: `http://127.0.0.1:8000/`
*   **FastAPI Swagger Docs**: `http://127.0.0.1:8000/docs`

---

## 🧠 Advanced Ingestion & RAG Engineering Techniques (कौन-कौन सी Techniques Use की गई हैं)

KnowDoc Backend deviates from basic, slow RAG frameworks by implementing premium production-grade strategies:

### 1. Asynchronous Ingestion & Document Progress Polling (`FastAPI BackgroundTasks`)
*   **Problem**: In basic RAG pipelines, uploading a document freezes the thread while OCR and vector database indexing execute. This leads to frontend network timeouts and poor UX.
*   **Technique**: Asynchronous Background Task Orchestration. When a file is uploaded, the backend instantly returns a `200 Success` envelope with status `uploading` and persists the record to `documents.json`.
*   **Asynchronous Stages**: The backend queues the processing job inside a thread pool using FastAPI `BackgroundTasks`. The status transitions dynamically through:
    `uploading` ➔ `processing` (text extraction) ➔ `indexing` (ChromaDB vectorization) ➔ `completed` or `failed`.
*   **Result**: The frontend receives a sub-100ms response, permitting smooth user interaction while background threads process heavy PDF scanning.

### 2. Digital PDF Ingestion Bypass (`PyMuPDF / fitz` 0.2s Speed Bypass)
*   **Problem**: OCR is extremely CPU-bound and slow. Running OCR for pure-text digital PDFs wastes massive server compute and introduces 20-30s ingestion latencies.
*   **Technique**: Smart PDF Text Layer Inspection.
    - If the input PDF contains searchable text, the engine executes native text layer extraction using PyMuPDF (`fitz`) in **under 0.2 seconds**, completely skipping the OCR engine.
    - CPU-bound **PaddleOCR** executes strictly as a fallback for scanned PDFs, handwriting, or image-based files with zero selectable characters.

### 3. MD5 Document Checksum Deduplication Cache
*   **Problem**: Users frequently upload identical documents multiple times, causing redundant CPU processing, duplication of embeddings, and vector db bloat.
*   **Technique**: MD5 Ingestion Cache.
    - Before starting any ingestion, the backend pre-computes an MD5 checksum of the uploaded file byte array.
    - If a matching checksum is found in `backend/app/db/data/processed/{hash}.json`, the server skips PyMuPDF extraction, PaddleOCR, and embedding generation entirely. It directly registers the document's cached layout coordinates and metadata in `<1ms`.

### 4. Layout-Aware Scaling (Unified 1000x1000 Canvas Grid)
*   **Problem**: Document pages have arbitrary dimensions (pixels, points, inches), causing visual annotation bounding boxes to misalign on different screen sizes.
*   **Technique**: Coordinate Standardization.
    - All extracted block coordinates `[x_min, y_min, x_max, y_max]` are scaled to a standard `1000x1000` grid for A4/Letter size documents.
    - This allows the frontend React visual canvas to overlay perfect, responsive highlight boxes over the document image regardless of the original resolution.

### 5. Semantic Vector Index & Threshold Filtering (ChromaDB + SentenceTransformers)
*   **Problem**: Querying high numbers of text chunks leads to context inflation, noisy prompts, and model hallucinations.
*   **Technique**: Production-Balanced RAG Chunking & Similarity Truncation.
    - Uses local `SentenceTransformer("all-MiniLM-L6-v2")` singleton service to generate dense vector embeddings.
    - Chunks visual layout lines using a precise size of `900 words` and `150 words` overlap. This large chunk design is specifically chosen over premature chunk over-optimization because it retains rich semantic context, allowing Gemini to formulate complete, accurate answers.
    - Vector database retrieval searches ChromaDB restricted strictly to `n_results=5` chunks (`top_k = 5`).
    - Applies a mathematically balanced L2 similarity distance threshold filter of `< 1.65`. Chunks matching outside this threshold are completely discarded, ensuring only mathematically close contexts reach the generator.

### 6. Dynamic RAG Prompt Contract & Gemini Response Post-Processing
*   **Problem**: LLMs frequently hallucinate sources, cite documents they did not extract context from, or ignore system formatting requests.
*   **Technique**: Rigid System Prompt Contract & Backend Post-Processing.
    - Enforces a high-end system prompt contract instructing Gemini to strictly output rich markdown (hierarchical headings, tabular grids, bullet points) and index accurate visual inline bracket citations in the format `[Doc X, Page Y]`.
    - **Backend Post-Processor**: Prior to returning the final JSON reply, the backend parses the Gemini text, matches the matched citations, and strips out any unused document reference metadata. Only files actually cited in the text are returned inside the dynamic sources list.

### 7. Conversational Sliding Memory Window
*   **Problem**: Carrying endless chat history chains exhausts token quotas and slows down response latencies.
*   **Technique**: Memory Window Constraint.
    - Implements a sliding window memory manager that dynamically structures only the **last 6 messages** as contextual memory for the Gemini conversational prompt, preserving natural dialogue flow while optimizing bandwidth.

### 8. Thread-Safe Local JSON Store
*   **Problem**: Storing metadata in-memory results in complete data loss upon server restart or browser refresh.
*   **Technique**: Persistent Thread-Safe Local Databases.
    - Uses local JSON files (`documents.json`, `chats.json`, `folders.json`) under thread-safe file-locking read/write methods (`_lock = threading.Lock()`) for lightning-fast transactional persistence.

### 9. Lazy Loading + Singleton Cache (AI Model Management)
*   **Problem**: Eager model initialization during FastAPI server boot consumes massive CPU/RAM spikes, triggering Railway healthcheck timeouts and deployment crashes.
*   **Technique**: On-Demand Singleton Model Loading.
    - Deferred model loading has been fully decoupled from uvicorn's import phase.
    - CPU PaddleOCR, local SentenceTransformers, and Gemini generative configurations are completely lazy-loaded only when their respective action endpoints are first triggered by client uploads or chats.
    - Once loaded, instances are cached in-memory as singletons for all subsequent operations, ensuring high scalability and sub-second container starts.

---

## ⚡ Developer Execution Logs & Verification Metrics
To log system health and track scaling metrics, the backend outputs clean operational reports in terminal logs:
- `METRIC: OCR/Extraction time for {filename}: {duration} seconds`
- `METRIC: Embedding generation time for {filename} ({chunks} chunks): {duration} seconds`
- `METRIC: ChromaDB Indexing time for {filename}: {duration} seconds`
- `METRIC: Total background task duration for {filename}: {duration} seconds (SUCCESS)`
- `METRIC: Cache lookup duration for {filename}: {duration} seconds`
