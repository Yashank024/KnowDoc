"use client";

import React, { useState, useEffect } from "react";
import SourceCard       from "./SourceCard";
import PDFOpener       from "./PDFOpener";
import CitationPreview from "./CitationPreview";
import RawTextList     from "./RawTextList";
import ViewerDrawer    from "./ViewerDrawer";
import styles from "./Viewer.module.css";

const TABS = [
  { id: "preview",  label: "Visual Canvas" },
  { id: "raw_text", label: "Extracted Text" }
];

/**
 * DocViewer — master Slide-Over "Canvas" drawer component.
 * Coordinates: slide-in/out transition parameters, raw lists, SVG overlays, and close buttons.
 */
export default function DocViewer({
  activeDoc,
  selectedCitation,
  isDrawerOpen,
  onClose
}) {
  const [activeTab, setActiveTab] = useState("preview");
  const [highlightedIndex, setHighlightedIndex] = useState(null);

  useEffect(() => {
    if (selectedCitation && activeDoc?.text_lines) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setHighlightedIndex(0);
      setActiveTab("preview");
    } else {
      setHighlightedIndex(null);
    }
  }, [selectedCitation, activeDoc]);

  return (
    <div
      className={`${styles.slideDrawer} ${
        isDrawerOpen ? styles.slideDrawerOpen : ""
      }`}
    >
      {/* Drawer Header Row */}
      <div className={styles.drawerHeader}>
        <div className={styles.headerTitleRow}>
          <span className={styles.drawerTitle}>Document Inspector</span>
          <button
            onClick={onClose}
            className={styles.closeBtn}
            title="Close Drawer"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2.5}
              stroke="currentColor"
              width={16}
              height={16}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {activeDoc && (
          <div className={styles.tabsRow}>
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${styles.tabBtn} ${
                  activeTab === tab.id ? styles.tabBtnActive : ""
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Drawer Core Canvas */}
      {activeDoc ? (
        <div className={styles.drawerBody}>
          <SourceCard file={activeDoc} />
          
          <PDFOpener filename={activeDoc.filename} />

          <hr className={styles.divider} />

          <div className={styles.tabContent}>
            {activeTab === "preview" && (
              <CitationPreview
                activeDoc={activeDoc}
                highlightedIndex={highlightedIndex}
                onSelectHighlight={setHighlightedIndex}
              />
            )}
            
            {activeTab === "raw_text" && (
              <RawTextList
                textLines={activeDoc.text_lines}
                highlightedIndex={highlightedIndex}
                onSelect={(idx) => {
                  setHighlightedIndex(idx);
                  setActiveTab("preview");
                }}
              />
            )}
          </div>

          <hr className={styles.divider} />

          {/* Coordinate details */}
          <ViewerDrawer
            textLines={activeDoc.text_lines}
            highlightedIndex={highlightedIndex}
          />
        </div>
      ) : (
        <div className={styles.drawerEmptyContainer}>
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
              d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
            />
          </svg>
          <p className={styles.emptyLabel}>No Document Selected</p>
          <p className={styles.emptySubtitle}>
            Click a document in the sidebar folder, or citation in chat messages, to inspect layout coordinates.
          </p>
        </div>
      )}
    </div>
  );
}
