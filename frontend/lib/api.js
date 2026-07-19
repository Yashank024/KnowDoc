const getBaseUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof window === "undefined") {
    return "http://127.0.0.1:8000";
  }
  const hostname = window.location.hostname;
  if (
    hostname === "localhost" ||
    hostname === "127.0.0.1" ||
    hostname.startsWith("10.") ||
    hostname.startsWith("192.168.") ||
    hostname.startsWith("172.")
  ) {
    return `${window.location.protocol}//${hostname}:8000`;
  }
  return "https://knowdoc-backend.onrender.com";
};

const BASE_URL = getBaseUrl();

/**
 * Checks the operational health of the backend OCR API server.
 */
export async function checkBackendHealth() {
  try {
    const response = await fetch(`${BASE_URL}/api/health`);
    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.warn("Backend health check failed (offline/unreachable):", error.message);
    return { status: "offline", error: error.message };
  }
}

/**
 * Uploads a document/image file to the backend for PaddleOCR text extraction.
 * Tracks progress states via parent component callbacks.
 * 
 * @param {File} file - The file object to upload
 */
export async function uploadDocumentToOCR(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${BASE_URL}/api/ocr`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errPayload = await response.json().catch(() => ({ detail: "OCR extraction failed." }));
    // errPayload.detail may be a string (400/500) or an object (422 pipeline failure)
    console.error("[KnowDoc] Upload failed. Full error payload:", JSON.stringify(errPayload, null, 2));
    const detail = errPayload.detail;
    let errorMsg;
    if (typeof detail === "string") {
      errorMsg = detail;
    } else if (detail && typeof detail === "object") {
      // 422 pipeline failure: { indexing_failed, reason, pipeline_stopped_at, diagnostics }
      errorMsg = detail.reason
        || detail.pipeline_stopped_at
        || `Pipeline failed: ${JSON.stringify(detail)}`;
    } else {
      errorMsg = "Server error running PaddleOCR.";
    }
    throw new Error(errorMsg);
  }

  return await response.json();
}

/**
 * Fetches all indexed documents in local JSON metadata database.
 */
export async function fetchDocuments() {
  const response = await fetch(`${BASE_URL}/api/documents`);
  if (!response.ok) {
    throw new Error("Failed to fetch indexed documents list.");
  }
  return await response.json();
}

/**
 * Deletes a document by ID.
 * 
 * @param {string} docId - The ID of the document to delete
 */
export async function deleteDocument(docId) {
  const response = await fetch(`${BASE_URL}/api/documents/${docId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Failed to delete document from backend storage.");
  }
  return await response.json();
}

/**
 * Fetches all category folders in local JSON metadata database.
 */
export async function fetchFolders() {
  const response = await fetch(`${BASE_URL}/api/folders`);
  if (!response.ok) {
    throw new Error("Failed to fetch workspaces folders list.");
  }
  return await response.json();
}

/**
 * Connects directly to the live backend RAG chatbot pipeline.
 * It passes the user prompt and active documents to filter semantic contexts,
 * retrieves RAG citations, and streams the reply word-by-word.
 * 
 * @param {string} prompt - The user's query
 * @param {Array} documents - List of active documents in session
 * @param {Function} onChunk - Callback triggered on each text segment for streaming simulation
 */
/**
 * Fetches all persistent chat sessions linked to the browser sessionId.
 */
export async function fetchChats(sessionId) {
  const url = sessionId ? `${BASE_URL}/api/chats?session_id=${sessionId}` : `${BASE_URL}/api/chats`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Failed to fetch persistent chat threads.");
  }
  return await response.json();
}

/**
 * Creates a new persistent chat session thread on the backend.
 */
export async function createChat(sessionId, title = "Document Chat Session") {
  const response = await fetch(`${BASE_URL}/api/chats`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      session_id: sessionId,
      title
    })
  });
  if (!response.ok) {
    throw new Error("Failed to create new chat thread.");
  }
  return await response.json();
}

/**
 * Deletes a persistent chat session thread on the backend.
 */
export async function deleteChat(chatId) {
  const response = await fetch(`${BASE_URL}/api/chats/${chatId}`, {
    method: "DELETE"
  });
  if (!response.ok) {
    throw new Error("Failed to delete chat thread from persistence database.");
  }
  return await response.json();
}

/**
 * Renames a persistent chat session thread on the backend.
 */
export async function renameChat(chatId, newTitle) {
  const response = await fetch(`${BASE_URL}/api/chats/${chatId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      title: newTitle
    })
  });
  if (!response.ok) {
    throw new Error("Failed to rename chat thread in persistence database.");
  }
  return await response.json();
}

/**
 * Connects directly to the live backend RAG chatbot pipeline.
 * It passes the user prompt and active documents to filter semantic contexts,
 * retrieves RAG citations, and streams the reply word-by-word.
 * 
 * @param {string} prompt - The user's query
 * @param {Array} documents - List of active documents in session
 * @param {Array} history - List of previous chat messages
 * @param {string} chatId - The target persistent chat thread ID
 * @param {string} sessionId - The browser session ID
 * @param {Function} onChunk - Callback triggered on each text segment for streaming simulation
 */
export async function streamAIChatResponse(prompt, documents, history, chatId, sessionId, onChunk) {
  // Extract all active document IDs
  const docIds = (documents || []).map((doc) => doc.id);

  // Map history to ChatMessageSchema schema: { sender: 'user' | 'ai', text: string }
  const formattedHistory = (history || [])
    .filter((msg) => msg.text && !msg.isStreaming)
    .map((msg) => ({
      sender: msg.sender === "ai" ? "ai" : "user",
      text: msg.text
    }));

  logger_info(`RAG Request: Querying AI model for prompt length ${prompt.length}...`);

  const response = await fetch(`${BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      message: prompt,
      chat_id: chatId,
      session_id: sessionId,
      doc_ids: docIds,
      history: formattedHistory
    })
  });

  if (!response.ok) {
    const errPayload = await response.json().catch(() => ({ detail: "Generative AI response failed." }));
    throw new Error(errPayload.detail || "Server error running RAG OpenRouter Chat.");
  }

  const result = await response.json();
  const replyText = result.reply || "I am sorry, I couldn't formulate a response.";

  // Simulate premium streaming delivery of the real RAG response text
  const words = replyText.split(" ");
  let accumulatedText = "";

  for (const word of words) {
    accumulatedText += word + " ";
    onChunk(accumulatedText);
    // 30ms delay per word to give a fast, premium streaming feel
    await new Promise((resolve) => setTimeout(resolve, 30));
  }

  return result;
}

// Simple logging wrapper
function logger_info(msg) {
  console.log(`[API CLIENT] ${msg}`);
}

/**
 * Calls the backend reset-database endpoint to wipe all runtime data.
 */
export async function resetDatabase() {
  const response = await fetch(`${BASE_URL}/api/admin/reset-database`, {
    method: "POST"
  });
  if (!response.ok) {
    const errPayload = await response.json().catch(() => ({}));
    throw errPayload.detail || errPayload || { error: "Failed to reset database." };
  }
  return await response.json();
}

