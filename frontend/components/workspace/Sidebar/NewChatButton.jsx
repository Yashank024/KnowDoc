"use client";

import React from "react";
import styles from "./Sidebar.module.css";

export default function NewChatButton({ onNewChat }) {
  return (
    <button onClick={onNewChat} className={styles.newChatBtnLarge}>
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
        strokeWidth={2.5} stroke="currentColor" className={styles.btnIcon}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
      </svg>
      <span>New Chat</span>
    </button>
  );
}
