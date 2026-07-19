"use client";

import { useState, useEffect } from "react";
import Sidebar     from "../../components/workspace/Sidebar/Sidebar";
import ChatArea    from "../../components/workspace/Chat/ChatArea";
import DocViewer   from "../../components/workspace/Viewer/DocViewer";
import DocExplorer from "../../components/workspace/Explorer/DocExplorer";
import SettingsModal from "../../components/workspace/SettingsModal";
import { fetchDocuments, deleteDocument, fetchChats, createChat, deleteChat, renameChat } from "../../lib/api";

export default function WorkspacePage() {
  // Global document list database - dynamic from backend
  const [documents, setDocuments] = useState([]);

  // Dynamic Workspace mode: "chat" or "explorer"
  const [viewMode, setViewMode] = useState("chat");

  // Drawer Slide-Over & Bounding Box Inspection Focus
  const [activeDoc, setActiveDoc] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  // Browser Session ID & Chats State Management
  const [sessionId, setSessionId] = useState(null);
  const [chats, setChats] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Fetch document list on component mount
  useEffect(() => {
    async function loadWorkspaceData() {
      try {
        const docList = await fetchDocuments();
        setDocuments(docList);
      } catch (err) {
        console.warn("FastAPI backend offline. Using local empty workspace.");
      }
    }
    loadWorkspaceData();
  }, []);

  // Real-time status polling interval for documents in active progress states
  useEffect(() => {
    const hasActiveProcessing = documents.some(
      (doc) => doc.status === "uploading" || doc.status === "processing" || doc.status === "indexing"
    );

    if (!hasActiveProcessing) return;

    console.log("[POLLING] Active processing documents found. Starting background status polling interval...");
    
    const intervalId = setInterval(async () => {
      try {
        const updatedDocList = await fetchDocuments();
        
        // Check if any document transitioned from processing to completed in this step
        documents.forEach((oldDoc) => {
          if (oldDoc.status === "processing") {
            const newDoc = updatedDocList.find((d) => d.id === oldDoc.id);
            if (newDoc && newDoc.status === "completed") {
              const successMsg = {
                id: `sys-${Date.now()}-${newDoc.id}`,
                sender: "ai",
                text: `Successfully processed and indexed document **${newDoc.filename}** globally via high-precision **PaddleOCR**! Total of **${newDoc.text_lines?.length || 0}** text blocks extracted.

You can now ask questions about the contents, or explore it inside the Visual Inspector!`,
                isStreaming: false
              };
              
              setChats((prevChats) =>
                prevChats.map((chat) =>
                  chat.id === activeChat
                    ? { ...chat, messages: [...chat.messages, successMsg] }
                    : chat
                )
              );
            }
          }
        });

        setDocuments(updatedDocList);

        // Sync activeDoc if it is currently processing and has updated
        if (activeDoc) {
          const matchingUpdated = updatedDocList.find((d) => d.id === activeDoc.id);
          if (matchingUpdated && (matchingUpdated.status !== activeDoc.status || matchingUpdated.text_lines?.length !== activeDoc.text_lines?.length)) {
            setActiveDoc(matchingUpdated);
          }
        }
      } catch (err) {
        console.warn("[POLLING] Background polling failed:", err.message);
      }
    }, 2000);

    return () => {
      console.log("[POLLING] Clearing background status polling interval.");
      clearInterval(intervalId);
    };
  }, [documents, activeDoc, activeChat]);



  useEffect(() => {
    if (typeof window !== "undefined" && window.innerWidth <= 768) {
      setIsSidebarCollapsed(true);
    }
  }, []);

  // Initialize/Retrieve Session ID from localStorage on mount
  useEffect(() => {
    let sessId = localStorage.getItem("session_id");
    if (!sessId) {
      sessId = (typeof crypto !== "undefined" && crypto.randomUUID) ? crypto.randomUUID() : `sess_${Math.random().toString(36).substring(2)}${Date.now().toString(36)}`;
      localStorage.setItem("session_id", sessId);
    }
    setSessionId(sessId);
  }, []);

  // Fetch persistent chat threads dynamically when sessionId is loaded
  useEffect(() => {
    if (!sessionId) return;

    async function loadChats() {
      try {
        const backendChats = await fetchChats(sessionId);
        if (backendChats && backendChats.length > 0) {
          setChats(backendChats);
          const savedActiveChat = localStorage.getItem(`active_chat_${sessionId}`);
          if (savedActiveChat && backendChats.some((c) => c.id === savedActiveChat)) {
            setActiveChat(savedActiveChat);
          } else {
            setActiveChat(backendChats[0].id);
          }
        } else {
          const defaultChat = await createChat(sessionId, "Document Chat Session");
          setChats([defaultChat]);
          setActiveChat(defaultChat.id);
        }
      } catch (err) {
        console.warn("Failed to load chat history from backend:", err.message);
      }
    }
    loadChats();
  }, [sessionId]);

  // Set active chat with local storage tracking
  function handleSetActiveChat(chatId) {
    setActiveChat(chatId);
    if (sessionId && chatId) {
      localStorage.setItem(`active_chat_${sessionId}`, chatId);
    }
  }

  // Selected citation focus state
  const [selectedCitation, setSelectedCitation] = useState(null);

  // Handle active message appending/streaming updates
  function handleSendMessage(messagePayload) {
    setChats((prevChats) =>
      prevChats.map((chat) => {
        if (chat.id !== activeChat) return chat;

        const existsIdx = chat.messages.findIndex((m) => m.id === messagePayload.id);

        if (existsIdx > -1) {
          const updatedMessages = [...chat.messages];
          if (messagePayload.text === null) {
            updatedMessages[existsIdx].isStreaming = false;
          } else {
            updatedMessages[existsIdx].text = messagePayload.text;
            if (messagePayload.citations !== undefined) {
              updatedMessages[existsIdx].citations = messagePayload.citations;
            }
            if (messagePayload.isStreaming !== undefined) {
              updatedMessages[existsIdx].isStreaming = messagePayload.isStreaming;
            }
          }
          return { ...chat, messages: updatedMessages };
        } else {
          return { ...chat, messages: [...chat.messages, messagePayload] };
        }
      })
    );
  }

  // Auto-focus and index the uploaded file globally
  function handleAddDocument(newDoc) {
    const formattedDoc = {
      ...newDoc,
      size: newDoc.size || "1.2 MB",
      date: newDoc.date || new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
      tags: newDoc.tags || ["Uploaded"]
    };

    setDocuments((prevDocs) => [formattedDoc, ...prevDocs]);
    setActiveDoc(formattedDoc);
    setIsDrawerOpen(true);

    const infoMsg = {
      id: `sys-${Date.now()}`,
      sender: "ai",
      text: `Started processing and indexing document **${newDoc.filename}** in the background via high-precision **PaddleOCR**...`,
      isStreaming: false
    };

    setChats((prevChats) =>
      prevChats.map((chat) =>
        chat.id === activeChat
          ? { ...chat, messages: [...chat.messages, infoMsg] }
          : chat
      )
    );
  }

  // Delete document globally from database and ChromaDB vectors
  async function handleDeleteDocument(docId) {
    try {
      await deleteDocument(docId);
      setDocuments((prevDocs) => {
        const updated = prevDocs.filter((d) => d.id !== docId);
        if (activeDoc && activeDoc.id === docId) {
          setActiveDoc(null);
          setIsDrawerOpen(false);
        }
        return updated;
      });
    } catch (err) {
      alert("Failed to delete document from backend.");
      console.error(err);
    }
  }

  // Initialize a fresh empty workspace chat session
  async function handleNewChat() {
    if (!sessionId) return;
    try {
      const newChatObj = await createChat(sessionId, `Document Chat Session #${chats.length + 1}`);
      setChats((prevChats) => [newChatObj, ...prevChats]);
      handleSetActiveChat(newChatObj.id);
    } catch (err) {
      alert("Failed to create a new chat session.");
      console.error(err);
    }
  }

  // Rename a specific chat thread
  async function handleRenameChat(chatId, newTitle) {
    if (!newTitle.trim()) return;
    try {
      await renameChat(chatId, newTitle);
      setChats((prevChats) =>
        prevChats.map((c) => (c.id === chatId ? { ...c, title: newTitle } : c))
      );
    } catch (err) {
      alert("Failed to rename chat session.");
      console.error(err);
    }
  }

  // Delete a specific chat thread
  async function handleDeleteChat(chatId) {
    try {
      await deleteChat(chatId);
      setChats((prevChats) => {
        const updated = prevChats.filter((c) => c.id !== chatId);
        if (activeChat === chatId) {
          if (updated.length > 0) {
            handleSetActiveChat(updated[0].id);
          } else {
            handleSetActiveChat(null);
          }
        }
        return updated;
      });
    } catch (err) {
      alert("Failed to delete chat thread.");
      console.error(err);
    }
  }

  // Share a specific chat thread (copying link safely)
  function handleShareChat(chatId) {
    const chat = chats.find((c) => c.id === chatId);
    const title = chat ? chat.title : "Workspace Chat";
    const origin = typeof window !== "undefined" ? window.location.origin : "http://localhost:3000";
    const shareUrl = `${origin}/workspace/share/${chatId}`;
    
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(shareUrl)
        .then(() => {
          alert(`Share link for "${title}" copied to clipboard!`);
        })
        .catch(() => {
          alert(`Link: ${shareUrl}`);
        });
    } else {
      alert(`Link: ${shareUrl}`);
    }
  }

  // Focus a specific document inside the slider drawer
  function handleSelectDoc(doc) {
    setActiveDoc(doc);
    setIsDrawerOpen(true);
  }

  // Handle database reset success by wiping frontend state and spawning a fresh chat thread
  async function handleResetSuccess() {
    setDocuments([]);
    setActiveDoc(null);
    setIsDrawerOpen(false);
    setSelectedCitation(null);
    setChats([]);
    setActiveChat(null);
    
    if (!sessionId) return;
    try {
      const newChatObj = await createChat(sessionId, "Document Chat Session #1");
      setChats([newChatObj]);
      handleSetActiveChat(newChatObj.id);
      setViewMode("chat");
    } catch (err) {
      console.error("Failed to generate default chat session post-reset:", err);
    }
  }

  // Locate active chat message thread
  const activeChatObj = chats.find((c) => c.id === activeChat) || chats[0];

  return (
    <main
      className="flex h-screen w-screen overflow-hidden"
      style={{ backgroundColor: "var(--champagne-mist)" }}
    >
      {/* Mobile Sidebar Toggle Button */}
      {isSidebarCollapsed && (
        <button
          onClick={() => setIsSidebarCollapsed(false)}
          className="mobile-sidebar-toggle"
          title="Open Menu"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
            width={24}
            height={24}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
          </svg>
        </button>
      )}

      {/* 1. Left Curved Sidebar Panel */}
      <Sidebar
        documents={documents}
        activeDoc={activeDoc}
        onSelectDoc={handleSelectDoc}
        onAddDocument={handleAddDocument}
        chats={chats}
        activeChat={activeChat}
        onSelectChat={(chatId) => {
          handleSetActiveChat(chatId);
          setViewMode("chat");
        }}
        onNewChat={() => {
          handleNewChat();
          setViewMode("chat");
        }}
        onRenameChat={handleRenameChat}
        onDeleteChat={handleDeleteChat}
        onShareChat={handleShareChat}
        viewMode={viewMode}
        onViewAll={() => setViewMode("explorer")}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={setIsSidebarCollapsed}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* 2. Middle Immersive Area: Chat Mode or Document Explorer Mode */}
      {viewMode === "chat" ? (
        <ChatArea
          documents={documents}
          onAddDocument={handleAddDocument}
          activeChatMessages={activeChatObj ? activeChatObj.messages : []}
          onSendMessage={handleSendMessage}
          chatId={activeChat}
          sessionId={sessionId}
          onRenameChat={handleRenameChat}
          onSelectCitation={(docIdx, pageIdx) => {
            // Identify matching active doc and pop open slide-over
            if (documents[docIdx]) {
              setActiveDoc(documents[docIdx]);
              setIsDrawerOpen(true);
            }
            setSelectedCitation({ docIndex: docIdx, pageIndex: pageIdx, ts: Date.now() });
          }}
        />
      ) : (
        <DocExplorer
          documents={documents}
          onAddDocument={handleAddDocument}
          onSelectDoc={handleSelectDoc}
          onDeleteDoc={handleDeleteDocument}
          onClose={() => setViewMode("chat")}
        />
      )}

      {/* 3. Right Absolute Slide-Over Canvas Drawer */}
      <DocViewer
        activeDoc={activeDoc}
        selectedCitation={selectedCitation}
        isDrawerOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      />

      {/* Settings Dialog Overlay */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onResetSuccess={handleResetSuccess}
      />
    </main>
  );
}
