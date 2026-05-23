"use client";

import React from "react";
import styles from "./Viewer.module.css";

export default function ViewerDrawer({ textLines, highlightedIndex }) {
  const selected = highlightedIndex !== null ? textLines?.[highlightedIndex] : null;

  return (
    <div className={styles.drawerDetails}>
      <span className={styles.drawerLabel}>Selected Coordinate Metadata</span>

      {selected ? (
        <div className={styles.drawerContent}>
          <blockquote className={styles.drawerText}>
            &ldquo;{selected.text}&rdquo;
          </blockquote>
          <div className={styles.drawerStats}>
            <div className={styles.drawerBadge}>
              <span className={styles.statKey}>Accuracy:</span>
              <strong className={styles.statVal}>{Math.round(selected.confidence * 100)}%</strong>
            </div>
            <div className={styles.drawerBadge}>
              <span className={styles.statKey}>Coordinates:</span>
              <strong className={styles.statVal}>
                [{selected.box?.[0]?.[0]}, {selected.box?.[0]?.[1]}]
              </strong>
            </div>
          </div>
        </div>
      ) : (
        <div className={styles.drawerEmptyState}>
          No coordinate block selected. Click inside the visual bounding box preview above to inspect.
        </div>
      )}
    </div>
  );
}
