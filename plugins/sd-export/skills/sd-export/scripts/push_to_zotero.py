#!/usr/bin/env python3
"""Push ScienceDirect citation data to Zotero via local Connector API.

Thin wrapper around shared.zotero with SD-specific adapter.
Supports both RIS import (backward compatible) and JSON structured import
with PDF attachment.
"""

import json
import sys
import os

# Add repo root to path for shared module imports
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
)

from shared.zotero.core import ZoteroClient
from shared.zotero.pdf import PdfHandler
from shared.zotero.cli import create_parser, read_input, run_push
from shared.zotero.adapters.sd import build_zotero_item


def main():
    parser = create_parser(
        description="Push ScienceDirect citations to Zotero",
        platform_name="ScienceDirect",
    )
    # RIS-specific arguments (mutually exclusive with JSON file)
    ris_group = parser.add_mutually_exclusive_group()
    ris_group.add_argument("--ris-file", help="Path to an RIS file to import")
    ris_group.add_argument("--ris-data", help="RIS data as a string")
    args = parser.parse_args()

    client = ZoteroClient(id_prefix="sd")

    if args.list:
        if not client.ping():
            print("Error: Cannot connect to Zotero.")
            sys.exit(1)
        client.list_collections()
        return

    # Mode 1: RIS import (backward compatible)
    if args.ris_file is not None or args.ris_data is not None:
        if not client.ping():
            print("Error: Zotero is not running. Please start Zotero desktop.")
            sys.exit(1)
        col = client.get_selected_collection()
        if col:
            print(f"Zotero collection: {col.get('name', '?')}")

        if args.ris_file:
            with open(args.ris_file, "r", encoding="utf-8") as f:
                ris_data = f.read()
        else:
            ris_data = args.ris_data

        result = client.import_ris(ris_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result["success"] else 1)

    # Mode 2: JSON structured import (uses shared CLI framework)
    paper_data = read_input(args)

    pdf = PdfHandler(default_referer="https://www.sciencedirect.com")

    def attachment_extractor(papers):
        """Collect PDF attachment info from paper data."""
        attachments = []
        cookies = ""
        for i, p in enumerate(papers):
            if p.get("pdfUrl"):
                attachments.append(
                    {
                        "itemIndex": i,
                        "pdfUrl": p["pdfUrl"],
                        "title": p.get("pdfTitle", "Full Text PDF"),
                    }
                )
            if p.get("cookies") and not cookies:
                cookies = p["cookies"]
        return attachments, cookies

    def extract_uri(paper):
        return paper.get("url", "")

    run_push(
        client=client,
        pdf_handler=pdf,
        build_item=build_zotero_item,
        paper_data=paper_data,
        uri_extractor=extract_uri,
        attachment_extractor=attachment_extractor,
    )


if __name__ == "__main__":
    main()
