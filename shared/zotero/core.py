#!/usr/bin/env python3
"""Unified Zotero Connector API client.

Provides core Zotero operations shared across all platform adapters:
- API request with timeout and error handling
- Deterministic session ID generation (content hash)
- saveItems with idempotency (201 = saved, 409 = already saved)
- saveAttachment for PDF uploads
- Collection listing and selection
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
import urllib.error
import urllib.request
from typing import Any, Optional

# Ensure UTF-8 output on all platforms (skip under pytest to avoid capture conflict)
import os as _os

if not _os.environ.get("PYTEST_RUNNING"):
    try:
        if hasattr(sys.stdout, "encoding") and sys.stdout.encoding != "utf-8":
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        if hasattr(sys.stderr, "encoding") and sys.stderr.encoding != "utf-8":
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    except (AttributeError, OSError):
        pass  # buffer not available (e.g., in tests or non-TTY environments)

ZOTERO_API = "http://127.0.0.1:23119/connector"
HTTP_TIMEOUT = 15  # seconds


class ZoteroClient:
    """Client for Zotero's local Connector API (localhost:23119).

    All platform adapters share this client for Zotero communication.
    """

    def __init__(
        self,
        api_base: str = ZOTERO_API,
        timeout: int = HTTP_TIMEOUT,
        id_prefix: str = "item",
    ):
        self.api_base = api_base
        self.timeout = timeout
        self.id_prefix = id_prefix

    # ------------------------------------------------------------------
    # Low-level API
    # ------------------------------------------------------------------

    def request(
        self, endpoint: str, data: Any = None, timeout: Optional[int] = None
    ) -> tuple[int, Any]:
        """Send JSON request to Zotero Connector API.

        Returns:
            (status_code, parsed_response_or_None)
            status 0 = connection refused, -1 = timeout
        """
        url = f"{self.api_base}/{endpoint}"
        body = json.dumps(data if data is not None else {}, ensure_ascii=False).encode(
            "utf-8"
        )
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Zotero-Connector-API-Version": "3",
            },
        )
        t = timeout or self.timeout
        try:
            resp = urllib.request.urlopen(req, timeout=t)
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
            return -1, {"error": f"Request timed out ({t}s)"}

    def ping(self) -> bool:
        """Check if Zotero is running."""
        status, _ = self.request("ping")
        return status == 200

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def make_session_id(self, items: list[dict]) -> str:
        """Generate deterministic 12-char session ID from item titles.

        Same titles always produce the same ID, enabling idempotency:
        - First call → 201 (saved)
        - Repeat call → 409 (already saved, treat as success)
        """
        key = "|".join(sorted(item.get("title", "") for item in items))
        return hashlib.md5(key.encode("utf-8", errors="surrogateescape")).hexdigest()[
            :12
        ]

    # ------------------------------------------------------------------
    # Collections
    # ------------------------------------------------------------------

    def get_selected_collection(self) -> Optional[dict]:
        """Get the currently selected Zotero collection."""
        status, data = self.request("getSelectedCollection")
        if status != 200 or not data:
            return None
        return data

    def list_collections(self) -> None:
        """Print all available Zotero collections to stdout."""
        data = self.get_selected_collection()
        if not data:
            print(
                "Error: Cannot connect to Zotero. Please ensure Zotero desktop is running."
            )
            return
        print(
            f"Current collection: {data.get('name', '?')} (ID: {data.get('id', '?')})"
        )
        print(f"Library: {data.get('libraryName', '?')}")
        print()
        print("Available collections:")
        for t in data.get("targets", []):
            indent = "  " * t.get("level", 0)
            recent = " *" if t.get("recent") else ""
            print(f"  {indent}{t.get('name', '?')} (ID: {t.get('id', '?')}){recent}")

    # ------------------------------------------------------------------
    # Save items
    # ------------------------------------------------------------------

    def save_items(
        self,
        items: list[dict],
        uri: str = "",
    ) -> tuple[int, str, str]:
        """Push items to Zotero via saveItems API.

        Uses deterministic sessionID for idempotency.

        Returns:
            (status, message, session_id)
            status 201 = success (new or idempotent)
        """
        session_id = self.make_session_id(items)

        # Assign stable IDs to each item (mutates in place — documented contract)
        for i, item in enumerate(items):
            if "id" not in item:
                item["id"] = f"{self.id_prefix}_{session_id}_{i}"

        data = {"sessionID": session_id, "uri": uri, "items": items}
        status, resp = self.request("saveItems", data)

        if status == 201:
            return 201, f"Saved (session: {session_id})", session_id
        elif status == 409:
            return 201, f"Already saved (session: {session_id})", session_id
        elif status == 500:
            if resp and "libraryEditable" in str(resp):
                return 500, "Target library is read-only.", session_id
            detail = resp.get("error", "") if resp else ""
            return 500, f"Zotero internal error: {detail}", session_id
        elif status == 0:
            return 0, "Zotero is not running or connection refused.", session_id
        elif status == -1:
            return -1, f"Request timed out ({self.timeout}s)", session_id
        else:
            return status, f"Unknown error, HTTP {status}", session_id

    # ------------------------------------------------------------------
    # Save attachment (PDF upload)
    # ------------------------------------------------------------------

    def save_attachment(
        self,
        session_id: str,
        parent_item_id: str,
        pdf_bytes: bytes,
        pdf_url: str,
        content_type: str = "application/pdf",
        title: str = "Full Text PDF",
    ) -> tuple[int, Optional[str]]:
        """Upload PDF binary to Zotero via /connector/saveAttachment.

        Zotero 7.x ignores attachments in saveItems, so PDFs must be
        uploaded separately via this endpoint.

        Returns:
            (status_code, error_message_or_None)
        """
        metadata = json.dumps(
            {
                "id": parent_item_id + "_pdf",
                "parentItemID": parent_item_id,
                "title": title,
                "url": pdf_url,
                "contentType": content_type,
            },
            ensure_ascii=False,
        )

        url = f"{self.api_base}/saveAttachment?sessionID={session_id}"
        req = urllib.request.Request(
            url,
            data=pdf_bytes,
            headers={
                "Content-Type": content_type,
                "X-Metadata": metadata,
                "Content-Length": str(len(pdf_bytes)),
                "X-Zotero-Connector-API-Version": "3",
            },
        )

        try:
            resp = urllib.request.urlopen(req, timeout=max(60, self.timeout))
            return resp.status, None
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", errors="replace")
        except urllib.error.URLError:
            return 0, "Connection refused"
        except TimeoutError:
            return -1, "Timeout"

    # ------------------------------------------------------------------
    # RIS import (ScienceDirect backward compatibility)
    # ------------------------------------------------------------------

    def import_ris(self, ris_data: str) -> dict:
        """Push RIS data to Zotero via /connector/import.

        Sends raw RIS text (not JSON-encoded) with Content-Type: text/plain.

        Returns:
            dict with 'success' (bool) and 'message' (str).
        """
        if not ris_data.strip():
            return {"success": False, "message": "Empty RIS data."}

        session_id = self.make_session_id([{"title": ris_data.strip()[:200]}])
        url = f"{self.api_base}/import?session={session_id}"
        payload = ris_data.encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "X-Zotero-Connector-API-Version": "3",
            },
        )

        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout)
            body = resp.read().decode("utf-8", errors="replace")
            return {
                "success": True,
                "message": f"Saved to Zotero (session: {session_id}). Response: {body}",
            }
        except urllib.error.HTTPError as e:
            if e.code == 409:
                return {
                    "success": True,
                    "message": f"Already saved (session: {session_id})",
                }
            resp_body = e.read().decode("utf-8", errors="replace")
            return {"success": False, "message": f"HTTP {e.code}: {resp_body}"}
        except urllib.error.URLError:
            return {
                "success": False,
                "message": "Cannot connect to Zotero.",
            }
        except TimeoutError:
            return {
                "success": False,
                "message": f"Request timed out ({self.timeout}s)",
            }
