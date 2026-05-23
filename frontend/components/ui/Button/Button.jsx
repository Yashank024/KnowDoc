"use client";

import React from "react";
import styles from "./Button.module.css";

/**
 * Reusable Button primitive.
 * @param {string} variant - "primary" | "secondary" | "icon"
 */
export default function Button({
  id,
  type     = "button",
  variant  = "primary",
  onClick,
  disabled = false,
  className = "",
  children,
  ...props
}) {
  const variantClass = styles[variant] ?? styles.primary;

  return (
    <button
      id={id}
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${styles.base} ${variantClass} ${className}`.trim()}
      {...props}
    >
      {children}
    </button>
  );
}
