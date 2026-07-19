"use client";

import React from "react";
import styles from "./Sidebar.module.css";

export default function SidebarHeader({ isCollapsed, onToggleCollapse }) {
  return (
    <div className={`${styles.brandRow} ${isCollapsed ? styles.brandRowCollapsed : ""}`}>
      <div className={styles.brandLeft}>
        <img src="/logo_symbol.png" alt="KnowDoc" className={styles.brandLogo} />
        {!isCollapsed && (
          <div className={styles.brandLabelContainer}>
            <span className={styles.brandLabel}>KnowDoc</span>
            <span className={styles.brandSubtitle}>AI Workspace</span>
          </div>
        )}
      </div>
      
      <button
        onClick={onToggleCollapse}
        className={styles.collapseBtn}
        title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        aria-label="Toggle Sidebar"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={2.5}
          stroke="currentColor"
          className={`${styles.collapseIcon} ${isCollapsed ? styles.collapseIconRotated : ""}`}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
        </svg>
      </button>
    </div>
  );
}
