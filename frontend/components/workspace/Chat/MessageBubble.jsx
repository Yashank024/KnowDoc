"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import styles from "./Chat.module.css";

function findDocIndex(filename, documents) {
  if (!documents || documents.length === 0) return -1;
  const target = filename.trim().toLowerCase();
  
  // 1. Exact match
  let idx = documents.findIndex(d => d.filename.trim().toLowerCase() === target);
  if (idx !== -1) return idx;
  
  // 2. Fuzzy/contains match
  idx = documents.findIndex(d => d.filename.toLowerCase().includes(target) || target.includes(d.filename.toLowerCase()));
  return idx;
}

// Preprocesses [Doc: filename, Page Y] style brackets or [Doc X, Page Y] into standard markdown links cite://X/Y
function preprocessCitations(text, documents = []) {
  if (!text) return "";
  
  // 1. Process new format [Doc: filename, Page Y]
  let processed = text.replace(/\[Doc:\s*([^,\]]+)(?:,\s*Page\s*(\d+))?\]/g, (match, filename, pageIdxStr) => {
    const pageNum = pageIdxStr ? pageIdxStr : "1";
    const docIdx = findDocIndex(filename, documents);
    const displayDocIdx = docIdx !== -1 ? docIdx : 0;
    return `[[Doc ${displayDocIdx + 1}, Page ${pageNum}]](cite://${displayDocIdx}/${pageNum})`;
  });

  // 2. Process old format [Doc X, Page Y]
  processed = processed.replace(/\[Doc\s*(\d+)(?:,\s*Page\s*(\d+))?\]/g, (match, docIdxStr, pageIdxStr) => {
    const docNum = docIdxStr;
    const pageNum = pageIdxStr ? pageIdxStr : "1";
    const docIdx = parseInt(docNum) - 1;
    return `[[Doc ${docNum}${pageIdxStr ? `, Page ${pageIdxStr}` : ""}]](cite://${docIdx}/${pageNum})`;
  });

  return processed;
}

// Extracts unique citations from raw text for bottom sources block
function extractCitations(text, documents = []) {
  if (!text) return [];
  const uniqueCitations = [];
  const citationKeyMap = {};
  
  // 1. Extract from new format [Doc: filename, Page Y]
  const newRegex = /\[Doc:\s*([^,\]]+)(?:,\s*Page\s*(\d+))?\]/g;
  let match;
  newRegex.lastIndex = 0;
  while ((match = newRegex.exec(text)) !== null) {
    const filename = match[1].trim();
    const docIdx = findDocIndex(filename, documents);
    if (docIdx === -1) continue;
    const pageIdx = match[2] ? parseInt(match[2]) : 1;
    const key = `${docIdx}-${pageIdx}`;
    if (citationKeyMap[key] === undefined) {
      const num = uniqueCitations.length + 1;
      uniqueCitations.push({
        num,
        docIdx,
        pageIdx,
        key
      });
      citationKeyMap[key] = num;
    }
  }

  // 2. Extract from old format [Doc X, Page Y]
  const oldRegex = /\[Doc\s*(\d+)(?:,\s*Page\s*(\d+))?\]/g;
  oldRegex.lastIndex = 0;
  while ((match = oldRegex.exec(text)) !== null) {
    const docIdx = parseInt(match[1]) - 1;
    const pageIdx = match[2] ? parseInt(match[2]) : 1;
    const key = `${docIdx}-${pageIdx}`;
    if (citationKeyMap[key] === undefined) {
      const num = uniqueCitations.length + 1;
      uniqueCitations.push({
        num,
        docIdx,
        pageIdx,
        key
      });
      citationKeyMap[key] = num;
    }
  }

  return uniqueCitations;
}

