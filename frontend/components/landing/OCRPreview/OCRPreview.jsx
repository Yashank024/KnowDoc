"use client";

import React, { useState } from "react";
import Section   from "../../layout/Section/Section";
import Container from "../../layout/Container/Container";
import styles from "./OCRPreview.module.css";

/* ── Data ── */
const LINES = [
  { id: "inv",    text: "INVOICE #INV-2026-904",  width: "88%", conf: "99.9%", coords: "[x:42, y:88,  w:224, h:24]" },
  { id: "date",   text: "Date: May 22, 2026",     width: "52%", conf: "99.7%", coords: "[x:42, y:124, w:180, h:20]" },
  { id: "vendor", text: "Vendor: PaddleOCR Corp",  width: "62%", conf: "99.8%", coords: "[x:42, y:158, w:210, h:20]" },
  { id: "sub",    text: "Subtotal: $13,500.00",    width: "48%", conf: "99.5%", coords: "[x:42, y:210, w:185, h:20]" },
  { id: "tax",    text: "Tax (5.56%): $750.00",    width: "48%", conf: "99.3%", coords: "[x:42, y:238, w:185, h:20]" },
];

const TOTALS = [
  { id: "lbl", text: "TOTAL AMOUNT DUE", bold: true, flex: "1",    coords: "[x:42,  y:280, w:195, h:22]", conf: "99.6%"               },
  { id: "val", text: "$14,250.00",       bold: true, flex: "none", coords: "[x:290, y:280, w:110, h:22]", conf: "99.9%", isVal: true },
];

/* ── LineItem sub-component ── */
function LineItem({ id, text, bold, coords, conf, width, flexStyle, isHovered, onEnter, onLeave }) {
  const cc = "var(--accent-orange)";
  return (
    <div
      className={styles.lineRow}
      style={{ width, flex: flexStyle, minWidth: flexStyle ? 0 : undefined }}
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
    >
      {isHovered && (
        <>
          <span className={`${styles.corner} ${styles.cornerTL}`} style={{ borderColor: cc }} />
          <span className={`${styles.corner} ${styles.cornerTR}`} style={{ borderColor: cc }} />
          <span className={`${styles.corner} ${styles.cornerBL}`} style={{ borderColor: cc }} />
          <span className={`${styles.corner} ${styles.cornerBR}`} style={{ borderColor: cc }} />
          <div className={styles.tooltip}>
            <span className={styles.tooltipCoord}>{coords}</span>
            <span className={styles.tooltipConf}>{conf}</span>
          </div>
        </>
      )}
      <div
        className={styles.lineText}
        style={{
          fontWeight: bold ? 700 : 500,
          color:      isHovered ? "var(--accent-orange)" : "rgba(17,17,17,0.75)",
          background: isHovered ? "rgba(217,91,36,0.06)" : "transparent",
        }}
      >
        {text}
      </div>
    </div>
  );
}

/* ── Main export ── */
export default function OCRPreview() {
  const [hovered,    setHovered]    = useState(null);
  const [citHovered, setCitHovered] = useState(false);

  return (
    <Section pt="0" pb="72px">
      <Container>

        {/* Section label */}
        <div className={styles.sectionLabel}>
          <span className={styles.labelText}>Live OCR Demo</span>
          <span className={styles.labelLine} />
        </div>

        {/* Card */}
        <div className={`${styles.cardWrapper} animate-fade-slide-up delay-200`}>
          <div className={styles.glow} />
          <div className={styles.card}>

            {/* Title bar */}
            <div className={styles.titleBar}>
              <div className={styles.trafficLights}>
                <span className={`${styles.dot} ${styles.dotRed}`} />
                <span className={`${styles.dot} ${styles.dotYellow}`} />
                <span className={`${styles.dot} ${styles.dotGreen}`} />
              </div>
              <div className={styles.fileTab}>
                <span className={`${styles.fileDot} animate-pulse`} />
                receipt_2026.pdf
              </div>
              <span className={styles.liveBadge}>OCR Live</span>
            </div>

            {/* Body */}
            <div className={styles.body}>

              {/* Doc pane */}
              <div className={styles.docPane}>
                <div className={`${styles.scanLine} animate-scan`} />
                <div className={styles.gridOverlay} />

                <div className={styles.paper}>
                  <div className={styles.paperHeader}>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <img src="/logo_symbol.png" alt="" style={{ height: "18px", width: "auto", objectFit: "contain" }} />
                      <div>
                        <div className={styles.paperLabel}>KnowDoc OCR Engine</div>
                        <div className={styles.paperSub}>Avg. confidence 99.8%</div>
                      </div>
                    </div>
                    <span className={styles.pageTag}>Page 1 / 1</span>
                  </div>

                  <div className={styles.lines}>
                    {LINES.map((line) => (
                      <LineItem
                        key={line.id} {...line}
                        isHovered={hovered === line.id}
                        onEnter={() => setHovered(line.id)}
                        onLeave={() => setHovered(null)}
                      />
                    ))}
                    <div className={styles.divider} />
                    <div className={styles.totalRow}>
                      {TOTALS.map((item) => (
                        <LineItem
                          key={item.id} {...item}
                          flexStyle={item.flex}
                          isHovered={hovered === item.id || (item.isVal && citHovered)}
                          onEnter={() => setHovered(item.id)}
                          onLeave={() => setHovered(null)}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* AI panel */}
              <div className={styles.aiPane}>
                <div className={styles.aiPaneHeader}>
                  <span className={styles.aiPaneLabel}>AI Response</span>
                </div>
                <div className={styles.questionBubble}>
                  What is the total invoice amount?
                </div>
                <div
                  className={styles.answerBubble}
                  style={{
                    border:     citHovered ? "1px solid rgba(217,91,36,0.30)" : "1px solid rgba(15,106,91,0.10)",
                    background: citHovered ? "rgba(217,91,36,0.04)"          : "rgba(255,255,255,0.75)",
                  }}
                >
                  <div className={styles.aiRow}>
                    <div className={styles.aiAvatar}>AI</div>
                    <div>
                      <p className={styles.aiText}>
                        Total due is{" "}
                        <strong className={styles.aiCited}>$14,250.00</strong>{" "}
                        <span
                          className="citation-badge"
                          onMouseEnter={() => setCitHovered(true)}
                          onMouseLeave={() => setCitHovered(false)}
                        >
                          [1]
                        </span>
                      </p>
                      <p className={styles.aiSource}>↳ [x:290, y:280] · Page 1 · 99.9%</p>
                    </div>
                  </div>
                </div>
                <div className={styles.meter}>
                  <div className={styles.meterRow}>
                    <span className={styles.meterLabel}>Avg. Confidence</span>
                    <span className={styles.meterValue}>99.8%</span>
                  </div>
                  <div className={styles.meterTrack}>
                    <div className={styles.meterFill} />
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>

      </Container>
    </Section>
  );
}
