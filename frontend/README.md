# 🟢 KnowDoc | Enterprise AI Document Intelligence Frontend

Welcome to the frontend repository of **KnowDoc**. This repository houses a high-fidelity, premium AI-powered document intelligence workspace built with **Next.js** using standard ES6+ Javascript and pure Vanilla CSS. The workspace integrates directly with the production-grade FastAPI backend, providing real-time smart citations, visual annotation bounding boxes, and dynamic persistent chats.

---

## 🎨 Branding & Visual Identity

KnowDoc is built upon a highly curated, premium visual identity designed to convey precision, intelligence, and modern sophistication. 

### 🎨 Brand Color Palette

We do not use generic colors. The design leverages a balanced, harmonious, and highly customized set of design tokens defined in [variables.css](file:///c:/Users/Lenovo/Desktop/KnowDoc/frontend/styles/variables.css):

| CSS Variable | Color Token | Hex Code | Visual Swatch | Semantic Usage |
| :--- | :--- | :--- | :--- | :--- |
| `--champagne-mist` | Primary Background | `#F3E7D3` | `█` (Beige Neutral) | Smooth backdrop, soft canvas, background color of the workspace and landing page. |
| `--emerald-tide` | Primary Color | `#0F6A5B` | `█` (Deep Forest Teal) | Major buttons, headers, branding elements, focus rings, active tabs. |
| `--accent-orange` | Highlight/CTA Accent | `#D95B24` | `█` (Sunset Vermillion) | Interactive states, upload zones, stats highlight, active scanning animations. |
| `--premium-black` | Core Typography | `#111111` | `█` (Obsidian Dark) | Primary text content, sidebars, premium card boundaries, and dark typography. |
| `--sidebar-bg` | Sidebar Canvas | `#EADBC8` | `█` (Warm Sand) | Left side navigation and file history background panel. |
| `--card-bg` | Glassmorphic Cards | `rgba(255, 255, 255, 0.40)` | Transparent Light Blur | Glassmorphism panels, dialog backgrounds, features, chat area backgrounds. |
| `--border-color` | Soft Borders | `rgba(15, 106, 91, 0.15)` | Transparent Teal | Clean card boundaries, subtle separators. |

---

## 💻 Tech Stack & Language Architecture

KnowDoc's frontend is strictly engineered using high-performance, future-proof modern standards:

*   **Core Framework**: **Next.js 16.x** utilizing the standard **App Router** structure.
*   **Languages**: Strict **Modern JavaScript (ES6+)** utilizing `.js` and `.jsx` extensions.
*   **Markdown Parsing**: **ReactMarkdown** with **remark-gfm** for parsing standard structured grids, tables, and lists dynamically.
*   **Styling Engine**: **Vanilla CSS Modules** (`*.module.css`) paired with a global variables cascading CSS system. Avoids utility Tailwind bloat inside high-fidelity UI components.
*   **Animations**: Advanced CSS keyframes supporting floating glowing orbs, sliding drawers, laser visual scanner sweeps, and pulse spinners.

---

## 📂 File Representation & Component Hierarchy

The directory is modularized under the principle of **"One component, one responsibility."**

```
frontend/
├── app/
│   ├── globals.css                # Global stylesheet Entry Point (chained imports)
│   ├── layout.js                  # Root Next.js layout (Plus Jakarta Sans configuration & SEO)
│   ├── page.js                    # Landing page (combines premium landing sections & ambient orbs)
│   └── workspace/
│       └── page.js                # 3-Pane workspace page (Chat Area | Doc Viewer | Sidebar coordination)
│
├── components/
│   ├── landing/                   # ── Landing Page Components ──
│   │   ├── CTASection/
│   │   │   ├── CTASection.jsx     # Branded glassmorphic call-to-action block
│   │   │   └── CTASection.module.css
│   │   ├── Features/
│   │   │   ├── Features.jsx       # 3-column key feature grid (High OCR Speed, Intelligent Chat, Layout Canvas)
│   │   │   └── Features.module.css
│   │   ├── Hero/
│   │   │   ├── Hero.jsx           # Branded Hero text grid, CTA buttons, metrics dashboard
│   │   │   └── Hero.module.css
│   │   ├── Navbar/
│   │   │   ├── Navbar.jsx         # Header navbar with sticky scrolling, logo assets, backend health check
│   │   │   └── Navbar.module.css
│   │   └── OCRPreview/
│   │       ├── OCRPreview.jsx     # Immersive, interactive PaddleOCR text extraction preview scanner
│   │       └── OCRPreview.module.css
│   │
│   ├── layout/                    # ── Structural Primitives ──
│   │   ├── Container/
│   │   │   ├── Container.jsx      # Flex layout wrapper matching 1400px width limit & 32px standard margins
│   │   │   └── Container.module.css
│   │   └── Section/
│   │       ├── Section.jsx        # Semantic HTML section wrapper with configurable padding systems
│   │       └── Section.module.css
│   │
│   ├── ui/                        # ── Shared Atomic UI Primitives ──
│   │   ├── Badge/
│   │   │   ├── Badge.jsx          # Reusable citation badges, backend health indicators, and score chips
│   │   │   └── Badge.module.css
│   │   └── Button/
│   │       ├── Button.jsx         # Custom rounded premium buttons (primary, secondary, icon styles)
│   │       └── Button.module.css
│   │
│   └── workspace/                 # ── Core Workspace Dashboard ──
│       ├── Chat/
│       │   ├── ChatArea.jsx       # Chat area, handles streaming user questions and active uploads
│       │   ├── ChatInput.jsx      # Prompt textarea input form with upload trigger
│       │   ├── MessageBubble.jsx  # Customized ReactMarkdown renderer with citation superscript links
│       │   ├── MessageList.jsx    # Chronological thread of bubbles with scroll locks and initial suggestion prompts
│       │   └── Chat.module.css
│       ├── Sidebar/
│       │   ├── ChatList.jsx       # List of active persistent chat sessions from chats.json
│       │   ├── DocumentList.jsx   # List of loaded documents with active processing loader filters
│       │   ├── Sidebar.jsx        # Coordination panel (file imports, catalog controls, category lists)
│       │   ├── UploadDropzone.jsx # Drag & drop upload area with glowing alerts
│       │   └── Sidebar.module.css
│       └── Viewer/
│           ├── DocViewer.jsx      # Workspace Inspector presentation tabs (Visual Canvas vs. Raw OCR blocks)
│           ├── OCRCanvas.jsx      # Responsive SVG canvas drawing bounding box highlights over document images
│           ├── RawTextList.jsx    # Chronological extracted block rows with individual conf-score badges
│           ├── ViewerDrawer.jsx   # Sidebar slider detail overlay presenting coordinates of selected blocks
│           └── Viewer.module.css
│
├── lib/
│   └── api.js                     # API Client (upload, fetchDocuments, fetchChats, streamAIChatResponse)
│
├── styles/                        # ── Layered Core Design Tokens ──
│   ├── reset.css                  # Absolute browser normalize and custom scrollbar resets
│   ├── variables.css              # Color palette configurations
│   ├── typography.css             # Monospace blocks and fluid header weights
│   ├── spacing.css                # Stack and row spacing utils
│   ├── animations.css             # Laser scanner keyframes and glowing transitions
│   └── utilities.css              # Custom glassmorphic blur filters
│
└── public/
    ├── logo_symbol.png            # Branded graphic mark (used in headers and sidebars)
    └── Title.png                  # Typographic logo wordmark (used strictly in Landing Hero)
```

---

## ⚡ Client Features & Frontend Techniques (कौन-कौन सी Techniques Use की गई हैं)

KnowDoc's frontend coordinates workspace states using state-of-the-art client-side techniques:

### 1. Browser Session UUID Sync & Synced CRUD Chat State
*   **Technique**: Browser UUID Synchronization.
*   **How it works**:
    - Upon workspace mounting, a browser-specific `session_id` is created or loaded from `localStorage`.
    - Active chats are fetched dynamically using the API call `fetchChats(sessionId)`.
    - If no chats exist for the browser, `createChat` automatically instantiates a thread on the backend.
    - All CRUD triggers (creating threads, deleting chats, switching conversations) are routed directly to backend REST endpoints and kept locally in React states.
*   **Result**: Flawless conversation persistence. Refreshing the browser or restarting the backend server restores all active chats and messages with zero data loss.

### 2. Real-Time Ingest Status Polling & UI Interaction Locks
*   **Technique**: Dynamic Status Polling & Action Shielding.
*   **How it works**:
    - When a document is uploaded, it is registered with status `uploading`.
    - The client initiates an active polling `setInterval` (checking `GET /api/documents` every 2 seconds) **only** if there are documents in progress states (`uploading`, `processing`, or `indexing`).
    - During these active progress states:
        - A glowing loader displays live progress in the sidebar and document grid catalog.
        - Click triggers on active documents are locked, preventing inspection queries or rendering crashes until indexing is `completed`.
    - Once all documents reach finalized states (`completed` or `failed`), the client clears the polling interval cleanly to preserve network bandwidth.

### 3. Markdown-Rich Responses with ReactMarkdown + GFM
*   **Technique**: Standardized AST Rendering.
*   **How it works**:
    - Discards simple string splits in message bubbles.
    - Renders text blocks through `<ReactMarkdown>` using `remark-gfm`.
    - Configured customized style component overrides for lists, headers, paragraphs, and tables, ensuring complex structured grids and document comparisons render with pixel-perfect premium typography.

### 4. Clickable Inline Citation Superscripts & Canvas Focus Jumps
*   **Technique**: Custom URL Scheme Mapping & Event Propagation.
*   **How it works**:
    - Prior to rendering, a regex converter parses message replies, identifying bracket sequences like `[Doc X, Page Y]` and converting them to standard markdown URL links with custom scheme syntax `[[Doc X, Page Y]](cite://X/Y)`.
    - `ReactMarkdown`'s anchor component component renderer is overridden:
        - If `href` matches `cite://X/Y`, the click event is hijacked to invoke `onSelectCitation(docIdx, pageIdx)`.
        - It displays a sleek sunset superscript: `<sup>[Doc X, Page Y]</sup>`.
        - Clicking the superscript triggers the responsive workspace visual inspect drawer to slide open on the right, switches the tab directly to the correct PDF canvas page, and flashes a highlighted orange rectangle over the cited text block location.

---

## 🚀 Getting Started & Local Development

Launch local builds easily using these commands:

### 1. Requirements Installation
Ensure all node modules are properly installed:
```bash
npm install
```

### 2. Start Next.js Development Server
Start the client server with high-performance compiler Turbopack enabled:
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) inside your web browser.

### 3. Production Compilation Validation
Check for any modular CSS errors or build compilation alerts:
```bash
npm run build
```
This builds optimized statically served bundles.
