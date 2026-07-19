"use client";

import React, { useEffect, useState } from "react";
import Image from "next/image";
import { checkBackendHealth } from "../../../lib/api";
import Container from "../../layout/Container/Container";
import styles from "./Navbar.module.css";

const STATUS_MAP = {
  online:   { color: "#22c55e", label: "Online",    pulse: true  },
  checking: { color: "#f59e0b", label: "Checking…", pulse: false },
  offline:  { color: "#ef4444", label: "Offline",   pulse: false },
};

export default function Navbar() {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    checkBackendHealth()
      .then((h) => setStatus(h.status === "healthy" ? "online" : "offline"))
      .catch(() => setStatus("offline"));
  }, []);

  const dot = STATUS_MAP[status];

  return (
    <header className={styles.header}>
      {/* Container provides max-width + padding-inline globally */}
      <Container>
        <div className={styles.inner}>

          {/* Logo — uses real brand assets */}
          <div className={styles.logo}>
            <img src="/logo_symbol.png" alt="KnowDoc" className={styles.logoImg} />
            <img src="/Title.png"       alt="KnowDoc" className={styles.titleImg} />
          </div>

          {/* Right cluster */}
          <nav className={styles.navRight}>
            <div className={styles.statusChip}>
              <span
                className={styles.statusDot}
                style={{
                  backgroundColor: dot.color,
                  animation: dot.pulse
                    ? "pulse 2s cubic-bezier(0.4,0,0.6,1) infinite"
                    : "none",
                }}
              />
              PaddleOCR Engine:&nbsp;
              <span className={styles.statusLabel} style={{ color: dot.color }}>
                {dot.label}
              </span>
            </div>

            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className={styles.docsLink}
            >
              Docs
            </a>
          </nav>

        </div>
      </Container>
    </header>
  );
}