export default function MessageBubble({ msg, documents, onSelectCitation }) {
  const isUser = msg.sender === "user";
  
  let uniqueCitations = [];
  if (!isUser) {
    if (msg.citations && msg.citations.length > 0) {
      uniqueCitations = msg.citations;
    } else {
      uniqueCitations = extractCitations(msg.text, documents);
    }
  }

  const preprocessedText = preprocessCitations(msg.text, documents);

  // Custom Markdown Element Renderers
  const components = {
    a: ({ href, children }) => {
      if (href && href.startsWith("cite://")) {
        const parts = href.replace("cite://", "").split("/");
        const docIdx = parseInt(parts[0]);
        const pageIdx = parseInt(parts[1]);
        return (
          <span
            className={styles.superscriptCitation}
            onClick={() => onSelectCitation(docIdx, pageIdx)}
            title={`Click to inspect source (Page ${pageIdx})`}
          >
            <sup>{children}</sup>
          </span>
        );
      }

      // Sanitize URL to prevent javascript: and data: XSS attacks
      let safeHref = href;
      const isSafe = href && (
        href.startsWith("http://") || 
        href.startsWith("https://") || 
        href.startsWith("mailto:") || 
        href.startsWith("tel:")
      );
      
      if (!isSafe) {
        safeHref = "#";
      }

      return (
        <a
          href={safeHref}
          target={safeHref === "#" ? "_self" : "_blank"}
          rel="noopener noreferrer"
          style={{ color: "var(--emerald-tide, #0f6a5b)", textDecoration: "underline" }}
          onClick={(e) => {
            if (safeHref === "#") {
              e.preventDefault();
            }
          }}
        >
          {children}
        </a>
      );
    },
    table: ({ children }) => (
      <div style={{ overflowX: "auto", margin: "12px 0", borderRadius: "8px", border: "1px solid var(--border-color, #e5e7eb)" }}>
        <table style={{ borderCollapse: "collapse", width: "100%", fontSize: "13.5px" }}>
          {children}
        </table>
      </div>
    ),
    thead: ({ children }) => <thead style={{ backgroundColor: "rgba(15, 106, 91, 0.05)" }}>{children}</thead>,
    th: ({ children }) => (
      <th style={{ borderBottom: "2px solid rgba(15, 106, 91, 0.1)", padding: "8px 12px", textAlign: "left", fontWeight: "700", color: "var(--premium-black, #111827)" }}>
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td style={{ borderBottom: "1px solid rgba(15, 106, 91, 0.05)", padding: "8px 12px", color: "var(--premium-black, #111827)" }}>
        {children}
      </td>
    ),
    tr: ({ children }) => <tr style={{ transition: "background-color 0.15s ease" }} className="hover:bg-[rgba(15,106,91,0.02)]">{children}</tr>,
    ul: ({ children }) => <ul style={{ paddingLeft: "20px", listStyleType: "disc", margin: "8px 0" }}>{children}</ul>,
    ol: ({ children }) => <ol style={{ paddingLeft: "20px", listStyleType: "decimal", margin: "8px 0" }}>{children}</ol>,
    li: ({ children }) => <li style={{ marginBottom: "4px" }}>{children}</li>,
    h1: ({ children }) => <h1 style={{ fontSize: "17px", fontWeight: "800", color: "var(--premium-black, #111827)", marginTop: "16px", marginBottom: "8px" }}>{children}</h1>,
    h2: ({ children }) => <h2 style={{ fontSize: "15px", fontWeight: "700", color: "var(--premium-black, #111827)", marginTop: "14px", marginBottom: "6px" }}>{children}</h2>,
    h3: ({ children }) => <h3 style={{ fontSize: "14px", fontWeight: "700", color: "var(--premium-black, #111827)", marginTop: "12px", marginBottom: "4px" }}>{children}</h3>,
    p: ({ children }) => <p style={{ margin: "0 0 8px 0", lineHeight: "1.6" }}>{children}</p>,
    strong: ({ children }) => <strong style={{ fontWeight: "700", color: "var(--premium-black, #111827)" }}>{children}</strong>
  };

  return (
    <div className={`${styles.bubbleWrapper} ${isUser ? styles.bubbleWrapperUser : ""}`}>
      <span className={styles.senderTag}>
        {isUser ? "Yashank" : "KnowDoc AI"}
      </span>

      <div className={`${styles.bubble} ${isUser ? styles.bubbleUser : styles.bubbleAi}`}>
        <div className={styles.messageText}>
          {msg.text ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
              {preprocessedText}
            </ReactMarkdown>
          ) : null}
        </div>

        {/* Streaming dots animation */}
        {msg.isStreaming && msg.text === "" && (
          <div className={styles.thinkingDots}>
            <span style={{ animationDelay: "0ms" }} />
            <span style={{ animationDelay: "150ms" }} />
            <span style={{ animationDelay: "300ms" }} />
          </div>
        )}

        {/* Dynamic bottom citation/sources row for AI responses */}
        {!isUser && uniqueCitations.length > 0 && (
          <div className={styles.sourcesContainer}>
            <div className={styles.sourcesHeader}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2.5}
                stroke="currentColor"
                width={12}
                height={12}
                className={styles.sourcesIcon}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"
                />
              </svg>
              <span>Sources</span>
            </div>
            <div className={styles.sourcesList}>
              {uniqueCitations.map((cite, idx) => {
                const filename = cite.filename;
                const docIdx = findDocIndex(filename, documents);
                
                // Determine first page and page list text representation
                let pageIdx = 1;
                let pageLabel = "";
                if (cite.pages && cite.pages.length > 0) {
                  pageIdx = cite.pages[0];
                  pageLabel = `Page ${cite.pages.join(", ")}`;
                } else if (cite.pageIdx !== undefined) {
                  pageIdx = cite.pageIdx;
                  pageLabel = `Page ${cite.pageIdx}`;
                } else {
                  pageLabel = "Page 1";
                }
                
                const displayFilename = filename;
                
                return (
                  <button
                    key={cite.key || idx}
                    onClick={() => {
                      if (docIdx !== -1) {
                        onSelectCitation(docIdx, pageIdx);
                      }
                    }}
                    className={styles.sourceCard}
                    title={`Click to inspect ${displayFilename}`}
                  >
                    <span className={styles.sourceBadge}>{idx + 1}</span>
                    <span className={styles.sourceFilename}>{displayFilename}</span>
                    <span className={styles.sourcePage}>{pageLabel}</span>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={2.5}
                      stroke="currentColor"
                      width={10}
                      height={10}
                      className={styles.sourceArrow}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25" />
                    </svg>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
