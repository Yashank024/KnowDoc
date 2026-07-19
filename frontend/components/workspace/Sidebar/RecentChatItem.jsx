"use client";

import React, { useState, useRef } from "react";
import ChatMenu from "./ChatMenu";
import styles from "./Sidebar.module.css";

export default function RecentChatItem({
  chat,
  isActive,
  onSelectChat,
  onRenameChat,
  onDeleteChat,
  onShareChat,
  isCollapsed
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [menuPos, setMenuPos] = useState({ top: 0, left: 0 });

  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(chat.title);

  const triggerRef = useRef(null);

  const handleMenuTrigger = (e) => {
    e.stopPropagation();
    const rect = e.currentTarget.getBoundingClientRect();
    // Position menu offset below and aligned left
    setMenuPos({
      top: rect.bottom + window.scrollY + 4,
      left: rect.left + window.scrollX - 110
    });
    setMenuOpen(!menuOpen);
  };

  const handleRenameSubmit = (e) => {
    e.preventDefault();
    if (editTitle.trim() && editTitle.trim() !== chat.title) {
      onRenameChat(chat.id, editTitle.trim());
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Escape") {
      setEditTitle(chat.title);
      setIsEditing(false);
    }
  };

  return (
    <div
      onClick={() => !isEditing && onSelectChat(chat.id)}
      className={`${styles.recentItem} ${isActive ? styles.recentItemActive : ""} ${isCollapsed ? styles.recentItemCollapsed : ""}`}
      title={isCollapsed ? chat.title : ""}
    >
      <div className={styles.recentLeft}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={2}
          stroke="currentColor"
          className={`${styles.chatIcon} ${isActive ? styles.chatIconActive : ""}`}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 011.037-.443 48.282 48.282 0 005.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z"
          />
        </svg>

        {!isCollapsed && (
          <div style={{ flex: 1, minWidth: 0 }}>
            {isEditing ? (
              <form onSubmit={handleRenameSubmit} onClick={(e) => e.stopPropagation()} style={{ width: "100%" }}>
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  onBlur={handleRenameSubmit}
                  onKeyDown={handleKeyDown}
                  className={styles.renameInput}
                  autoFocus
                />
              </form>
            ) : (
              <span className={styles.recentTitle}>{chat.title}</span>
            )}
          </div>
        )}
      </div>

      {!isCollapsed && !isEditing && (
        <div className={styles.recentRight}>
          {chat.timestamp && !menuOpen && (
            <span className={styles.recentTime}>{chat.timestamp}</span>
          )}
          <button
            ref={triggerRef}
            onClick={handleMenuTrigger}
            className={styles.menuTriggerBtn}
            title="Chat Options"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2.5}
              stroke="currentColor"
              width={13}
              height={13}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6.75 12a.75.75 0 11-1.5 0 .75.75 0 011.5 0zM12.75 12a.75.75 0 11-1.5 0 .75.75 0 011.5 0zM18.75 12a.75.75 0 11-1.5 0 .75.75 0 011.5 0z"
              />
            </svg>
          </button>
        </div>
      )}

      {/* Popover options menu */}
      <ChatMenu
        isOpen={menuOpen}
        onClose={() => setMenuOpen(false)}
        position={menuPos}
        onRename={() => setIsEditing(true)}
        onShare={() => onShareChat(chat.id)}
        onDelete={() => onDeleteChat(chat.id)}
      />
    </div>
  );
}
