# 🟢 KnowDoc | AI Document Intelligence Workspace

An enterprise-ready, premium **RAG (Retrieval-Augmented Generation)** document intelligence platform. KnowDoc dynamically ingests mixed selectable/scanned PDFs and images, standardizes irregular visual layout coordinates onto uniform virtual canvas grids, indexes semantic vectors using lightweight local embeddings, and delivers an interactive conversational workspace with persistent session-synced chats and clickable visual citations.

---

## 📐 Unified Enterprise Architecture Mapping (System Execution Flow)

```
  [ Next.js Client Interface ]
               │
               ▼  (1. Drag-and-Drop File Upload)
  [ FastAPI Ingest API Gateway ] ────► (2. Immediate 200 OK Status: 'uploading')
               │
               ├─► [ MD5 Cache Check ] ─── (Hit) ───► [ Load Cached Coordinates ]
               │                                                 │
               ▼ (Miss)                                          ▼
  [ Asynchronous Background Tasks ] ────────────────────► [ Frontend Progress ]
               │                                        (Live status polling)
               ├─► [ Searchable Text Check ] 
               │          ├─► Digital: [ PyMuPDF Extract ] (0.2s Bypass)
               │          └─► Scanned: [ CPU PaddleOCR ] (Fallback Engine)
               │
               ▼  (3. Normalize to 1000x1000 Grid)
  [ Layout-Aware Chunker ] (900 words, 150 overlap)
               │
               ▼  (4. Vectorize text blocks)
  [ SentenceTransformer Engine ] (all-MiniLM-L6-v2)
               │
               ▼  (5. Index Dense Embeddings)
  [ ChromaDB Local Vector Store ] ◄──────────────────────► [ Active Document Delete ]
               │                                         (Cascaded collection prune)
               │
               ▼  (6. Query Semantic Matching: top_k=5, L2 < 1.65)
  [ RAG Processing Pipeline ] ──► [ Sliding Memory Window ] (Last 6 turns)
               │
               ▼  (7. Generative Context Reasoning)
  [ Google Gemini 2.5 API ] (Under Markdown Citation Contract)
               │
               ▼  (8. Render Interactive Highlights)
  [ Clickable Citations on React Canvas ] ◄─── (Matches cite:// anchor scheme)
```

---

## 📂 Subfolder README Modules

KnowDoc is cleanly decoupled into two independent, highly structured sub-systems. For detailed logic directories, package configurations, API definitions, and folder structures, consult their respective subfolder documentation:

*   🦾 **Backend Sub-System**: [backend/README.md](backend/README.md) – FastAPI backend routing, CPU PaddleOCR engine setups, metadata thread-safety, and SQLite ChromaDB integrations.
*   💻 **Frontend Sub-System**: [frontend/README.md](frontend/README.md) – Next.js Client Workspace layouts, standard CSS variables layer architecture, dynamic polling hook implementations, and markdown citation renderers.

---

## 🛠️ Complete Component Blueprint (File-by-File Mappings)

### 1. 🧠 Core AI & Semantic Processing Services
*   [rag_pipeline.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/services/ai/rag_pipeline.py): The core system orchestrator. Computes semantic search vectors, queries ChromaDB with threshold bounds, compiles the prompt block bounded at `12,000` characters, restricts context with a sliding conversation window (last 6 messages), queries Gemini under a markdown contract, and filters cited sources.
*   [embeddings_service.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/services/ai/embeddings_service.py): Generates dense 384-dimensional text vectors. Implements a lazy-loading SentenceTransformers wrapper loaded with the local `all-MiniLM-L6-v2` CPU-optimized model, falling back to Google Generative AI embeddings if local loading fails.
*   [gemini_service.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/services/ai/gemini_service.py): Configures the Google Gemini API client connection. Implements dynamic lazy-loaded completions using the fast `gemini-2.5-flash` model, enforcing structured and rigid markdown replies.
*   [chunking.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/utils/chunking.py): Contains document split algorithms. Standardizes paragraph and visual layout OCR lines into overlapping segments of exactly `chunk_size = 900` words with a sliding `chunk_overlap = 150` words to retain comprehensive semantic context.

