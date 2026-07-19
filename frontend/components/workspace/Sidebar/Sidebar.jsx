"use client";

import React, { useState } from "react";
import SidebarHeader     from "./SidebarHeader";
import SidebarActions    from "./SidebarActions";
import DocumentsSection  from "./DocumentsSection";
import RecentChats       from "./RecentChats";
import AccountSection    from "./AccountSection";
import styles            from "./Sidebar.module.css";

/**
 * Sidebar — master layout coordinator for the memory panels.
 * Features: collapsible states, search triggers, recent global uploads, and ChatGPT actions.
 */
export default function Sidebar({
  documents,
  activeDoc,
  onSelectDoc,
  onAddDocument,
  chats,
  activeChat,
  onSelectChat,
  onNewChat,
  onRenameChat,
  onDeleteChat,
  onShareChat,
  viewMode,
  onViewAll,
  isCollapsed: controlledIsCollapsed,
  onToggleCollapse: controlledOnToggleCollapse,
  onOpenSettings
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [localIsCollapsed, setLocalIsCollapsed] = useState(false);

  const isCollapsed = controlledIsCollapsed !== undefined ? controlledIsCollapsed : localIsCollapsed;
  const setIsCollapsed = controlledOnToggleCollapse !== undefined ? controlledOnToggleCollapse : setLocalIsCollapsed;

  // Filters chats by title matching search query
  const filteredChats = chats.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <aside className={`${styles.aside} ${isCollapsed ? styles.asideCollapsed : ""}`}>
      {/* Top Branding & Control Panel */}
      <div className={styles.topContainer}>
        <SidebarHeader
          isCollapsed={isCollapsed}
          onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
        />
        
        <SidebarActions
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onNewChat={onNewChat}
          isCollapsed={isCollapsed}
        />
      </div>

      {/* Middle Scrollable Memory Panels */}
      <div className={styles.middleContainer}>
        <DocumentsSection
          documents={documents}
          activeDoc={activeDoc}
          onSelectDoc={onSelectDoc}
          onAddDocument={onAddDocument}
          isCollapsed={isCollapsed}
          onViewAll={onViewAll}
        />
        
        <RecentChats
          chats={filteredChats}
          activeChat={activeChat}
          onSelectChat={onSelectChat}
          onRenameChat={onRenameChat}
          onDeleteChat={onDeleteChat}
          onShareChat={onShareChat}
          isCollapsed={isCollapsed}
        />
      </div>

      {/* Bottom Profile Section */}
      <AccountSection isCollapsed={isCollapsed} onOpenSettings={onOpenSettings} />
    </aside>
  );
}
