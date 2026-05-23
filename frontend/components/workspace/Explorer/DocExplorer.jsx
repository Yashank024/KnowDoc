"use client";

import React, { useState, useRef } from "react";
import { uploadDocumentToOCR } from "../../../lib/api";
import styles from "./DocExplorer.module.css";

/**
 * DocExplorer — Dynamic Google Drive/Notion caliber Document Intelligence Dashboard.
 * Lists global indexed files, dynamically tags them, searches, filters, and uploads directly.
 */
export default function DocExplorer({
  documents,
  onAddDocument,
  onSelectDoc,
  onDeleteDoc,
  onClose
}) {
  const [selectedTag, setSelectedTag] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  // Parse total size for the statistics banner
  const totalFiles = documents.length;
  const totalSizeMB = documents.reduce((sum, doc) => {
    const sizeStr = doc.size || "1.0 MB";
    const num = parseFloat(sizeStr.replace(/[^0-9.]/g, ""));
    const isKB = sizeStr.toLowerCase().includes("kb");
    const value = isNaN(num) ? 1.0 : num;
    return sum + (isKB ? value / 1024 : value);
  }, 0).toFixed(2);

  // Compute all unique tags across all documents dynamically
  const uniqueTags = Array.from(
    new Set(documents.flatMap((doc) => doc.tags || []))
  ).filter(Boolean);

  // Filter documents by active tag and active local search query
  const filteredDocs = documents.filter((doc) => {
    const matchesTag =
      selectedTag === "All" || (doc.tags && doc.tags.includes(selectedTag));
    const matchesSearch =
      doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (doc.full_text && doc.full_text.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesTag && matchesSearch;
  });

  // Calculate tag item counts
  function getTagCount(tag) {
    if (tag === "All") return documents.length;
    return documents.filter((d) => d.tags && d.tags.includes(tag)).length;
  }

  // Trigger file selection input
  function triggerFileSelect() {
    fileInputRef.current?.click();
  }

  // File upload processing with local PaddleOCR integration
  async function handleFileChange(e) {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    await processFile(files[0]);
    e.target.value = "";
  }

  async function processFile(file) {
    const allowed = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".pdf"];
    const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();

    if (!allowed.includes(ext)) {
      alert("Unsupported file format. Please upload images or PDFs.");
      return;
    }

    setUploadStatus("Uploading");

    try {
      await new Promise((r) => setTimeout(r, 200));

      const uploadResult = await uploadDocumentToOCR(file);
      setUploadStatus("Success!");

      // Generate soft dynamic AI tags based on keywords or file type
      const filenameLower = file.name.toLowerCase();
      let generatedTags = ["Uploaded"];
      if (filenameLower.includes("invoice") || filenameLower.includes("receipt") || filenameLower.includes("bill")) {
        generatedTags = ["Finance", "Invoices"];
      } else if (filenameLower.includes("policy") || filenameLower.includes("rule") || filenameLower.includes("handbook")) {
        generatedTags = ["HR", "Policies", "Legal"];
      } else if (filenameLower.includes("tax") || filenameLower.includes("form") || filenameLower.includes("1040")) {
        generatedTags = ["Finance", "Tax"];
      } else if (ext === ".pdf") {
        generatedTags = ["PDF", "Documents"];
      } else {
        generatedTags = ["Image", "Analysis"];
      }

      onAddDocument({
        id: uploadResult.document_id,
        filename: file.name,
        size: uploadResult.size,
        text_lines: [],
        full_text: "",
        tags: uploadResult.tags || generatedTags,
        status: "uploading"
      });

      setTimeout(() => setUploadStatus(null), 1000);
    } catch (err) {
      console.error(err);
      setUploadStatus("Error");
      alert(err.message || "Failed to communicate with FastAPI server.");
      setUploadStatus(null);
    }
  }

  // Drag and Drop event handlers
  function handleDragOver(e) {
    e.preventDefault();
    setIsDragOver(true);
  }

  function handleDragLeave() {
    setIsDragOver(false);
  }

  async function handleDrop(e) {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      await processFile(files[0]);
    }
  }

  // Get format icons dynamically
  function getFormatBadge(filename) {
    const ext = filename.substring(filename.lastIndexOf(".")).toLowerCase();
    if (ext === ".pdf") {
      return { label: "PDF", bg: "#FCE8E6", color: "#C53929", border: "rgba(197, 57, 41, 0.15)" };
    } else if ([".png", ".jpg", ".jpeg", ".bmp", ".tiff"].includes(ext)) {
      return { label: "IMG", bg: "#E8F0FE", color: "#1A73E8", border: "rgba(26, 115, 232, 0.15)" };
    }
    return { label: "DOC", bg: "#E6F4EA", color: "#137333", border: "rgba(19, 115, 51, 0.15)" };
  }

  return (
    <div className={styles.explorerOverlay}>
      {/* Dynamic Header Panel */}
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <h1 className={styles.title}>Global Document Memory</h1>
          <p className={styles.subtitle}>
            AI auto-indexing database active on **PaddleOCR** layout parsing
          </p>
        </div>
        <div className={styles.headerRight}>
          <div className={styles.statsBadge}>
            <span className={styles.statsLabel}>Total Index:</span>
            <span className={styles.statsValue}>{totalFiles} files</span>
            <span className={styles.statsDivider} />
            <span className={styles.statsValue}>{totalSizeMB} MB</span>
          </div>
          <button onClick={onClose} className={styles.backBtn} title="Back to Chat Mode">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2.5}
              stroke="currentColor"
              width={16}
              height={16}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 15L3 9m0 0l6-6M3 9h12a6 6 0 010 12h-3" />
            </svg>
            <span>Back to Chat</span>
          </button>
        </div>
      </header>

      {/* Main Core Layout: Sidebar and Catalog Grid */}
      <div className={styles.mainLayout}>
        
        {/* Dynamic Sidebar Tags Navigator */}
        <aside className={styles.sidebar}>
          <div className={styles.searchBox}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
              className={styles.searchIcon}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.602 10.602Z" />
            </svg>
            <input
              type="text"
              placeholder="Search index..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={styles.searchInput}
            />
          </div>

          <nav className={styles.nav}>
            <div className={styles.navHeader}>DYNAMIC AI TAGS</div>
            <button
              onClick={() => setSelectedTag("All")}
              className={`${styles.navItem} ${selectedTag === "All" ? styles.navItemActive : ""}`}
            >
              <span className={styles.navItemName}>All Memory</span>
              <span className={styles.navItemCount}>{getTagCount("All")}</span>
            </button>

            {uniqueTags.map((tag) => (
              <button
                key={tag}
                onClick={() => setSelectedTag(tag)}
                className={`${styles.navItem} ${selectedTag === tag ? styles.navItemActive : ""}`}
              >
                <span className={styles.navItemName}>#{tag}</span>
                <span className={styles.navItemCount}>{getTagCount(tag)}</span>
              </button>
            ))}
          </nav>

          {/* Quick-Upload inside Explorer Sidebar */}
          <div className={styles.uploadBlock}>
            <button
              onClick={triggerFileSelect}
              className={styles.sidebarUploadBtn}
              disabled={uploadStatus !== null}
            >
              {uploadStatus ? (
                <>
                  <span className={styles.spinner} />
                  <span>{uploadStatus}</span>
                </>
              ) : (
                <>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={2.5}
                    stroke="currentColor"
                    width={15}
                    height={15}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                  </svg>
                  <span>Upload Document</span>
                </>
              )}
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              className="hidden"
              accept=".jpg,.jpeg,.png,.bmp,.tiff,.pdf"
            />
          </div>
        </aside>

        {/* Dynamic Grid Catalog Workspace */}
        <main
          className={`${styles.catalogArea} ${isDragOver ? styles.catalogDragOver : ""}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {isDragOver && (
            <div className={styles.dragOverModal}>
              <div className={styles.dragOverContent}>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className={styles.dragIcon}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z"
                  />
                </svg>
                <h3>Drop files to index directly!</h3>
                <p>Images and PDF files will be immediately processed with layout-aware OCR.</p>
              </div>
            </div>
          )}

          {filteredDocs.length === 0 ? (
            <div className={styles.emptyGrid}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1}
                stroke="currentColor"
                className={styles.emptyIcon}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"
                />
              </svg>
              <h3>No Indexed Documents Found</h3>
              <p>
                {searchQuery
                  ? `No results match your search "${searchQuery}".`
                  : `There are no active files categorized under dynamic tag "${selectedTag}".`}
              </p>
              <button onClick={triggerFileSelect} className={styles.emptyGridUploadBtn}>
                Upload First File
              </button>
            </div>
          ) : (
            <div className={styles.grid}>
              {filteredDocs.map((doc) => {
                const badge = getFormatBadge(doc.filename);
                const blockCount = doc.text_lines?.length || 0;
                const isProcessing = doc.status === "uploading" || doc.status === "processing" || doc.status === "indexing";
                
                return (
                  <div key={doc.id} className={`${styles.card} ${isProcessing ? styles.cardProcessing : ""}`}>
                    {/* Format Badge & File Metadata */}
                    <div className={styles.cardHeader}>
                      <span
                        className={styles.formatBadge}
                        style={{
                          backgroundColor: isProcessing ? "rgba(217,91,36,0.08)" : badge.bg,
                          color: isProcessing ? "var(--accent-orange)" : badge.color,
                          borderColor: isProcessing ? "rgba(217, 91, 36, 0.15)" : badge.border
                        }}
                      >
                        {isProcessing ? doc.status : badge.label}
                      </span>
                      <span className={styles.cardDate}>{doc.date}</span>
                    </div>

                    {/* File Title */}
                    <h3 className={styles.cardTitle} title={doc.filename} style={isProcessing ? { opacity: 0.7 } : {}}>
                      {doc.filename}
                    </h3>

                    {/* OCR Stats Sub-row */}
                    <div className={styles.cardMeta}>
                      <span className={styles.metaItem}>Size: {doc.size || "1.0 MB"}</span>
                      <span className={styles.metaDivider} />
                      <span className={styles.metaItem}>
                        {isProcessing ? "Processing..." : `${blockCount} text blocks`}
                      </span>
                    </div>

                    {/* Dynamic Auto-tags badge pills */}
                    <div className={styles.tagsContainer}>
                      {isProcessing ? (
                        <span className={styles.processingTagPill}>#indexing</span>
                      ) : (
                        doc.tags?.map((tag) => (
                          <span key={tag} className={styles.tagPill}>
                            #{tag}
                          </span>
                        ))
                      )}
                    </div>

                    {/* Footer Action Row */}
                    <div className={styles.cardFooter}>
                      <button
                        onClick={isProcessing ? undefined : () => onSelectDoc(doc)}
                        className={styles.inspectBtn}
                        disabled={isProcessing}
                        style={isProcessing ? { cursor: "not-allowed", opacity: 0.5 } : {}}
                        title={isProcessing ? "Processing document..." : "Open in visual inspector"}
                      >
                        {isProcessing ? (
                          <span className={styles.cardSpinner} />
                        ) : (
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                            strokeWidth={2}
                            stroke="currentColor"
                            width={14}
                            height={14}
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                            <circle cx="12" cy="12" r="3" />
                          </svg>
                        )}
                        <span>Inspect</span>
                      </button>

                      <button
                        onClick={isProcessing ? undefined : () => {
                          if (confirm(`Are you sure you want to delete ${doc.filename} from global AI memory?`)) {
                            onDeleteDoc(doc.id);
                          }
                        }}
                        className={styles.deleteBtn}
                        disabled={isProcessing}
                        style={isProcessing ? { cursor: "not-allowed", opacity: 0.5 } : {}}
                        title={isProcessing ? "Processing document..." : "Erase from system database indexing"}
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                          strokeWidth={2}
                          stroke="currentColor"
                          width={14}
                          height={14}
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                        </svg>
                        <span>Erase</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
