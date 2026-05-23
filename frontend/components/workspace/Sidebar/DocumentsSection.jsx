"use client";

import React, { useRef, useState } from "react";
import { uploadDocumentToOCR } from "../../../lib/api";
import styles from "./DocumentsSection.module.css";

export default function DocumentsSection({
  documents,
  onSelectDoc,
  onAddDocument,
  activeDoc,
  isCollapsed,
  onViewAll
}) {
  const fileInputRef = useRef(null);
  const [uploadStatus, setUploadStatus] = useState(null);

  // Take top 3 documents as recent uploads
  const recentDocs = documents.slice(0, 3);

  function triggerFileSelect() {
    fileInputRef.current?.click();
  }

  async function handleFileChange(e) {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    const allowed = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".pdf"];
    const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();

    if (!allowed.includes(ext)) {
      alert("Unsupported file format. Please upload images or PDFs.");
      return;
    }

    setUploadStatus("Uploading");

    try {
      // Simulate quick connection step
      await new Promise((r) => setTimeout(r, 200));
      
      const uploadResult = await uploadDocumentToOCR(file);
      setUploadStatus("Success!");

      onAddDocument({
        id: uploadResult.document_id,
        filename: file.name,
        size: uploadResult.size,
        tags: uploadResult.tags,
        text_lines: [],
        full_text: "",
        status: "uploading"
      });

      setTimeout(() => setUploadStatus(null), 1000);
    } catch (err) {
      console.error(err);
      setUploadStatus("Error");
      alert(err.message || "Failed to communicate with FastAPI server.");
      setUploadStatus(null);
    } finally {
      e.target.value = "";
    }
  }

  if (isCollapsed) {
    return (
      <div className={styles.containerCollapsed}>
        {/* Upload Trigger */}
        <button
          onClick={triggerFileSelect}
          className={styles.collapsedBtn}
          title="Upload Document"
          disabled={uploadStatus !== null}
        >
          {uploadStatus ? (
            <span className={styles.collapsedProgressRing} />
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2.5}
              stroke="currentColor"
              className={styles.collapsedIcon}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
          )}
        </button>

        {/* View Explorer Trigger */}
        <button
          onClick={onViewAll}
          className={styles.collapsedBtn}
          title="View All Documents"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
            className={styles.collapsedIcon}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 8.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25a2.25 2.25 0 0 1-2.25 2.25h-2.25A2.25 2.25 0 0 1 13.5 8.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z"
            />
          </svg>
        </button>

        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          accept=".jpg,.jpeg,.png,.bmp,.tiff,.pdf"
        />
      </div>
    );
  }

  return (
    <div className={styles.section}>
      {/* Header title */}
      <div className={styles.header}>
        <div className={styles.headerTitle}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
            width={15}
            height={15}
            className={styles.headerIcon}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"
            />
          </svg>
          <span>Documents</span>
        </div>
        <button
          onClick={onViewAll}
          className={styles.viewAllBtn}
          title="Open Document Explorer Dashboard"
        >
          View All →
        </button>
      </div>

      {/* Upload button wrapper */}
      <div className={styles.uploadWrapper}>
        <button
          onClick={triggerFileSelect}
          className={styles.uploadBtn}
          disabled={uploadStatus !== null}
        >
          {uploadStatus ? (
            <span className={styles.uploadLoadingText}>
              <span className={styles.spinner} />
              {uploadStatus}
            </span>
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

      {/* Recent files list */}
      <div className={styles.list}>
        <div className={styles.listTitle}>Recent Uploads</div>
        {recentDocs.length === 0 ? (
          <div className={styles.emptyState}>No documents uploaded yet</div>
        ) : (
          recentDocs.map((doc) => {
            const isActive = activeDoc && activeDoc.id === doc.id;
            const isProcessing = doc.status === "uploading" || doc.status === "processing" || doc.status === "indexing";
            return (
              <div
                key={doc.id}
                onClick={isProcessing ? undefined : () => onSelectDoc(doc)}
                className={`${styles.item} ${isActive ? styles.itemActive : ""} ${isProcessing ? styles.itemProcessing : ""}`}
                style={isProcessing ? { cursor: "not-allowed", opacity: 0.85 } : {}}
                title={isProcessing ? `Document is currently ${doc.status}. Please wait...` : "Click to view document in Inspector"}
              >
                <div className={styles.itemMeta}>
                  {isProcessing ? (
                    <span className={styles.itemSpinner} />
                  ) : (
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={2}
                      stroke="currentColor"
                      className={styles.itemIcon}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"
                      />
                    </svg>
                  )}
                  <span className={styles.fileName}>{doc.filename}</span>
                </div>
                {isProcessing ? (
                  <span className={styles.statusBadge}>{doc.status === "uploading" ? "uploading" : doc.status === "processing" ? "parsing" : "indexing"}</span>
                ) : (
                  <span className={styles.fileDate}>{doc.date}</span>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
