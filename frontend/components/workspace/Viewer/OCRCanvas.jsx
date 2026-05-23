"use client";

import React from "react";
import styles from "./Viewer.module.css";

const W = 1000;
const H = 1000;

/**
 * OCRCanvas — SVG polygon overlay + absolute text labels.
 * ~75 lines. Pure renderer, no state.
 */
export default function OCRCanvas({ textLines, highlightedIndex, onSelect }) {
  return (
    <div className={styles.stack}>
      <span className={styles.sectionLabel}>Interactive Bounding Boxes</span>

      <div className={styles.canvasCard}>
        {/* Watermark */}
        <div className={styles.canvasWatermark}>DOC</div>

        {/* SVG polygons */}
        <svg viewBox={`0 0 ${W} ${H}`} className={styles.canvasSvg}>
          {textLines?.map((line, idx) => {
            const box = line.box;
            if (!box || box.length < 4) return null;
            const pts = box.map((pt) => `${pt[0]},${pt[1]}`).join(" ");
            const hi  = highlightedIndex === idx;
            return (
              <polygon
                key={idx}
                points={pts}
                fill={hi ? "rgba(217,91,36,0.15)" : "rgba(15,106,91,0.05)"}
                stroke={hi ? "var(--accent-orange)" : "var(--emerald-tide)"}
                strokeWidth={hi ? 4 : 2}
                className={styles.polygon}
              />
            );
          })}
        </svg>

        {/* Absolute text labels */}
        {textLines?.map((line, idx) => {
          const box = line.box;
          if (!box || box.length < 4) return null;
          const x = box[0][0];
          const y = box[0][1];
          const bw = box[1][0] - box[0][0];
          const bh = box[2][1] - box[1][1];
          const hi = highlightedIndex === idx;

          return (
            <div
              key={idx}
              onClick={() => onSelect(idx)}
              className={styles.textLabel}
              style={{
                left:   `${(x / W) * 100}%`,
                top:    `${(y / H) * 100}%`,
                maxWidth: `${(bw / W) * 100}%`,
                height: `${(bh / H) * 100}%`,
                color:  hi ? "var(--accent-orange)" : "var(--emerald-tide)",
                backgroundColor: hi ? "rgba(217,91,36,0.05)" : "rgba(255,255,255,0.8)",
                border: hi ? "1px solid var(--accent-orange)" : "1px solid rgba(15,106,91,0.1)",
                boxShadow: hi ? "0 2px 6px rgba(217,91,36,0.15)" : "none",
                transform: hi ? "scale(1.02)" : "none",
              }}
            >
              <span className={styles.textLabelText}>{line.text}</span>
            </div>
          );
        })}
      </div>

      <p className={styles.canvasHint}>
        Click text boxes to audit bounding-box placement.
      </p>
    </div>
  );
}
