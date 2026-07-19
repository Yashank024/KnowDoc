# 🛡️ Security, Concurrency & Sandboxing - KnowDoc

This document outlines the security controls, concurrency safeguards, and storage sandboxing architectures integrated into the **KnowDoc Document Intelligence Workspace**.

---

## 🔒 1. Backend Thread-Safety & File-Lock Concurrency

### ⚠️ Concurrency Challenges in JSON Databases
To bypass premature relational database overhead, KnowDoc utilizes flat local JSON files (`documents.json`, `chats.json`, `folders.json`) for configuration and state logging. In multi-user or rapid-upload scenarios, concurrent read/write requests can trigger race conditions, resulting in file truncation or document corruption.

### 🛡️ Implementation of Safe Mutex Locks
To resolve concurrency conflicts, the backend implements thread-safe file access handlers using Python's native `threading.Lock()` mutex locks inside `ChatStore` and `MetadataStore` layers:

```python
import os
import json
import threading

class MetadataStore:
    _lock = threading.Lock()  # Shared class-level mutex lock

    def _read_json(self):
        with self._lock:  # Safeguards the open/read block
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return []

    def _write_json(self, data):
        with self._lock:  # Safeguards the open/write block
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
```

### ⚡ Technical Benefits
*   **Zero File Corruption**: Ensures database transactional operations (such as registering a newly completed background OCR document or updating chat messages) execute sequentially, preventing interleaving writes.
*   **Low Complexity**: Provides robust concurrency locks without the overhead of heavy enterprise SQL servers.

---

## 🌐 2. Cross-Origin Resource Sharing (CORS) Security

### Scope of Integration
Because the **Next.js frontend** (`http://localhost:3000`) and the **FastAPI backend** (`http://127.0.0.1:8000`) operate on different ports, the browser's **Same-Origin Policy** restricts network requests.

### CORS Middleware Settings
The backend configures cross-origin policies inside `backend/app/main.py`, restricting permitted communication pipelines to specific trusted dev hosts:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+|[a-zA-Z0-9-]+\.vercel\.app)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### ⚡ Technical Benefits
*   **Production Deployment Integration**: Automatically allows access from the production client `https://knowdoc.vercel.app` as well as any branch previews or custom deployment links on Vercel (`*.vercel.app`).
*   **Flexible Local Subnet Testing**: Supports loopback interfaces (`localhost`, `127.0.0.1`) and local private subnets (`10.x.x.x`, `192.168.x.x`, `172.x.x.x`) to enable easy LAN-based paired debugging.

---

## 💻 3. Client Storage Sandboxing

### localStorage Isolation
The frontend isolates persistent workspace profiles using local sandboxed keys inside the browser's `localStorage` namespace:
- `session_id`: Houses the unique, persistent browser UUID. This key acts as the query separator (`session_id={uuid}`) for retrieval endpoints.
- `active_chat_{session_id}`: Persists the active chat tab selection, restoring conversation layout frames on refresh.

### Protection Vector
By utilizing standard client-side state hooks combined with local storage, no sensitive authorization tokens or browser cookies are stored or exposed to external origins.

---

## 🗄️ 4. File Storage Scoping & Sanitation

### Path Traversal Guardrails
When documents are saved or deleted via `uploads/` disk directories, the server validates extension constraints and purges standard relative path indicators (`../`, `..\`) to secure the filesystem:

*   **Extensions Allowed**: Strictly checks uploaded extensions against a permitted whitelist `['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.pdf']`.
*   **Sanitized File Names**: Filenames are sanitized, preventing arbitrary path injections from writing files outside the designated `uploads/` workspace path.

---

## ⏱️ 5. API Throttling & Rate Limiting (DOS Mitigation)

To prevent brute force queries and API billing spikes on our OpenRouter account, the backend implements an in-memory sliding window `RateLimiterMiddleware` inside `backend/app/main.py`.

*   **Rate Limit Threshold**: 60 requests per minute per IP address.
*   **Target Scope**: Applies strictly to `/api` routes (e.g. chat, uploads, documents), bypassing root diagnostic endpoints and Next.js static asset requests.
*   **Behavior**: When a client exceeds the threshold, the middleware intercepts the pipeline and returns HTTP Status Code `429 Too Many Requests` with a plain text warning: `"Rate limit exceeded. Please try again in a minute."`.

---

## 🛡️ 6. Security Headers & Content Security Policy (CSP)

To mitigate clickjacking, MIME-type sniffing, and cross-site scripting vulnerabilities, the custom `SecurityHeadersMiddleware` appends hardened HTTP response headers on every response:

*   `X-Frame-Options: DENY`: Prevents the site from being rendered inside an iframe, blocking clickjacking attacks.
*   `X-Content-Type-Options: nosniff`: Prevents MIME-type sniffing vulnerabilities.
*   `X-XSS-Protection: 1; mode=block`: Instructs modern web browsers to block any detected reflective XSS script injections.
*   `Referrer-Policy: strict-origin-when-cross-origin`: Restricts referrer information sent with outbound link navigations.
*   `Content-Security-Policy (CSP)`: Enforces a strict default-src policy:
    - `default-src 'self'`: Restricts loading styles and frames strictly to our domain.
    - `connect-src 'self' *`: Permits API backend connections and browser hot module reloading (HMR) during dev cycles.
    - `frame-ancestors 'none'`: Excludes iframe frame mounting globally.

---

## 🔗 7. Frontend DOM XSS link sanitizers

Markdown links rendered dynamically inside conversation threads can be hijacked to execute cross-site scripting (DOM XSS) using schemas like `javascript:evil_code()`. 

To prevent this, the custom `a` link tag renderer inside [MessageBubble.jsx](file:///c:/Users/Lenovo/Desktop/KnowDoc/frontend/components/workspace/Chat/MessageBubble.jsx) runs strict sanitization audits:
- **Whitelisted Protocols**: Only URLs starting with `http://`, `https://`, `mailto:`, `tel:`, or our custom `cite://` scheme are allowed.
- **Unsafe Protocols**: Links containing other protocols (such as `javascript:` or `data:`) are dynamically neutralized to `safeHref = "#"` and their click handler triggers are disabled via `e.preventDefault()`, completely blocking link-based injection vectors.

---

## 🔒 8. GitIgnore Database Exposure Protections

Local JSON database stores containing private logs (`chats.json`, `documents.json`, `folders.json`) are explicitly excluded from git indexing inside `backend/.gitignore`:

```text
# Exclude database files containing sensitive user chats and metadata
app/db/data/chats.json
app/db/data/documents.json
app/db/data/folders.json
```
This ensures private conversations and layout OCR extractions are never committed or exposed to public repositories.
