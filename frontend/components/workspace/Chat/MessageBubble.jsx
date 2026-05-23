"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import styles from "./Chat.module.css";

// Preprocesses [Doc X, Page Y] style brackets into standard markdown links cite://X/Y
function preprocessCitations(text) {
  if (!text) return "";
  return text.replace(/\[Doc\s*(\d+)(?:,\s*Page\s*(\d+))?\]/g, (match, docIdxStr, pageIdxStr) => {
    const docNum = docIdxStr;
    const pageNum = pageIdxStr ? pageIdxStr : "1";
    return `[[Doc ${docNum}${pageIdxStr ? `, Page ${pageIdxStr}` : ""}]](cite://${docNum}/${pageNum})`;
  });
}

// Extracts unique citations from raw text for bottom sources block
function extractCitations(text) {
  if (!text) return [];
  const uniqueCitations = [];
  const citationKeyMap = {};
  const citationRegex = /\[Doc\s*(\d+)(?:,\s*Page\s*(\d+))?\]/g;
  let match;
  
  citationRegex.lastIndex = 0;
  while ((match = citationRegex.exec(text)) !== null) {
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
  const uniqueCitations = isUser ? [] : extractCitations(msg.text);
  const preprocessedText = preprocessCitations(msg.text);

  // Custom Markdown Element Renderers
  const components = {
    a: ({ href, children }) => {
      if (href && href.startsWith("cite://")) {
        const parts = href.replace("cite://", "").split("/");
        const docIdx = parseInt(parts[0]) - 1;
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
      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: "var(--emerald-tide, #0f6a5b)", textDecoration: "underline" }}
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
              {uniqueCitations.map((cite) => {
                const doc = documents?.[cite.docIdx];
                const filename = doc ? doc.filename : `Document ${cite.docIdx + 1}`;
                return (
                  <button
                    key={cite.key}
                    onClick={() => onSelectCitation(cite.docIdx, cite.pageIdx)}
                    className={styles.sourceCard}
                    title={`Click to inspect ${filename}`}
                  >
                    <span className={styles.sourceBadge}>{cite.num}</span>
                    <span className={styles.sourceFilename}>{filename}</span>
                    <span className={styles.sourcePage}>Page {cite.pageIdx}</span>
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
