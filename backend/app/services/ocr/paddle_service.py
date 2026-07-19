"""
PaddleOCR Cloud API Service — Clean Rebuild.

Single responsibility: Submit a file to PaddleOCR-VL-1.6 Cloud API,
poll until complete, download JSONL, extract markdown text.

No coordinate parsing. No bounding boxes. No fallback chains.
Returns a simple PaddleResult dataclass.
"""

import os
import json
import time
import logging
import requests

from dataclasses import dataclass, field
from typing import List
from app.core import config

logger = logging.getLogger("paddle_service")

JOB_URL = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"
MODEL = "PaddleOCR-VL-1.6"
POLL_INTERVAL_SEC = 5
MAX_POLL_ATTEMPTS = 120  # 10 minutes


@dataclass
class PaddleResult:
    success: bool
    error: str = ""
    raw_jsonl: str = ""
    pages: List[dict] = field(default_factory=list)
    # Aggregated across all pages
    markdown: str = ""
    text_lines: List[str] = field(default_factory=list)
    page_count: int = 0


def run(file_path: str) -> PaddleResult:
    """
    Submit file_path to PaddleOCR Cloud API.
    Poll until done, download JSONL, extract markdown text_lines.
    Logs the full raw JSONL to the console before any parsing.
    """
    token = config.PADDLEOCR_API_KEY
    if not token:
        return PaddleResult(success=False, error="PADDLEOCR_API_KEY is not set.")

    if not os.path.exists(file_path):
        return PaddleResult(success=False, error=f"File not found: {file_path}")

    headers = {"Authorization": f"bearer {token}"}
    optional_payload = {
        "useDocOrientationClassify": False,
        "useDocUnwarping": False,
        "useChartRecognition": False,
    }
    data = {
        "model": MODEL,
        "optionalPayload": json.dumps(optional_payload)
    }

    logger.info("="*60)
    logger.info("PADDLE OCR API CALL")
    logger.info(f"  JOB_URL   : {JOB_URL}")
    logger.info(f"  MODEL     : {MODEL}")
    logger.info(f"  file_path : {file_path}")
    logger.info(f"  file_size : {os.path.getsize(file_path)} bytes")
    logger.info(f"  API_KEY set: {'yes' if token else 'NO — KEY MISSING'}")
    logger.info(f"  payload   : model={MODEL}, optional={optional_payload}")
    logger.info("="*60)

    # ── Submit job ─────────────────────────────────────────────────────────────
    logger.info(f"[PaddleOCR] Submitting job for: {os.path.basename(file_path)}")
    submit_start = time.time()
    try:
        with open(file_path, "rb") as f:
            resp = requests.post(JOB_URL, headers=headers, data=data,
                                 files={"file": f}, timeout=30)
    except Exception as e:
        logger.error(f"[PaddleOCR] NETWORK ERROR during job submission: {type(e).__name__}: {e}")
        return PaddleResult(success=False, error=f"Job submission network error: {e}")

    submit_elapsed = time.time() - submit_start
    logger.info(f"[PaddleOCR] Submit HTTP status : {resp.status_code} (elapsed={submit_elapsed:.2f}s)")
    logger.info(f"[PaddleOCR] Submit response    : {resp.text[:500]}")

    if resp.status_code != 200:
        logger.error(f"[PaddleOCR] FAIL: Job submission HTTP {resp.status_code}: {resp.text[:300]}")
        return PaddleResult(
            success=False,
            error=f"Job submission failed HTTP {resp.status_code}: {resp.text[:300]}"
        )

    resp_json = resp.json()
    job_id = resp_json.get("data", {}).get("jobId")
    logger.info(f"[PaddleOCR] resp_json keys: {list(resp_json.keys())}")
    logger.info(f"[PaddleOCR] data section  : {resp_json.get('data', {})}")
    if not job_id:
        logger.error(f"[PaddleOCR] FAIL: No jobId in response: {resp_json}")
        return PaddleResult(
            success=False,
            error=f"No jobId in submission response: {resp_json}"
        )
    logger.info(f"[PaddleOCR] Job submitted. jobId={job_id}")

    # ── Poll ───────────────────────────────────────────────────────────────────
    jsonl_url = None
    for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
        time.sleep(POLL_INTERVAL_SEC)
        try:
            poll_resp = requests.get(f"{JOB_URL}/{job_id}", headers=headers, timeout=15)
        except Exception as e:
            logger.warning(f"[PaddleOCR] Poll attempt {attempt} network error: {e}")
            continue

        if poll_resp.status_code != 200:
            logger.warning(f"[PaddleOCR] Poll attempt {attempt} HTTP {poll_resp.status_code}: {poll_resp.text[:200]}")
            continue

        poll_data = poll_resp.json().get("data", {})
        state = poll_data.get("state", "unknown")
        logger.info(f"[PaddleOCR] Poll {attempt}/{MAX_POLL_ATTEMPTS}: state={state} | keys={list(poll_data.keys())}")

        if state == "done":
            jsonl_url = poll_data.get("resultUrl", {}).get("jsonUrl")
            logger.info(f"[PaddleOCR] Job done. Result URL: {jsonl_url}")
            break
        elif state == "failed":
            error_msg = poll_data.get("errorMsg", "No error message returned.")
            return PaddleResult(success=False, error=f"PaddleOCR job failed: {error_msg}")
        # state == pending / running → continue polling

    if not jsonl_url:
        return PaddleResult(success=False, error="Timed out polling PaddleOCR job.")

    # ── Download JSONL ─────────────────────────────────────────────────────────
    logger.info(f"[PaddleOCR] Downloading JSONL result...")
    try:
        jsonl_resp = requests.get(jsonl_url, timeout=60)
        jsonl_resp.raise_for_status()
    except Exception as e:
        return PaddleResult(success=False, error=f"Failed to download JSONL: {e}")

    raw_jsonl = jsonl_resp.text

    # Log the FULL raw response — critical for debugging
    logger.info("[PaddleOCR] ══════════ RAW JSONL RESPONSE (FULL) ══════════")
    logger.info(raw_jsonl)
    logger.info("[PaddleOCR] ════════════════════════════════════════════════")

    # ── Parse JSONL ────────────────────────────────────────────────────────────
    pages = []
    all_text_lines: List[dict] = []
    all_markdown_parts: List[str] = []

    for line_num, line in enumerate(raw_jsonl.strip().split("\n"), start=1):
        line = line.strip()
        if not line:
            continue

        try:
            page_obj = json.loads(line)
        except json.JSONDecodeError as e:
            logger.warning(f"[PaddleOCR] Could not parse JSONL line {line_num}: {e}")
            continue

        result = page_obj.get("result", {})
        layout_results = result.get("layoutParsingResults", [])

        page_markdown_parts = []
        raw_lines = []
        for res in layout_results:
            md_text = ""
            md_node = res.get("markdown")
            if isinstance(md_node, dict):
                md_text = md_node.get("text", "")
            elif isinstance(md_node, str):
                md_text = md_node

            if md_text:
                page_markdown_parts.append(md_text)
                
            box = []
            loc = res.get("layoutLocation", {})
            if isinstance(loc, dict):
                pts = loc.get("points", [])
                if pts and len(pts) >= 4:
                    box = pts
            
            if md_text:
                raw_lines.append({"text": md_text, "box": box})

        page_markdown = "\n".join(page_markdown_parts)

        # Scale points to [0, 1000] based on max coordinates on the page
        all_x = [pt[0] for rl in raw_lines for pt in rl["box"] if rl["box"]]
        all_y = [pt[1] for rl in raw_lines for pt in rl["box"] if rl["box"]]
        max_x = max(all_x) if all_x else 1000
        max_y = max(all_y) if all_y else 1000

        clean_lines = []
        for rl in raw_lines:
            scaled_box = []
            if rl["box"]:
                for pt in rl["box"]:
                    scaled_box.append([
                        (pt[0] / max_x) * 1000 if max_x > 0 else pt[0],
                        (pt[1] / max_y) * 1000 if max_y > 0 else pt[1]
                    ])
            
            clean_text = rl["text"].lstrip("#>-* ").strip()
            if clean_text:
                clean_lines.append({
                    "text": clean_text,
                    "box": scaled_box,
                    "confidence": 0.9,
                    "page": line_num
                })

        pages.append({
            "page": line_num,
            "layout_results_count": len(layout_results),
            "markdown": page_markdown,
            "text_lines": clean_lines,
        })

        all_markdown_parts.append(page_markdown)
        all_text_lines.extend(clean_lines)

        logger.info(
            f"[PaddleOCR] Page {line_num}: "
            f"layout_results={len(layout_results)}, "
            f"markdown_chars={len(page_markdown)}, "
            f"text_lines={len(clean_lines)}"
        )

    total_markdown = "\n".join(all_markdown_parts)

    logger.info(
        f"[PaddleOCR] Parse complete — "
        f"pages={len(pages)}, "
        f"total_text_lines={len(all_text_lines)}, "
        f"total_markdown_chars={len(total_markdown)}"
    )

    return PaddleResult(
        success=True,
        raw_jsonl=raw_jsonl,
        pages=pages,
        markdown=total_markdown,
        text_lines=all_text_lines,
        page_count=len(pages),
    )
