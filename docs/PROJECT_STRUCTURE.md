# 📂 Project Structure Blueprint - KnowDoc

The directory structure below details the modular organization of both the Next.js frontend client codebase and the FastAPI backend engine:

---

## 💻 1. Frontend Component Structure (`frontend/`)

The Next.js client decouples presentation elements under strict folder conventions:

```
frontend/
├── app/
│   ├── globals.css                # Global stylesheet entry point (chained imports)
│   ├── layout.js                  # App base layout (fonts loading & page structure setup)
│   ├── page.js                    # Landing/Marketing presentation page
│   └── workspace/
│       └── page.js                # 3-Pane workspace orchestrator (Sidebar, Chat, Viewer)
├── components/
│   ├── landing/                   # ── Marketing landing elements ──
│   │   ├── CTASection/            # Call-To-Action grid card
│   │   ├── Features/              # 3-column benefit feature matrix
│   │   ├── Hero/                  # Responsive welcome banner & statistics dashboard
│   │   ├── Navbar/                # Sticky header & server health check indicators
│   │   └── OCRPreview/            # Interactive visual text scanner simulation
│   ├── layout/                    # ── Responsive CSS Flex wraps ──
│   │   ├── Container/             # Standardized 1400px page boundary limits
│   │   └── Section/               # Semantic block wrappers
│   ├── ui/                        # ── Atomic reusable UI items ──
│   │   ├── Badge/                 # Score chips, server checks, and citation numbers
│   │   └── Button/                # primary/secondary rounded components
│   └── workspace/                 # ── Workspace application elements ──
│       ├── Chat/
│       │   ├── ChatArea.jsx       # Coordinates active streams, suggestions, uploads
│       │   ├── ChatInput.jsx      # Message text area and file triggers
│       │   ├── MessageBubble.jsx  # ReactMarkdown parser & citation overrides
│       │   ├── MessageList.jsx    # message rendering list with auto-scroll
│       │   └── Chat.module.css    # Layout configurations
│       ├── Sidebar/
│       │   ├── ChatList.jsx       # Lists historic persistent active chat sessions
│       │   ├── DocumentList.jsx   # Lists uploads showing glowing task states
│       │   ├── Sidebar.jsx        # Co-ordinating panel shell
│       │   ├── UploadDropzone.jsx # Sunset Vermillion file drops trigger zone
│       │   └── Sidebar.module.css
│       └── Viewer/
│           ├── DocViewer.jsx      # Side visual inspect and raw coordinates tab selector
│           ├── OCRCanvas.jsx      # SVG drawing overlay projecting bounding boxes directly onto document images
│           ├── RawTextList.jsx    # Chronological extracted block rows with individual conf-score badges
│           ├── ViewerDrawer.jsx   # Sidebar slider detail overlay presenting coordinates of selected blocks
│           └── Viewer.module.css  # Inspector CSS modules
├── lib/
│   └── api.js                     # Central REST interface (checkHealth, streamAIChatResponse)
├── styles/                        # ── CSS Variables and Animations ──
│   ├── reset.css                  # Normalizer and fluid scrollbars
│   ├── variables.css              # Custom theme colors (Emerald, Orange, Warm Sand)
│   ├── typography.css             # Plus Jakarta Sans typography weights
│   ├── spacing.css                # Grid gaps, layout stack systems
│   ├── animations.css             # Scanner sweep lines and rotating spins
│   └── utilities.css              # Glass backdrops and glowing ambient orbs
└── public/
    ├── logo_symbol.png            # Branded graphic mark (used in headers and sidebars)
    └── Title.png                  # Typographic logo wordmark (used strictly in Landing Hero)
```

---

## 🦾 2. Backend Architecture Layout (`backend/`)

The FastAPI engine is structured cleanly according to service separations:

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
