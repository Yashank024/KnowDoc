"use client";

import React from "react";
import styles from "./Viewer.module.css";

export default function SourceCard({ file }) {
  const fileLines = file.text_lines ?? [];
  const avgConfidence = fileLines.length > 0
    ? `${Math.round(fileLines.reduce((acc, ln) => acc + ln.confidence, 0) / fileLines.length * 100)}%`
    : "100%";

  return (
    <div className={styles.sourceCard}>
      <div className={styles.sourceCardHeader}>
        <span className={styles.sourceCardTitle}>{file.filename}</span>
        <span className={styles.sourceCardStatus}>Active Source</span>
      </div>
      
      <div className={styles.sourceDetails}>
        <div className={styles.detailRow}>
          <span>Indexed Blocks:</span>
          <strong>{fileLines.length} blocks</strong>
        </div>
        <div className={styles.detailRow}>
          <span>OCR Engine:</span>
          <strong>PaddleOCR v4</strong>
        </div>
        <div className={styles.detailRow}>
          <span>Avg. Accuracy:</span>
          <strong style={{ color: "var(--emerald-tide)" }}>{avgConfidence}</strong>
        </div>
      </div>
    </div>
  );
}
