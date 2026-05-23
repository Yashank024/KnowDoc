"use client";

import React from "react";
import OCRCanvas from "./OCRCanvas";
import styles from "./Viewer.module.css";

export default function CitationPreview({
  activeDoc,
  highlightedIndex,
  onSelectHighlight
}) {
  return (
    <div className={styles.citationPreviewContainer}>
      <div className={styles.canvasWrapper}>
        <OCRCanvas
          textLines={activeDoc.text_lines}
          highlightedIndex={highlightedIndex}
          onSelect={onSelectHighlight}
        />
      </div>
    </div>
  );
}
