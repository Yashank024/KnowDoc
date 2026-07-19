"use client";

import React from "react";
import RecentChatItem from "./RecentChatItem";
import styles from "./Sidebar.module.css";

export default function RecentChats({
  chats,
  activeChat,
  onSelectChat,
  onRenameChat,
  onDeleteChat,
  onShareChat,
  isCollapsed
}) {
  return (
    <div className={`${styles.recentChatsSection} ${isCollapsed ? styles.recentChatsSectionCollapsed : ""}`}>
      {!isCollapsed && <span className={styles.sectionLabel}>Recent Chats</span>}
      <div className={styles.recentList}>
        {chats.length > 0 ? (
          chats.map((chat) => (
            <RecentChatItem
              key={chat.id}
              chat={chat}
              isActive={chat.id === activeChat}
              onSelectChat={onSelectChat}
              onRenameChat={onRenameChat}
              onDeleteChat={onDeleteChat}
              onShareChat={onShareChat}
              isCollapsed={isCollapsed}
            />
          ))
        ) : (
          !isCollapsed && <div className={styles.recentEmpty}>No chat history.</div>
        )}
      </div>
    </div>
  );
}
