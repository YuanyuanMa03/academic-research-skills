#!/usr/bin/env python3
"""Push Google Scholar / PubMed paper data to Zotero via local Connector API.

Thin wrapper around shared.zotero with GS/PubMed-specific adapter.
Supports PDF attachment with PMC fallback.
"""

import sys
import os

# Add repo root to path for shared module imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))

from shared.zotero.core import ZoteroClient
from shared.zotero.pdf import PdfHandler
from shared.zotero.cli import create_parser, read_input, run_push
from shared.zotero.adapters.gs import build_zotero_item, extract_uri, resolve_pdf_url


def main():
    parser = create_parser(
        description="Push Google Scholar / PubMed citations to Zotero",
        platform_name="Google Scholar",
    )
    args = parser.parse_args()

    client = ZoteroClient(id_prefix="pm")
    pdf = PdfHandler(default_referer="https://scholar.google.com")

    if args.list:
        if not client.ping():
            print("Error: Cannot connect to Zotero.")
            sys.exit(1)
        client.list_collections()
        return

    paper_data = read_input(args)

    def attachment_extractor(papers):
        """Inject PMC PDF URLs before attach_pdfs processes them."""
        for p in papers:
            url = resolve_pdf_url(p)
            if url:
                p.setdefault("pdfUrl", url)
        return papers, ""

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
