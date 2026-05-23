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
    allow_origins=[
        "http://localhost:3000",      # Client dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"],
    allow_headers=["*"],
)
```

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
