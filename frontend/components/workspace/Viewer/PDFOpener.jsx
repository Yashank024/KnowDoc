"use client";

import React from "react";
import styles from "./Viewer.module.css";

export default function PDFOpener({ filename }) {
  function handleOpen() {
    // Open a blank tab with a descriptive simulated window to fit conversational navigation
    const win = window.open("", "_blank");
    if (win) {
      win.document.write(`
        <html>
          <head>
            <title>Original Document: ${filename}</title>
            <style>
              body {
                background-color: #F3E7D3;
                color: #111111;
                font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
              }
              .box {
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.05);
                text-align: center;
                max-width: 450px;
              }
              h1 { color: #0F6A5B; font-size: 20px; margin-bottom: 12px; }
              p { font-size: 13px; color: rgba(0,0,0,0.6); line-height: 1.5; }
              .badge {
                background-color: #D95B24;
                color: white;
                font-size: 10px;
                font-weight: 700;
                padding: 4px 10px;
                border-radius: 999px;
                text-transform: uppercase;
                display: inline-block;
                margin-top: 16px;
              }
            </style>
          </head>
          <body>
            <div class="box">
              <h1>📄 Opening Original Document</h1>
              <p>Simulating original high-resolution PDF rendering for <strong>${filename}</strong> inside separate secure browser tab.</p>
              <div class="badge">PaddleOCR Connected</div>
            </div>
          </body>
        </html>
      `);
      win.document.close();
    }
  }

  return (
    <button onClick={handleOpen} className={styles.pdfOpenerBtn}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={2}
        stroke="currentColor"
        width={14}
        height={14}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"
        />
      </svg>
      <span>Open Original PDF</span>
    </button>
  );
}
