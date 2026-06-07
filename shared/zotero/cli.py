#!/usr/bin/env python3
"""Shared CLI framework for Zotero push scripts.

Provides a unified argparse-based entry point that all platform
adapters use. Eliminates the old sys.argv/manual parsing inconsistency.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable, Optional

from shared.zotero.core import ZoteroClient
from shared.zotero.pdf import PdfHandler


def create_parser(
    description: str,
    platform_name: str,
) -> argparse.ArgumentParser:
    """Create a standard argument parser for Zotero push scripts.

    Standard arguments:
        FILE        JSON input file (positional, optional)
        --list      List Zotero collections

    Platform-specific arguments can be added by the adapter after
    calling this function.
    """
    parser = argparse.ArgumentParser(
        description=description,
        epilog=f"Push {platform_name} citations to Zotero desktop.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Path to JSON file with paper data (reads from stdin if omitted)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available Zotero collections and exit",
    )
    return parser


def read_input(args: argparse.Namespace) -> Any:
    """Read JSON input from file argument or stdin."""
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {args.file}: {e}")
            sys.exit(1)
    else:
        try:
            return json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON from stdin: {e}")
            sys.exit(1)


def run_push(
    client: ZoteroClient,
    pdf_handler: Optional[PdfHandler],
    build_item: Callable[[dict], dict],
    paper_data: Any,
    uri_extractor: Optional[Callable[[dict], str]] = None,
    attachment_extractor: Optional[Callable[[list], tuple[list, str]]] = None,
) -> None:
    """Execute the standard push workflow.

    Args:
        client: ZoteroClient instance
        pdf_handler: PdfHandler instance (None if platform doesn't support PDFs)
        build_item: Function(paper_dict) -> zotero_item_dict
        paper_data: Parsed JSON input (single dict, list, or {"items": [...]})
        uri_extractor: Optional function(paper_dict) -> uri string
        attachment_extractor: Optional function(papers) -> (attachments, cookies)
    """
    # Check Zotero is running
    if not client.ping():
        print("Error: Zotero is not running. Please start Zotero desktop.")
        sys.exit(1)

    # Show current collection
    col = client.get_selected_collection()
    if col:
        print(f"Zotero collection: {col.get('name', '?')}")

    # Handle already-formatted Zotero items
    if isinstance(paper_data, dict) and "items" in paper_data:
        status, msg, _ = client.save_items(
            paper_data["items"], paper_data.get("uri", "")
        )
        if status == 201:
            print(f"OK: {msg} ({len(paper_data['items'])} papers)")
        else:
            print(f"Error: {msg}")
            sys.exit(1)
        return

    # Normalize to list
    papers = paper_data if isinstance(paper_data, list) else [paper_data]

    # Build Zotero items, tracking which papers produced valid items
    items = []
    matched_papers = []
    for p in papers:
        if "itemType" in p:
            items.append(p)
            matched_papers.append(p)
        else:
            item = build_item(p)
            if item is not None:
                items.append(item)
                matched_papers.append(p)

    if not items:
        print("Error: No valid paper data.")
        sys.exit(1)

    # Extract URI
    uri = ""
    if uri_extractor and papers:
        uri = uri_extractor(papers[0])

    # Save items
    status, msg, session_id = client.save_items(items, uri)
    if status != 201:
        print(f"Error: {msg}")
        sys.exit(1)

    print(f"OK: {msg} ({len(items)} papers)")
    for item in items:
        print(f"  - {item.get('title', '?')}")

    # Handle PDF attachments — use matched_papers to keep alignment with items
    if pdf_handler and attachment_extractor:
        attachments, cookies = attachment_extractor(matched_papers)
        if attachments:
            pdf_handler.attach_pdfs(
                client, session_id, items, matched_papers, cookies=cookies
            )
