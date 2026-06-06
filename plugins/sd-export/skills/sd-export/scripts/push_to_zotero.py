#!/usr/bin/env python3
"""Push ScienceDirect citation data to Zotero via local Connector API (localhost:23119).

Supports two modes:
  1. RIS import:  --ris-file or --ris-data  (backward compatible)
  2. JSON import: --json (structured data with optional PDF attachment)

Session strategy: deterministic sessionID derived from content hash.
- 201 = saved successfully
- 409 = SESSION_EXISTS = already saved (idempotent, treat as success)
- Zotero's session gc/remove are buggy, sessions persist until restart.
  Deterministic IDs turn this bug into a feature: same content → same ID → 409 = already done.
"""

import argparse
import hashlib
import io
import json
import sys
import urllib.error
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

ZOTERO_API = "http://127.0.0.1:23119/connector"
HTTP_TIMEOUT = 15  # seconds, matching Zotero Connector extension


# ---------------------------------------------------------------------------
# Zotero API helpers
# ---------------------------------------------------------------------------

def zotero_request(endpoint, data=None, timeout=HTTP_TIMEOUT):
    """Send JSON request to Zotero local API with timeout."""
    url = f"{ZOTERO_API}/{endpoint}"
    body = json.dumps(data or {}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "X-Zotero-Connector-API-Version": "3",
    })
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        text = resp.read().decode("utf-8")
        return resp.status, json.loads(text) if text else None
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(resp_body) if resp_body else None
        except json.JSONDecodeError:
            return e.code, {"error": resp_body}
    except urllib.error.URLError:
        return 0, None
    except TimeoutError:
        return -1, {"error": f"Request timed out ({timeout}s)"}


def make_session_id(content_key):
    """Generate deterministic 12-char sessionID from content key.

    Same content always produces the same ID, so:
    - First call: creates session, saves items → 201
    - Repeat call: session exists → 409 → treat as already saved
    """
    return hashlib.md5(
        content_key.encode("utf-8", errors="surrogateescape")
    ).hexdigest()[:12]


def get_selected_collection():
    """Get currently selected Zotero collection."""
    status, data = zotero_request("getSelectedCollection")
    if status != 200 or not data:
        return None
    return data


# ---------------------------------------------------------------------------
# RIS import (backward compatible)
# ---------------------------------------------------------------------------

