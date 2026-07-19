"use client";

import React from "react";
import styles from "./Badge.module.css";

/**
 * Reusable Badge/chip primitive.
 * @param {string} variant - "default" | "orange" | "dark"
 */
export default function Badge({ children, variant = "default", className = "" }) {
  const variantClass = styles[variant] ?? styles.default;

  return (
    <span className={`${styles.badge} ${variantClass} ${className}`.trim()}>
      {children}
    </span>
  );
}
