"use client";

import React from "react";
import styles from "./Viewer.module.css";

/**
 * RawTextList — extracted text blocks with confidence badges.
 * ~55 lines. Pure renderer, no state.
 */
export default function RawTextList({ textLines, highlightedIndex, onSelect }) {
  return (
    <div className={styles.stack}>
      <span className={styles.sectionLabel}>PaddleOCR Detections</span>

      <div className={styles.rawList}>
        {textLines?.map((line, idx) => {
          const confPct  = Math.round(line.confidence * 100);
          const isHighConf = confPct >= 90;
          const isActive   = highlightedIndex === idx;

          return (
            <div
              key={idx}
              onClick={() => onSelect(idx)}
              className={`${styles.rawItem} ${isActive ? styles.rawItemActive : ""}`}
            >
              <div className={styles.rawItemText}>{line.text}</div>
              <div className={styles.rawItemMeta}>
                <span className={styles.rawBlockLabel}>Block #{idx + 1}</span>
                <span className={`${styles.rawConfBadge} ${isHighConf ? styles.rawConfHigh : styles.rawConfLow}`}>
                  Conf: {confPct}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
