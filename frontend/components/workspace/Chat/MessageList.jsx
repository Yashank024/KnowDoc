"use client";

import React from "react";
import MessageBubble from "./MessageBubble";
import styles from "./Chat.module.css";

export default function MessageList({ messages, documents, onSelectCitation, scrollRef }) {
  if (messages.length === 0) {
    return null;
  }

  return (
    <div className={styles.messageList}>
      {messages.map((msg, idx) => (
        <MessageBubble
          key={msg.id || idx}
          msg={msg}
          documents={documents}
          onSelectCitation={onSelectCitation}
        />
      ))}
      <div ref={scrollRef} />
    </div>
  );
}