### 2. 🦾 Layout OCR Parsing & Extraction Services
*   [paddle_service.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/services/ocr/paddle_service.py): Wraps the CPU-bound PaddleOCR engine. It initializes on the first scanned image upload trigger, performing multi-language visual text block segmentation and coordinate tracking.
*   [pdf_service.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/services/ocr/pdf_service.py): The primary PDF extraction gateway. Natively parses searchable digital text layers page-by-page in under `0.2 seconds` using PyMuPDF (`fitz`), completely bypassing CPU-heavy PaddleOCR.
*   [image_service.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/services/ocr/image_service.py): Validates uploaded image ratios and coordinates prior to OCR block execution.

### 3. 🗄️ Storage Gateway & Ingest Services
*   [upload_service.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/services/storage/upload_service.py): Orchestrates raw file writes, generates MD5Checksum hashes to skip redundant processing, structures document metadata schemas, and dispatches long-running indexing pipelines asynchronously to `BackgroundTasks`.
*   [file_service.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/services/storage/file_service.py): Performs raw disk file writes and cascades deletions when documents are deleted.
*   [folder_service.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/services/storage/folder_service.py): Handles logical workspace folder groupings.

### 4. 💬 Chat memory & Citation Builders
*   [chat_service.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/services/chat/chat_service.py): Appends active query-reply logs directly to metadata databases.
*   [citation_service.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/services/chat/citation_service.py): Normalizes source filenames and page occurrences for frontend presentation.
*   [memory_service.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/services/chat/memory_service.py): Prunes long conversation threads into a clean sliding window of the last 6 turns.

