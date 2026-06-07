#!/usr/bin/env python3
"""Push ScienceDirect citation data to Zotero via local Connector API.

Thin wrapper around shared.zotero with SD-specific adapter.
Supports both RIS import (backward compatible) and JSON structured import
with PDF attachment.
"""

import argparse
import json
import sys
import os

# Add repo root to path for shared module imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from shared.zotero.core import ZoteroClient
from shared.zotero.pdf import PdfHandler
from shared.zotero.adapters.sd import build_zotero_item, extract_uri


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

    client = ZoteroClient(id_prefix="sd")

    # Check Zotero is running
    if not client.ping():
        print("Error: Zotero is not running. Please start Zotero desktop.")
        sys.exit(1)

    if args.list:
        client.list_collections()
        return

    # Show current collection
    col = client.get_selected_collection()
    if col:
        print(f"Zotero collection: {col.get('name', '?')}")

    # Mode 1: RIS import (backward compatible)
    if args.ris_file or args.ris_data:
        if args.ris_file:
            with open(args.ris_file, "r", encoding="utf-8") as f:
                ris_data = f.read()
        else:
            ris_data = args.ris_data

        result = client.import_ris(ris_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result["success"] else 1)

    # Mode 2: JSON structured import with PDF support
    if args.json:
        with open(args.json, "r", encoding="utf-8") as f:
            paper_data = json.load(f)

        # Handle already-formatted Zotero items
        if isinstance(paper_data, dict) and "items" in paper_data:
            status, msg, _ = client.save_items(
                paper_data["items"], paper_data.get("uri", "")
            )
            if status == 201:
                print(f"Success: {msg} ({len(paper_data['items'])} items)")
            else:
                print(f"Failed: {msg}")
                sys.exit(1)
            return

        # Normalize to list
        papers = paper_data if isinstance(paper_data, list) else [paper_data]

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

        # Collect attachment info and cookies
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
        status, msg, session_id = client.save_items(items, uri)
        if status != 201:
            print(f"Failed: {msg}")
            sys.exit(1)

        print(f"Success: {msg} ({len(items)} items)")
        for item in items:
            print(f"  - {item.get('title', '?')}")

        # Handle PDF attachments
        if attachments:
            pdf = PdfHandler(default_referer="https://www.sciencedirect.com")
            pdf.attach_pdfs(client, session_id, items, papers, cookies=cookies)


if __name__ == "__main__":
    main()
