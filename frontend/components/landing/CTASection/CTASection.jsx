"use client";

import React from "react";
import Link from "next/link";
import Section   from "../../layout/Section/Section";
import Container from "../../layout/Container/Container";
import styles from "./CTASection.module.css";

export default function CTASection() {
  return (
    <Section pt="0" pb="80px">
      <Container>
        <div className={`${styles.inner} animate-fade-slide-up delay-100`}>

          <span className={styles.label}>Get Started Today</span>

          <h2 className={styles.heading}>
            Ready to unlock your{" "}
            <span className={styles.headingAccent}>documents</span>?
          </h2>

          <p className={styles.desc}>
            Upload your first PDF in seconds. No configuration. No cloud
            uploads. Everything runs locally on your machine.
          </p>

          <div className={styles.ctaRow}>
            <Link href="/workspace" className={styles.btn}>
              Open Workspace →
            </Link>
          </div>

          <span className={styles.trust}>
            100% local processing · No data leaves your machine
          </span>

        </div>
      </Container>
    </Section>
  );
}