def push_ris(ris_data):
    """Push RIS data to Zotero via /connector/import with deterministic session.

    Returns:
        dict with 'success' boolean and 'message' string.
    """
    if not ris_data.strip():
        return {"success": False, "message": "Empty RIS data."}

    session_id = make_session_id(ris_data.strip())
    url = f"{ZOTERO_API}/import?session={session_id}"
    payload = json.dumps(ris_data).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
    })

    try:
        resp = urllib.request.urlopen(req, timeout=HTTP_TIMEOUT)
        body = resp.read().decode("utf-8", errors="replace")
        return {"success": True, "message": f"Saved to Zotero (session: {session_id}). Response: {body}"}
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8", errors="replace")
        if e.code == 409:
            return {"success": True, "message": f"Already saved, no duplicates added (session: {session_id})"}
        return {"success": False, "message": f"HTTP {e.code}: {resp_body}"}
    except urllib.error.URLError as e:
        return {
            "success": False,
            "message": f"Cannot connect to Zotero. Is Zotero desktop running? Error: {e.reason}",
        }
    except TimeoutError:
        return {"success": False, "message": f"Request timed out ({HTTP_TIMEOUT}s)"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {e}"}


# ---------------------------------------------------------------------------
# JSON / structured item import with PDF attachment support
# ---------------------------------------------------------------------------

def build_zotero_item(paper):
    """Build Zotero journalArticle item from ScienceDirect paper data."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    item = {
        "itemType": "journalArticle",
        "title": paper.get("title", ""),
        "abstractNote": paper.get("abstract", ""),
        "date": paper.get("date", ""),
        "url": paper.get("url", ""),
        "DOI": paper.get("doi", ""),
        "volume": paper.get("volume", ""),
        "issue": paper.get("issue", ""),
        "pages": paper.get("pages", ""),
        "publicationTitle": paper.get("journal", ""),
        "libraryCatalog": "ScienceDirect",
        "accessDate": now,
        "creators": [
            {"name": a, "creatorType": "author"}
            for a in paper.get("authors", [])
        ],
        "tags": [
            {"tag": k, "type": 1}
            for k in paper.get("keywords", [])
        ],
        "attachments": [],
    }

    if paper.get("issn"):
        item["ISSN"] = paper["issn"]
    if paper.get("articleType"):
        item["extra"] = f"articleType: {paper['articleType']}"

    return item


def download_pdf(pdf_url, cookies="", referer="https://www.sciencedirect.com"):
    """Download PDF from ScienceDirect using provided cookies.

    Returns (bytes, content_type) or (None, error_message).
    """
    req = urllib.request.Request(pdf_url, headers={
        "Cookie": cookies,
        "Referer": referer,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/145.0.0.0",
    })
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        content_type = resp.headers.get("Content-Type", "application/pdf")
        data = resp.read()
        if len(data) < 1024:
            return None, f"PDF file too small ({len(data)} bytes), may require authentication"
        return data, content_type
    except Exception as e:
        return None, str(e)


def save_attachment(session_id, item_id, pdf_bytes, pdf_url,
                    content_type="application/pdf", title="Full Text PDF"):
    """Upload PDF binary to Zotero via /connector/saveAttachment (Zotero 7.x workflow)."""
    metadata = json.dumps({
        "id": item_id + "_pdf",
        "parentItemID": item_id,
        "title": title,
        "url": pdf_url,
        "contentType": content_type,
    })
    url = f"{ZOTERO_API}/saveAttachment?sessionID={session_id}"
    req = urllib.request.Request(url, data=pdf_bytes, headers={
        "Content-Type": content_type,
        "X-Metadata": metadata,
        "Content-Length": str(len(pdf_bytes)),
        "X-Zotero-Connector-API-Version": "3",
    })
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        return resp.status, None
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except Exception as e:
        return 0, str(e)


def save_items(items, uri="", attachments=None, cookies=""):
    """Push items to Zotero via saveItems API, optionally with PDF attachments.

    Uses deterministic sessionID (content hash) for idempotency:
    - 201 = saved successfully
    - 409 = same items already saved in this Zotero session (success)
    """
    key = "|".join(sorted(item.get("title", "") for item in items))
    session_id = make_session_id(key)

    # Assign IDs to items (needed for attachment parentItemID mapping)
    for i, item in enumerate(items):
        if "id" not in item:
            item["id"] = f"sd_{session_id}_{i}"

    data = {
        "sessionID": session_id,
        "uri": uri,
        "items": items,
    }
    status, resp = zotero_request("saveItems", data)

    already_saved = False
    if status == 201:
        msg = f"Saved to Zotero (session: {session_id})"
    elif status == 409:
        already_saved = True
        msg = f"Already saved, no duplicates added (session: {session_id})"
    elif status == 500:
        detail = resp.get("error", "") if resp else ""
        if "libraryEditable" in str(resp):
            return 500, "Target library is read-only. Switch to a writable collection in Zotero."
        return 500, f"Zotero internal error: {detail}"
    elif status == 0:
        return 0, "Zotero is not running or connection refused"
    elif status == -1:
        return -1, f"Request timed out ({HTTP_TIMEOUT}s)"
    else:
        return status, f"Unknown error, HTTP {status}"

    # Handle PDF attachments (only for new saves, skip if already saved)
    if attachments and not already_saved:
        col = get_selected_collection()
        files_editable = col.get("filesEditable", True) if col else True

        if files_editable:
            pdf_results = []
            for att in attachments:
                idx = att.get("itemIndex", 0)
                pdf_url = att.get("pdfUrl", "")
                title = att.get("title", "Full Text PDF")
                if not pdf_url:
                    continue

                item_id = items[idx]["id"] if idx < len(items) else items[0]["id"]
                print(f"  Downloading PDF: {pdf_url[:80]}...", file=sys.stderr)
                pdf_bytes, ct = download_pdf(pdf_url, cookies=cookies)

                if pdf_bytes is None:
                    pdf_results.append(f"  PDF download failed: {ct}")
                    continue

                print(f"  Uploading PDF to Zotero ({len(pdf_bytes)} bytes)...", file=sys.stderr)
                att_status, att_err = save_attachment(
                    session_id, item_id, pdf_bytes, pdf_url, title=title
                )
                if att_status == 201:
                    pdf_results.append(f"  PDF attached: {title} ({len(pdf_bytes) // 1024}KB)")
                else:
                    pdf_results.append(f"  PDF upload failed: HTTP {att_status} {att_err or ''}")

            if pdf_results:
                msg += "\n" + "\n".join(pdf_results)
        else:
            msg += "\n  (Target collection does not support file attachments, skipping PDF)"

    return 201, msg


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Push ScienceDirect citations to Zotero"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ris-file", help="Path to an RIS file to import")
    group.add_argument("--ris-data", help="RIS data as a string")
    group.add_argument(
        "--json",
        help="Path to JSON file with structured paper data (supports PDF attachment)",
    )
    group.add_argument("--list", action="store_true", help="List Zotero collections")
    args = parser.parse_args()

    # Check Zotero is running
    status, _ = zotero_request("ping")
    if status == 0:
        print("Error: Zotero is not running. Please start Zotero desktop.")
        sys.exit(1)

    if args.list:
        col = get_selected_collection()
        if col:
            print(f"Current collection: {col.get('name', '?')} (ID: {col.get('id', '?')})")
            print(f"Library: {col.get('libraryName', '?')}")
            for t in col.get("targets", []):
                indent = "  " * t.get("level", 0)
                print(f"  {indent}{t['name']} (ID: {t['id']})")
        return

    # Show current collection
    col = get_selected_collection()
    if col:
        print(f"Zotero collection: {col.get('name', '?')}")

    # Mode 1: RIS import
    if args.ris_file or args.ris_data:
        if args.ris_file:
            with open(args.ris_file, "r", encoding="utf-8") as f:
                ris_data = f.read()
        else:
            ris_data = args.ris_data

        result = push_ris(ris_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result["success"] else 1)

    # Mode 2: JSON structured import
    if args.json:
        with open(args.json, "r", encoding="utf-8") as f:
            paper_data = json.load(f)

        # Handle both single paper and array
        if isinstance(paper_data, list):
            papers = paper_data
        elif "items" in paper_data:
            # Already in Zotero format
            status, msg = save_items(
                paper_data["items"], paper_data.get("uri", "")
            )
            if status == 201:
                print(f"Success: {msg} ({len(paper_data['items'])} items)")
            else:
                print(f"Failed: {msg}")
                sys.exit(1)
            return
        else:
            papers = [paper_data]

        # Build Zotero items
        items = []
        for p in papers:
            if "itemType" in p:
                items.append(p)
            elif "title" in p:
                items.append(build_zotero_item(p))

        if not items:
            print("Error: No valid paper data found.")
            sys.exit(1)

        # Collect attachment info and cookies from input
        attachments = []
        cookies = ""
        for i, p in enumerate(papers):
            if p.get("pdfUrl"):
                attachments.append({
                    "itemIndex": i,
                    "pdfUrl": p["pdfUrl"],
                    "title": p.get("pdfTitle", "Full Text PDF"),
                })
            if p.get("cookies") and not cookies:
                cookies = p["cookies"]

        uri = papers[0].get("url", "")
        status, msg = save_items(items, uri, attachments=attachments, cookies=cookies)
        if status == 201:
            print(f"Success: {msg} ({len(items)} items)")
            for item in items:
                print(f"  - {item.get('title', '?')}")
        else:
            print(f"Failed: {msg}")
            sys.exit(1)


if __name__ == "__main__":
    main()