### 5. 🔌 Routing Gateways (API Endpoints)
*   [chat.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/api/routes/chat.py): Directs chat sessions, processes queries, lists session logs, and executes persistent database chat thread renames.
*   [upload.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/api/routes/upload.py): Dispatches ingestion triggers for multipart file uploads.
*   [documents.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/api/routes/documents.py): Manages list catalogs and executes cascaded document deletion (pruning registries and deleting matching vector collections).
*   [folders.py](file:///c:/Users/Lenovo/Desktop/KnowDoc/backend/app/api/routes/folders.py): Configures workspace folders binds.

### 6. 💻 Frontend Components Layer
*   [page.js](file:///c:/Users/Lenovo/Desktop/KnowDoc/frontend/app/workspace/page.js): The Next.js workspace manager. Generates browser UUID session keys, coordinates drag-and-drop uploads, polls status progress bars, handles sidebar navigation, and manages chat input channels.
*   [MessageBubble.jsx](file:///c:/Users/Lenovo/Desktop/KnowDoc/frontend/components/MessageBubble.jsx): Renders markdown streaming text using `react-markdown` and `remark-gfm`. Intercepts system inline bracket citations `[Doc X, Page Y]` on-the-fly and overlays clickable citation badges.
*   [api.js](file:///c:/Users/Lenovo/Desktop/KnowDoc/frontend/lib/api.js): Manages axios-based server bindings for seamless, non-blocking asynchronous REST exchanges.

---

## 🗄️ Decoupled Data Architecture & File Mapping

KnowDoc avoids premature database complexity by mapping metadata schemas directly to persistent local stores protected by mutex locks (`threading.Lock()`). The database maps as follows:

```
KnowDoc Workspace Storage Layer
├── backend/app/
│   ├── db/data/
│   │   ├── documents.json   <── [Metadata Schema Registry] Registers document size, status, MD5 hash, paths.
│   │   ├── chats.json       <── [Chat Session Database] Syncs user-assistant conversations, session mappings.
│   │   ├── folders.json     <── [Folders Registry] Organizes custom workspaces categories.
│   │   └── processed/       <── [MD5 Extraction Cache] Pre-parsed JSON files named '{md5_hash}.json'.
│   │
│   └── vector_db/           <── [ChromaDB persistent store] Persistent SQLite collection ('chroma.sqlite3').
```

# 🚀 KnowDoc AI — Local Setup & Installation Guide

## 1. Clone the Repository

Download the complete project from GitHub using the following command:

```bash
git clone https://github.com/Yashank024/KnowDoc.git
```

---

## 2. Open the Project Folder

Navigate into the downloaded project directory:

```bash
cd KnowDoc
```

Open the project inside any IDE or code editor such as:

* VS Code
* PyCharm
* Cursor
* IntelliJ IDEA

---

# 💻 Frontend Setup (Next.js)

Open a terminal and navigate to the frontend directory:

```bash
cd frontend
```

---

## Install Frontend Dependencies

Install all required Node.js packages:

```bash
npm install
```

---

## Start Frontend Development Server

Run the Next.js frontend server:

```bash
npm run dev
```

Frontend will start at:

```bash
http://localhost:3000
```

Workspace URL:

```bash
http://localhost:3000/workspace
```

---

# 🦾 Backend Setup (FastAPI + OCR + RAG)

Open a second terminal and navigate to the backend directory:

```bash
cd backend
```

---

## Install Python 3.11.9

Recommended Python version:

```bash
Python 3.11.9
```

Download Python from:

```bash
https://www.python.org/downloads/release/python-3119/
```

---

## Create Virtual Environment

Create a Python virtual environment:

```bash
python -m venv venv
```

---

## Activate Virtual Environment

### Windows PowerShell

```bash
venv\Scripts\activate
```

---

## Install Backend Dependencies

Install all required backend libraries:

```bash
pip install -r requirements.txt
```

---

## Configure Gemini API Key

Create a `.env` file inside the `backend/` directory and add:

```env
GEMINI_API_KEY=your_gemini_api_key
```

---

## Start FastAPI Backend Server

Run the backend server using uvicorn:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend will start at:

```bash
http://127.0.0.1:8000
```

Swagger API Documentation:

```bash
http://127.0.0.1:8000/docs
```

---

# 🌐 Final Local Development Workflow

Run both servers simultaneously:

| Service      | URL                             |
| ------------ | ------------------------------- |
| Frontend     | http://localhost:3000           |
| Backend      | http://127.0.0.1:8000           |
| Workspace    | http://localhost:3000/workspace |
| Swagger Docs | http://127.0.0.1:8000/docs      |

---

# 📦 Production Deployment

| Service             | Platform |
| ------------------- | -------- |
| Frontend Deployment | Vercel   |
| Backend Deployment  | Railway  |
| Version Control     | GitHub   |
| Containerization    | Docker   |

---

# ⚠️ Important Notes

* Ensure Python `3.11.9` is installed before backend setup.
* Ensure Node.js and npm are installed before frontend setup.
* Backend OCR models load dynamically during first usage.
* Gemini API key is required for AI response generation.
* Keep both frontend and backend servers running simultaneously during local development.

---

# 🔗 Project Links

### GitHub Repository

https://github.com/Yashank024/KnowDoc.git

### Live Demo

https://knowdoc.vercel.app/

### Demo Video
https://drive.google.com/file/d/1zkwUhqDMrG_B--oI4CV4dLKv1DiHSVaS/view?usp=sharing

# 👨💻 Developed By

**Yashank Gupta**
*AI Architect & Full Stack Developer*

---

# 🚀 DEVELOPMENT JOURNEY, CHALLENGES & SYSTEM FLOW

The development of KnowDoc AI involved multiple stages of experimentation, architecture redesign, infrastructure debugging, OCR optimization, frontend restructuring, and deployment stabilization before evolving into a production-oriented AI document intelligence platform.

### 🔬 The DotsOCR Experimentation & Redesign
The project initially started with experimentation around the DotsOCR research model due to its advanced document parsing capabilities. However, during testing inside Google Colab, the model proved extremely resource intensive. GPU memory usage became unstable, RAM limitations were repeatedly exceeded, and inference latency became impractical for real-world workflows.

To solve this issue, the OCR architecture was redesigned completely and migrated to **PaddleOCR**, which provided significantly better CPU compatibility, faster execution speed, and deployment stability for scalable document processing workflows.

### 🦾 Environment & Dependency Challenges
After selecting PaddleOCR, several backend engineering challenges appeared including dependency conflicts, Python environment inconsistencies, OCR runtime instability, and package installation failures. These issues were resolved by rebuilding the environment architecture, isolating OCR testing pipelines, and restructuring dependency management systems.

### 💻 Frontend Architecture Decoupling
The frontend development phase introduced another major challenge. As features expanded rapidly, the UI architecture became unstructured due to duplicated components, conflicting CSS layers, and scattered state management logic. To stabilize the system, the frontend was redesigned using a modular component-driven architecture with dedicated responsibility-based workspace systems.

### 🌐 End-to-End Local & Cloud Deployment Stabilization
One of the most difficult engineering phases involved connecting the frontend and backend reliably across both local and production environments. Several deployment issues occurred including:
* CORS failures,
* incorrect API routing,
* environment variable mismatches,
* localhost production conflicts,
* Railway deployment instability,
* Vercel build failures,
* and backend connection breakdowns.

The deployment infrastructure was eventually stabilized using environment-based API configuration systems, Docker-based backend deployment, centralized API coordination layers, and optimized runtime initialization strategies.

### 🧠 Semantic Retrieval & Chunking Alignment
Another critical challenge involved semantic retrieval and vector chunking workflows. Multiple advanced chunking experiments initially degraded retrieval quality and caused irrelevant AI responses. The vector database had to be rebuilt completely after semantic retrieval alignment failed.

The architecture was simplified into overlapping sliding-window semantic chunking pipelines, which restored contextual retrieval accuracy and stabilized AI-generated responses.

---

## ⚡ Core Performance Optimizations

Several performance optimizations were implemented throughout development including:
* **Lazy-loaded OCR initialization** (deferred loading to prevent container cold starts)
* **Singleton AI model caching** (in-memory caching for sub-millisecond execution loops)
* **Asynchronous background ingestion** (FastAPI `BackgroundTasks` thread pool matching)
* **Semantic similarity filtering** (L2 cosine similarity pruning threshold checks)
* **Trigger-based Gemini execution** (dynamic completion logic under prompt contracts)
* **Deployment memory optimization** (lightweight modules replacing heavy dependencies)

---

## ⚙️ The Production Execution Pipeline

The final system architecture now operates through the following production workflow:

```
  [1. User Uploads File] ──► [2. Validate & Store File] ──► [3. Digital Text Inspect]
                                                                     │
                                             ┌───────────────────────┴───────────────────────┐
                                             ▼                                               ▼
                                  (Selectable PDF Bypass)                         (Scanned PDF/Image Scan)
                             [PyMuPDF Layer Extraction]                         [CPU PaddleOCR Pipeline]
                                             │                                               │
                                             └───────────────────────┬───────────────────────┘
                                                                     ▼
                                                      [4. Normalized 1000x1000 Grid]
                                                                     │
                                                                     ▼
                                                      [5. Layout-Aware Chunker]
                                                                     │
                                                                     ▼
                                                      [6. SentenceTransformers Embed]
                                                                     │
                                                                     ▼
                                                      [7. ChromaDB Dense Vector Store]
                                                                     │
                                                                     ▼
                                                      [8. Similarity Query Matches]
                                                                     │
                                                                     ▼
                                                      [9. Context-Aware Chunks to Gemini]
                                                                     │
                                                                     ▼
                                                      [10. Answering under Citation Contract]
                                                                     │
                                                                     ▼
                                                      [11. Interactive Canvas overlays]
```

1. Users upload PDFs or image-based documents
2. The backend validates and stores uploaded files
3. Digital PDFs bypass OCR using PyMuPDF extraction
4. Scanned files activate PaddleOCR extraction pipelines
5. Extracted text is cleaned and segmented into semantic chunks
6. SentenceTransformers generate vector embeddings
7. ChromaDB stores semantic document vectors
8. User queries trigger semantic similarity retrieval
9. Relevant contextual chunks are passed into Gemini AI
10. AI-generated responses are formatted with source citations
11. Citation references synchronize directly with frontend OCR visualization layers

The project evolved from an experimental prototype into a scalable AI-powered enterprise document intelligence platform capable of contextual document retrieval, semantic AI interaction, OCR visualization, persistent chat synchronization, and production-grade deployment workflows.