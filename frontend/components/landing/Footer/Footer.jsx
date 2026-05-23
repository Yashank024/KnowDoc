"use client";

import React from "react";
import Container from "../../layout/Container/Container";
import styles from "./Footer.module.css";

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <Container>
        <div className={styles.divider} />
        
        <div className={styles.grid}>
          {/* Brand Row */}
          <div className={styles.brandCol}>
            <div className={styles.brand}>
              <img src="/logo_symbol.png" alt="KnowDoc Logo" className={styles.logoImg} />
              <img src="/Title.png" alt="KnowDoc Title" className={styles.titleImg} />
            </div>
            <p className={styles.brandDesc}>
              An AI knowledge operating system and local-first document memory engine powered by advanced OCR.
            </p>
            <div className={styles.creditBadge}>
              <span className={styles.pulseDot} />
              Completely created by Yashank
            </div>
          </div>

          {/* Contact Details Card */}
          <div className={styles.contactCard}>
            <h4 className={styles.colTitle}>Architect & Developer</h4>
            <div className={styles.cardContent}>
              <div className={styles.cardHeader}>
                <div className={styles.avatar}>YG</div>
                <div>
                  <div className={styles.devName}>Yashank Gupta</div>
                  <div className={styles.devTitle}>Full-Stack AI Engineer</div>
                </div>
              </div>
              
              <div className={styles.contactList}>
                <a href="tel:8005282545" className={styles.contactItem}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className={styles.contactIcon}>
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
                  </svg>
                  <span>8005282545</span>
                </a>
                
                <a href="mailto:yg421518@gmail.com" className={styles.contactItem}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className={styles.contactIcon}>
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                    <polyline points="22,6 12,13 2,6" />
                  </svg>
                  <span>yg421518@gmail.com</span>
                </a>
              </div>
            </div>
          </div>

          {/* Technology & Stack Column */}
          <div className={styles.stackCol}>
            <h4 className={styles.colTitle}>Operational Engine</h4>
            <div className={styles.techChips}>
              <div className={styles.chip} style={{ "--accent": "var(--accent-orange)" }}>
                <span>Next.js 14</span>
              </div>
              <div className={styles.chip} style={{ "--accent": "var(--emerald-tide)" }}>
                <span>FastAPI</span>
              </div>
              <div className={styles.chip} style={{ "--accent": "var(--accent-orange)" }}>
                <span>PaddleOCR v3</span>
              </div>
              <div className={styles.chip} style={{ "--accent": "var(--emerald-tide)" }}>
                <span>React 18</span>
              </div>
              <div className={styles.chip} style={{ "--accent": "var(--premium-black)" }}>
                <span>Local SQLite</span>
              </div>
              <div className={styles.chip} style={{ "--accent": "var(--emerald-tide)" }}>
                <span>Vanilla CSS Modules</span>
              </div>
            </div>
            <p className={styles.stackDesc}>
              Zero external APIs. High performance. Native intelligence directly executed on device.
            </p>
          </div>
        </div>

        {/* Footer Bottom Bar */}
        <div className={styles.bottomBar}>
          <p className={styles.copyright}>
            © {new Date().getFullYear()} KnowDoc. All rights reserved.
          </p>
          <div className={styles.bottomLinks}>
            <a href="https://github.com" target="_blank" rel="noreferrer" className={styles.bottomLink}>
              GitHub Repository
            </a>
            <span className={styles.dotSeparator} />
            <a href="#" className={styles.bottomLink}>
              Documentation
            </a>
          </div>
        </div>
      </Container>
    </footer>
  );
}
