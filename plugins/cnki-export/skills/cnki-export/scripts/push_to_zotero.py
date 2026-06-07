#!/usr/bin/env python3
"""Push CNKI paper data to Zotero via local Connector API.

Thin wrapper around shared.zotero with CNKI-specific adapter.
Supports ELEARNING format parsing and PDF attachment with CNKI cookies.
"""

import sys
import os

# Add repo root to path for shared module imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))

from shared.zotero.core import ZoteroClient
from shared.zotero.pdf import PdfHandler
from shared.zotero.cli import create_parser, read_input, run_push
from shared.zotero.adapters.cnki import (
    build_zotero_item,
    build_item_from_elearning,
    extract_uri,
)


def main():
    parser = create_parser(
        description="Push CNKI citations to Zotero",
        platform_name="CNKI",
    )
    args = parser.parse_args()

    client = ZoteroClient(id_prefix="cnki")
    pdf = PdfHandler(default_referer="https://kns.cnki.net")

    if args.list:
        if not client.ping():
            print("Error: 无法连接 Zotero。请确保 Zotero 桌面端已启动。")
            sys.exit(1)
        client.list_collections()
        return

    paper_data = read_input(args)

    def cnki_build_item(paper):
        """Build item, handling ELEARNING format."""
        if "itemType" in paper:
            return paper
        if "ELEARNING" in paper:
            return build_item_from_elearning(paper)
        return build_zotero_item(paper)

    def attachment_extractor(papers):
        """Extract attachment info and cookies from CNKI paper data."""
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
        return attachments, cookies

    run_push(
        client=client,
        pdf_handler=pdf,
        build_item=cnki_build_item,
        paper_data=paper_data,
        uri_extractor=extract_uri,
        attachment_extractor=attachment_extractor,
    )


if __name__ == "__main__":
    main()
