"use client";

import React, { useState } from "react";
import { resetDatabase } from "../../lib/api";
import styles from "./SettingsModal.module.css";

export default function SettingsModal({ isOpen, onClose, onResetSuccess }) {
  const [isConfirming, setIsConfirming] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  if (!isOpen) return null;

  const handleResetClick = () => {
    setIsConfirming(true);
  };

  const handleCancelConfirm = () => {
    setIsConfirming(false);
  };

  const handleClose = () => {
    // Reset states back to initial when closing
    setIsConfirming(false);
    setIsSuccess(false);
    setIsLoading(false);
    setError(null);
    setStats(null);
    onClose();
  };

  const executeReset = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await resetDatabase();
      if (response.success) {
        setStats(response);
        setIsSuccess(true);
        // Trigger parent workspace state wipeout and rebuild
        if (onResetSuccess) {
          onResetSuccess(response);
        }
      } else {
        setError({
          stage: response.stage || "Execution",
          error: response.error || "An unknown error occurred during database reset."
        });
      }
    } catch (err) {
      console.error("[SettingsModal] Error resetting database:", err);
      // Determine if error contains detail stage
      const stage = err.stage || "API Call";
      const errorMsg = err.error || err.message || "Failed to communicate with reset API.";
      setError({ stage, error: errorMsg });
    } finally {
      setIsLoading(false);
      setIsConfirming(false);
    }
  };

  return (
    <div className={styles.overlay} onClick={!isLoading ? handleClose : undefined}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        
        {/* Header */}
        <div className={styles.header}>
          <h2 className={isConfirming ? styles.confirmTitle : styles.title}>
            {isLoading ? "Resetting System..." : isSuccess ? "Reset Successful" : isConfirming ? "Dangerous Action Confirmation" : "Settings"}
          </h2>
          {!isLoading && (
            <button className={styles.closeButton} onClick={handleClose} aria-label="Close settings">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" width={18} height={18}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Body Content */}
        <div className={styles.content}>
          {isLoading ? (
            <div className={styles.loadingContainer}>
              <div className={styles.spinner}></div>
              <p className={styles.loadingText}>Resetting database...</p>
            </div>
          ) : isSuccess ? (
            <div className={styles.successContainer}>
              <div className={styles.successHeader}>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width={22} height={22}>
                  <path fillRule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm13.36-1.814a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.74-5.24z" clipRule="evenodd" />
                </svg>
                <span>Database successfully reset.</span>
              </div>
              <div className={styles.successList}>
                <div className={styles.successItem}>
                  <span className={styles.checkmark}>✓</span>
                  <span>Upload storage cleared ({stats?.deleted_uploaded_files ?? 0} files)</span>
                </div>
                <div className={styles.successItem}>
                  <span className={styles.checkmark}>✓</span>
                  <span>OCR cache cleared</span>
                </div>
                <div className={styles.successItem}>
                  <span className={styles.checkmark}>✓</span>
                  <span>Vector database reset ({stats?.deleted_vectors ?? 0} vectors)</span>
                </div>
                <div className={styles.successItem}>
                  <span className={styles.checkmark}>✓</span>
                  <span>Runtime cache cleared</span>
                </div>
                <div className={styles.successItem}>
                  <span className={styles.checkmark}>✓</span>
                  <span>Memory released</span>
                </div>
              </div>
              <p style={{ fontSize: "0.85rem", color: "#666", marginTop: "0.5rem" }}>
                The workspace interface has been re-synchronized.
              </p>
              <div className={styles.actions} style={{ marginTop: "1rem" }}>
                <button className={styles.btnCancel} onClick={handleClose}>
                  Done
                </button>
              </div>
            </div>
          ) : isConfirming ? (
            <div>
              <p><strong>Are you absolutely sure?</strong></p>
              <p style={{ marginTop: "0.5rem" }}>This action will permanently delete:</p>
              <ul className={styles.bulletList}>
                <li>Uploaded PDFs</li>
                <li>OCR cache</li>
                <li>Parsed documents</li>
                <li>Vector database</li>
                <li>Chroma collections</li>
                <li>Runtime cache</li>
                <li>Conversation metadata</li>
              </ul>
              <p style={{ color: "var(--accent-orange)", fontWeight: 600, marginTop: "0.5rem" }}>
                This cannot be undone.
              </p>
              <div className={styles.actions} style={{ marginTop: "1.5rem" }}>
                <button className={styles.btnCancel} onClick={handleCancelConfirm}>
                  Cancel
                </button>
                <button className={styles.btnDelete} onClick={executeReset}>
                  Yes, Delete Everything
                </button>
              </div>
            </div>
          ) : (
            <div>
              {/* Show error if one occurred in a previous attempt */}
              {error && (
                <div className={styles.errorContainer}>
                  <div className={styles.errorTitle}>⚠ Reset Failed: {error.stage}</div>
                  <div className={styles.errorDesc}>{error.error}</div>
                </div>
              )}

              {/* Configuration Section */}
              <div className={styles.infoSection}>
                <div className={styles.infoItem}>
                  <span className={styles.infoLabel}>PaddleOCR API:</span>
                  <span className={styles.infoValue}>Cloud API (VL-1.6)</span>
                </div>
                <div className={styles.infoItem}>
                  <span className={styles.infoLabel}>Embeddings Scope:</span>
                  <span className={styles.infoValue}>Folder Isolated (RAG)</span>
                </div>
                <div className={styles.infoItem}>
                  <span className={styles.infoLabel}>LLM Model:</span>
                  <span className={styles.infoValue}>OpenRouter (Tencent Hunyuan 3)</span>
                </div>
                <div className={styles.infoItem}>
                  <span className={styles.infoLabel}>Theme Style:</span>
                  <span className={styles.infoValue}>Champagne Mist Premium Light</span>
                </div>
              </div>

              {/* Danger Zone */}
              <div className={styles.dangerZone}>
                <div className={styles.dangerHeader}>
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" width={18} height={18}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                  </svg>
                  <span>⚠ Danger Zone</span>
                </div>
                <div className={styles.dangerDesc}>
                  This will permanently remove every uploaded document, all OCR results, all vector embeddings, all cached runtime data, and reset the application database. This action cannot be undone.
                </div>
                <div className={styles.actions}>
                  <button className={styles.btnDelete} onClick={handleResetClick}>
                    Delete All Data
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
