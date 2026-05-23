# 🏛️ System Architecture - KnowDoc Platform

KnowDoc represents a production-grade **Retrieval-Augmented Generation (RAG)** system designed for visual document auditing. It optimizes document ingestion throughput and semantic alignment using the pipeline detailed below.

---

## 📐 Ingestion & Conversation Pipeline

The diagram below maps the absolute sequential flow of a file uploaded by the client through the ingestion validation, asynchronous extraction, vector indexing, conversational reasoning, and visual coordinate highlight rendering phases:

```mermaid
flowchart TD
    %% Styling
    classDef client fill:#f9f6f0,stroke:#0f6a5b,stroke-width:2px;
    classDef server fill:#e2efe0,stroke:#0f6a5b,stroke-width:2px;
    classDef db fill:#fad9c1,stroke:#d95b24,stroke-width:2px;
    
    %% Client Upload Trigger
    subgraph Client [Next.js Client]
        A["1. User Uploads File (Drag & Drop)"]:::client
        B["2. Instantly Receives Success (Status: 'uploading')"]:::client
        C["3. Polling Active Status Interval (2s)"]:::client
        P1["Visual OCR Highlights (1000x1000 BBoxes)"]:::client
    end

    %% Ingestion Routing
    subgraph Ingestion [FastAPI Ingest Layer]
        D["4. MD5 Byte Checksum Generation"]:::server
        E{"5. Checksum in processed/ hash.json?"}:::server
        F["6. INSTANT cache match (Bypass OCR)"]:::server
        G["7. Asynchronous Thread Queue (FastAPI BackgroundTasks)"]:::server
    end

    %% Async Background Thread
    subgraph AsyncPipeline [Background Ingest Task Pipeline]
        H{"8. File Extension & Text Check"}:::server
        I["9. PyMuPDF (fitz) Direct Text Extraction (0.2s Bypass)"]:::server
        J["10. CPU-bound PaddleOCR (Scanned Files)"]:::server
        K["11. Standardize Coordinates to 1000x1000 A4 Canvas Grid"]:::server
        L["12. Generate Embeddings (SentenceTransformers all-MiniLM-L6-v2)"]:::db
        M["13. Insert vectors & metadata into ChromaDB persistent database"]:::db
        N["14. Register Status 'completed' inside documents.json"]:::db
    end

    %% Conversational RAG Loop
    subgraph ConversationalRAG [Conversational RAG Pipeline]
        Query["User Prompt Context"]:::client
        Classify{"Local Two-Layer Query Classifier"}:::server
        Greetings["Conversational Response (hello, thanks, help)"]:::server
        Retrieval["ChromaDB Vector Semantic Query (n_results=3, similarity < 1.25)"]:::db
        MemWindow["Sliding Memory Window (Last 6 chat turns)"]:::server
        GeminiContract["Google Gemini 2.5 Flash Markdown Prompt Contract"]:::server
        CitationParser["Backend Citation Matcher & Metadata Truncator"]:::server
    end

    %% Flow Connections
    A --> D
    D --> E
    E -- Yes --> F
    E -- No --> G
    G --> H
    H -- Digital PDF --> I
    H -- Scanned/Image --> J
    I --> K
    J --> K
    K --> L
    L --> M
    M --> N
    N -->|State Synced| C
    
    %% RAG Connections
    Query --> Classify
    Classify -- Match Simple Greetings --> Greetings
    Classify -- Match Document Queries --> Retrieval
    Retrieval --> MemWindow
    MemWindow --> GeminiContract
    GeminiContract --> CitationParser
    CitationParser -->|Rendered Markdown + cite:// scheme| P1
```

---

## 🦾 Core Architectural Techniques & Benefits

### 1. Ultra-Fast Ingestion Response (Background Execution)
*   **Technique**: When a user drops a file, it is saved to storage and registered inside `documents.json` with state `"uploading"`. The server instantly replies `200 OK` to the React client.
*   **Benefit**: The frontend transitions to a loading state and displays dynamic progress animations, preventing browser timeout blocks during heavy extraction jobs.

### 2. Digital PDF Native Extraction Bypass
*   **Technique**: A regular PDF has characters mapped in layout positions. PyMuPDF (`fitz`) extracts the text layer directly.
*   **Benefit**: Ingestion finishes in **0.2 seconds** instead of the typical 20 seconds needed for heavy visual OCR models, reducing processing load on standard CPUs.

### 3. MD5 Duplicate Document Checksum Deduplication
*   **Technique**: Before starting extraction, the server generates an MD5 checksum of the binary array. If this checksum file path (`backend/app/db/data/processed/{hash}.json`) exists, extraction, chunking, and embedding generation are skipped.
*   **Benefit**: High-speed, sub-millisecond duplicate checks prevent database redundancy.

### 4. Layout Standardizing (1000x1000 Canvas Coordinate Grid)
*   **Technique**: Normalizes page widths and heights to standard coordinate ranges `[0-1000]`.
*   **Benefit**: The frontend visual inspector overlay accurately matches PDF elements with CSS highlight rectangles across responsive screen dimensions.

### 5. Vector Index & Distance Truncation
*   **Technique**: Chunks text blocks using overlapping sliders, vectorizes context using a local `SentenceTransformer("all-MiniLM-L6-v2")` model, and checks distance inside a ChromaDB collection (`backend/app/vector_db`).
*   **Constraints**:
    - Limits retrieve queries to `n_results=3` chunks.
    - Rejects contexts with an L2 vector distance `>= 1.25`.

### 6. RAG Chat Session Storage & Response Parsing
*   **Technique**: Keeps browser session data synced using UUID keys in standard `localStorage`. Synchronizes conversations directly through persistent CRUD chat endpoints to `chats.json`.
*   **Post-Processing Citation Scheme**: Gemini output references `[Doc X, Page Y]`, which the frontend converts into markdown anchors pointing to a custom URL scheme `cite://X/Y` to enable interactive highlight focus.
