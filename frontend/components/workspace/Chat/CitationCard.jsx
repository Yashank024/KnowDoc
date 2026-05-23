"use client";

import React from "react";
import Badge from "../../ui/Badge/Badge";
import styles from "./Chat.module.css";

export default function CitationCard({ docIndex, pageIndex, onClick }) {
  return (
    <Badge
      variant="orange"
      className={styles.citationCard}
      onClick={onClick}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={2.5}
        stroke="currentColor"
        width={10}
        height={10}
        className={styles.linkIcon}
      >
        <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
      </svg>
      <span>Ref {docIndex} • P.{pageIndex}</span>
    </Badge>
  );
}
