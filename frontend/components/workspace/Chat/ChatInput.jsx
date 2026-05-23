"use client";

import React, { useRef } from "react";
import styles from "./Chat.module.css";

/**
 * ChatInput — Premium minimalist messaging bar inspired by Claude & modern LLM hubs.
 * Supports layoutMode="center" (Claude empty state) and layoutMode="bottom" (active chat).
 */
export default function ChatInput({
  value,
  onChange,
  onSubmit,
  isGenerating,
  layoutMode = "bottom", // "bottom" or "center"
  onUploadFile
}) {
  const canSend = value.trim() && !isGenerating;
  const fileInputRef = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (canSend) {
        onSubmit(e);
      }
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file && onUploadFile) {
      onUploadFile(file);
    }
    e.target.value = "";
  };

  if (layoutMode === "center") {
    return (
      <div className={styles.centerInputContainer}>
        <form onSubmit={onSubmit} className={styles.centerInputForm}>
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              isGenerating
                ? "KnowDoc is thinking..."
                : "Ask questions or index documents to search context..."
            }
            disabled={isGenerating}
            className={styles.centerTextarea}
            rows={3}
          />

          <div className={styles.centerInputFooter}>
            <div className={styles.centerFooterLeft}>
              {/* Plus Button inside input block for dynamic file uploads */}
              <button
                type="button"
                onClick={triggerFileSelect}
                className={styles.centerPlusBtn}
                title="Upload document to global memory"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2.8}
                  stroke="currentColor"
                  width={18}
                  height={18}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                </svg>
              </button>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
                accept=".jpg,.jpeg,.png,.bmp,.tiff,.pdf"
              />
            </div>

            <div className={styles.centerFooterRight}>
              {/* Claude-inspired Model Selector Pill */}
              <div className={styles.modelSelectorPill} title="Dynamic model selection">
                <span>KnowDoc AI 1.0</span>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2.5}
                  stroke="currentColor"
                  width={10}
                  height={10}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                </svg>
              </div>

              {/* Decorative Audio Icons */}
              <button type="button" className={styles.iconActionBtn} title="Voice Input (Mic)">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" width={15} height={15}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" />
                </svg>
              </button>

              <button type="button" className={styles.iconActionBtn} title="Audio output settings">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" width={15} height={15}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.114 5.636a9 9 0 010 12.728M16.463 8.288a5.25 5.25 0 010 7.424M6.75 8.25l4.72-4.72a.75.75 0 011.28.53v15.88a.75.75 0 01-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.01 9.01 0 012.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75z" />
                </svg>
              </button>

              {/* Submit send arrow */}
              <button
                type="submit"
                disabled={!canSend}
                className={styles.centerSendBtn}
                style={{
                  backgroundColor: canSend ? "var(--emerald-tide)" : "rgba(0,0,0,0.05)",
                  color:           canSend ? "var(--champagne-mist)" : "rgba(0,0,0,0.25)"
                }}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2.5}
                  stroke="currentColor"
                  width={15}
                  height={15}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 10.5L12 3m0 0l7.5 7.5M12 3v18" />
                </svg>
              </button>
            </div>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div className={styles.inputWrapper}>
      <form onSubmit={onSubmit} className={styles.inputForm}>
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            isGenerating
              ? "KnowDoc is thinking..."
              : "Ask questions or index documents to search context..."
          }
          disabled={isGenerating}
          className={styles.input}
        />

        <button
          type="submit"
          disabled={!canSend}
          className={styles.sendBtn}
          style={{
            backgroundColor: canSend ? "var(--emerald-tide)" : "transparent",
            color:           canSend ? "var(--champagne-mist)" : "rgba(0,0,0,0.3)",
            boxShadow:       canSend ? "0 2px 8px rgba(15, 106, 91, 0.2)" : "none"
          }}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2.5}
            stroke="currentColor"
            width={16}
            height={16}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 10.5L12 3m0 0l7.5 7.5M12 3v18" />
          </svg>
        </button>
      </form>

      <p className={styles.inputHint}>
        Connected to high-precision PaddleOCR layout engine. Context parsed dynamically.
      </p>
    </div>
  );
}
