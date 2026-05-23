"use client";

import React from "react";
import Link from "next/link";
import Section   from "../../layout/Section/Section";
import Container from "../../layout/Container/Container";
import styles from "./Hero.module.css";

const STATS = [
  { value: "99.9%",           label: "OCR Accuracy" },
  { value: "< 2s",            label: "Processing"   },
  { value: "PDF · JPG · PNG", label: "Formats"      },
];

export default function Hero() {
  return (
    // Section handles padding-block; Container handles max-width + padding-inline
    <Section pt="80px" pb="56px">
      <Container>
        {/* .inner centers the copy column within the full 1400px container */}
        <div className={styles.inner}>

          {/* Live badge */}
          <div className={`${styles.badge} animate-fade-slide-up`}>
            <span className={styles.badgeDot} />
            KnowDoc v2.0 — Local OCR Intelligence
          </div>

          {/* Main headline */}
          <h1 className={`${styles.heading} animate-fade-slide-up delay-100`}>
            Instant intelligence for your{" "}
            <span className={styles.highlight}>
              <span className={styles.highlightBar} />
              enterprise docs
            </span>
            .
          </h1>

          {/* Subtitle */}
          <p className={`${styles.subtitle} animate-fade-slide-up delay-200`}>
            Drop financial receipts, scanned invoices, or legal PDFs. Extract
            high-precision text with{" "}
            <strong className={styles.subtitleAccent}>PaddleOCR</strong>, then
            query your document knowledge with full citation mapping.
          </p>

          {/* Stats row */}
          <div className={`${styles.statsRow} animate-fade-slide-up delay-300`}>
            {STATS.map((s, i) => (
              <React.Fragment key={s.label}>
                {i > 0 && <span className={styles.statDivider} />}
                <div className={styles.stat}>
                  <span className={styles.statValue}>{s.value}</span>
                  <span className={styles.statLabel}>{s.label}</span>
                </div>
              </React.Fragment>
            ))}
          </div>

          {/* CTAs */}
          <div className={`${styles.ctaRow} animate-fade-slide-up delay-400`}>
            <Link href="/workspace">
              <button id="btn-get-started" className={styles.btnPrimary}>
                Get Started Free
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none" viewBox="0 0 24 24"
                  strokeWidth={2.5} stroke="currentColor"
                  width={16} height={16}
                  className={styles.btnArrow}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                </svg>
              </button>
            </Link>

            <Link href="/workspace">
              <button id="btn-explore" className={styles.btnSecondary}>
                Explore Dashboard
              </button>
            </Link>
          </div>

        </div>
      </Container>
    </Section>
  );
}
