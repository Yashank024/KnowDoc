"use client";

import React, { useState, useRef, useEffect } from "react";
import { uploadDocumentToOCR, streamAIChatResponse } from "../../../lib/api";
import MessageList from "./MessageList";
import ChatInput   from "./ChatInput";
import styles from "./Chat.module.css";

/**
 * ChatArea — primary conversational OS interface.
 * Coordinates: global document memory context, hidden document upload triggers, and simulated AI streaming.
 */
export default function ChatArea({
  documents,
  onAddDocument,
  activeChatMessages,
  onSendMessage,
  onSelectCitation,
  chatId,
  sessionId,
  onRenameChat
}) {
  const [inputValue, setInputValue] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null); // 'Uploading' | 'Processing OCR' | 'Success!' | 'Error' | null

  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeChatMessages]);

  async function handleSend(e) {
    e.preventDefault();
    if (!inputValue.trim() || isGenerating) return;

    const userText = inputValue;
    const aiMessageId = Date.now().toString();

    setInputValue("");
    setIsGenerating(true);

    onSendMessage({ id: `user-${Date.now()}`, sender: "user", text: userText });
    onSendMessage({ id: aiMessageId, sender: "ai", text: "", isStreaming: true });

    try {
      const result = await streamAIChatResponse(userText, documents, activeChatMessages, chatId, sessionId, (chunk) => {
        onSendMessage({ id: aiMessageId, sender: "ai", text: chunk, isStreaming: true });
      });
      onSendMessage({
        id: aiMessageId,
        sender: "ai",
        text: result.reply,
        citations: result.citations,
        isStreaming: false
      });
      if (result.chat_title && onRenameChat) {
        onRenameChat(chatId, result.chat_title);
      }
    } catch (err) {
      console.error(err);
      onSendMessage({
        id: aiMessageId,
        sender: "ai",
        text: "Error: Local FastAPI server not responding on port 8000.",
        isStreaming: false
      });
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleUploadFile(file) {
    const allowed = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".pdf"];
    const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();

    if (!allowed.includes(ext)) {
      alert("Unsupported file format. Please upload images or PDFs.");
      return;
    }

    setUploadStatus("Uploading");

    try {
      await new Promise((r) => setTimeout(r, 300));
      setUploadStatus("Processing OCR");
      
      const ocrResult = await uploadDocumentToOCR(file);
      setUploadStatus("Success!");

      onAddDocument({
        id: ocrResult.document_id || ocrResult.id || Date.now().toString(),
        filename: file.name,
        text_lines: ocrResult.text_lines || [],
        full_text: ocrResult.full_text || "",
        status: ocrResult.status || "processing"
      });

      setTimeout(() => setUploadStatus(null), 1500);
    } catch (err) {
      console.error(err);
      setUploadStatus("Error");
      alert(err.message || "Failed to communicate with FastAPI PaddleOCR server.");
      setUploadStatus(null);
    }
  }

  function handleSuggestionClick(text) {
    setInputValue(text);
  }

  const isEmpty = activeChatMessages.length === 0;

  return (
    <section className={styles.panel}>
      {/* Global Memory Context Header */}
      <div className={styles.topBar}>
        <div className={styles.folderContext}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
            width={18}
            height={18}
            className={styles.topBarFolderIcon}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z"
            />
          </svg>
          <span className={styles.topBarLabel}>
            Global AI Memory
          </span>
        </div>

        <div className={styles.actionsRow}>
          <div className={styles.topBarStatus}>
            <span className={styles.statusDot} />
            <span className={styles.statusText}>
              Live Memory ({documents.length} docs indexed)
            </span>
          </div>
        </div>
      </div>

      {isEmpty ? (
        <div className={styles.emptyStateContainer}>
          <div className={styles.welcomePanel}>
            <img src="/logo_symbol.png" alt="KnowDoc Logo" className={styles.welcomeIcon} />
            <h2 className={styles.welcomeTitle}>What document can I help audit today?</h2>
            <p className={styles.welcomeDesc}>
              Upload invoices, HR manuals, or spreadsheets directly. Our active PaddleOCR engine parses visual layout coordinates to index text blocks.
            </p>
          </div>

          {/* Centered spacious Claude-style chat input */}
          <div className={styles.centeredInputWrapper}>
            {uploadStatus && (
              <div className={styles.centeredUploadStatus}>
                <span className={styles.spinnerSmall} />
                <span className={styles.centeredUploadText}>{uploadStatus}</span>
              </div>
            )}
            <ChatInput
              value={inputValue}
              onChange={setInputValue}
              onSubmit={handleSend}
              isGenerating={isGenerating}
              layoutMode="center"
              onUploadFile={handleUploadFile}
              disabled={isGenerating}
              documents={documents}
            />
          </div>

          {/* Suggestion prompt cards */}
          <div className={styles.welcomePanel} style={{ marginTop: 0 }}>
            <div className={styles.suggestionsGrid}>
              <div
                className={styles.suggestionCard}
                onClick={() => handleSuggestionClick("Review annual leave limits and standard PTO allocation rules.")}
              >
                <span className={styles.suggestionTitle}>📄 Audit HR Policy</span>
                <p className={styles.suggestionText}>Review annual leave limits and standard PTO allocation rules.</p>
              </div>
              <div
                className={styles.suggestionCard}
                onClick={() => handleSuggestionClick("Audit payment totals and verify vendor name coordinates.")}
              >
                <span className={styles.suggestionTitle}>💰 Invoice coordinates</span>
                <p className={styles.suggestionText}>Audit payment totals and verify vendor name coordinates.</p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <>
          {/* Message thread */}
          <MessageList
            messages={activeChatMessages}
            documents={documents}
            onSelectCitation={onSelectCitation}
            scrollRef={scrollRef}
          />

          {/* Prompts Input Area */}
          <ChatInput
            value={inputValue}
            onChange={setInputValue}
            onSubmit={handleSend}
            isGenerating={isGenerating}
            layoutMode="bottom"
            onUploadFile={handleUploadFile}
            disabled={isGenerating}
            documents={documents}
          />
        </>
      )}
    </section>
  );
}
