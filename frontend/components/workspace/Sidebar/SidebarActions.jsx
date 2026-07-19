"use client";

import React from "react";
import SearchChats from "./SearchChats";
import styles from "./Sidebar.module.css";

export default function SidebarActions({
  searchQuery,
  onSearchChange,
  onNewChat,
  isCollapsed
}) {
  return (
    <div className={`${styles.actionsContainer} ${isCollapsed ? styles.actionsContainerCollapsed : ""}`}>
      {/* 1. New Chat Button */}
      <button
        onClick={onNewChat}
        className={isCollapsed ? styles.newChatBtnCollapsed : styles.newChatBtnLarge}
        title="Start New Chat Session"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={2.5}
          stroke="currentColor"
          className={styles.btnIcon}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
        {!isCollapsed && <span>New Chat</span>}
      </button>

      {/* 2. Search Input */}
      {!isCollapsed ? (
        <SearchChats query={searchQuery} onQueryChange={onSearchChange} />
      ) : (
        <button
          className={styles.searchIconBtnCollapsed}
          title="Search Chats"
          aria-label="Search Chats"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
            className={styles.btnIcon}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
            />
          </svg>
        </button>
      )}
    </div>
  );
}
