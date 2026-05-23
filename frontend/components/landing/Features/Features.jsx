"use client";

import React from "react";
import Section   from "../../layout/Section/Section";
import Container from "../../layout/Container/Container";
import styles from "./Features.module.css";

const FEATURES = [
  {
    title:      "High-Precision PaddleOCR v3",
    desc:       "Custom deep-learning models run locally on Windows to parse character bounding-boxes with extreme layout accuracy across scanned, photographed, or digital PDFs.",
    accent:     "var(--accent-orange)",
    iconBg:     "rgba(217,91,36,0.07)",
    iconBorder: "rgba(217,91,36,0.15)",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8}
        strokeLinecap="round" strokeLinejoin="round" width={20} height={20}>
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <path d="M3 9h18M9 21V9" />
        <circle cx="15.5" cy="15" r="2.5" strokeDasharray="2 2" />
      </svg>
    ),
  },
  {
    title:      "Context-Aware Citation Graph",
    desc:       "Every AI answer is linked directly to visual coordinate bounding boxes and page numbers in your source document, eliminating hallucination at the source.",
    accent:     "var(--emerald-tide)",
    iconBg:     "rgba(15,106,91,0.07)",
    iconBorder: "rgba(15,106,91,0.15)",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8}
        strokeLinecap="round" strokeLinejoin="round" width={20} height={20}>
        <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71" />
        <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71" />
      </svg>
    ),
  },
  {
    title:      "Elite Split-Pane Workspace",
    desc:       "A Perplexity-caliber professional workspace with document viewer, chat interface, OCR inspector, and real-time source highlighting in a single clean dashboard.",
    accent:     "var(--accent-orange)",
    iconBg:     "rgba(217,91,36,0.07)",
    iconBorder: "rgba(217,91,36,0.15)",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8}
        strokeLinecap="round" strokeLinejoin="round" width={20} height={20}>
        <rect x="2" y="3" width="20" height="18" rx="2" />
        <path d="M8 3v18M2 9h6" />
      </svg>
    ),
  },
];

export default function Features() {
  return (
    <section className={styles.wrapper}>
      <div className={styles.divider} />
      <Section pt="56px" pb="64px">
        <Container>

          {/* Section label */}
          <div className={styles.sectionLabel}>
            <span className={styles.labelText}>Core Capabilities</span>
            <span className={styles.labelLine} />
          </div>

          {/* Grid */}
          <div className={styles.grid}>
            {FEATURES.map((f, i) => (
              <div
                key={f.title}
                className={`${styles.card} animate-fade-slide-up`}
                style={{ animationDelay: `${(i + 1) * 150}ms` }}
              >
                <div
                  className={styles.cardAccent}
                  style={{ background: `linear-gradient(90deg, ${f.accent}, transparent)` }}
                />
                <div
                  className={styles.iconBadge}
                  style={{ color: f.accent, background: f.iconBg, border: `1px solid ${f.iconBorder}` }}
                >
                  {f.icon}
                </div>
                <div>
                  <h3 className={styles.title}>{f.title}</h3>
                  <p className={styles.desc}>{f.desc}</p>
                </div>
                <div className={styles.cardIndex} style={{ color: f.accent }}>
                  0{i + 1}
                </div>
              </div>
            ))}
          </div>



        </Container>
      </Section>
    </section>
  );
}
