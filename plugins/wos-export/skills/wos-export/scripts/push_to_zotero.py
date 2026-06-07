#!/usr/bin/env python3
"""Push WoS paper data to Zotero via local Connector API.

Thin wrapper around shared.zotero with WoS-specific adapter.
"""

import sys
import os

# Add repo root to path for shared module imports
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
)

from shared.zotero.core import ZoteroClient
from shared.zotero.cli import create_parser, read_input, run_push
from shared.zotero.adapters.wos import build_zotero_item, extract_uri


def main():
    parser = create_parser(
        description="Push Web of Science citations to Zotero",
        platform_name="Web of Science",
    )
    args = parser.parse_args()

    client = ZoteroClient(id_prefix="wos")

    if args.list:
        if not client.ping():
            print("Error: Cannot connect to Zotero.")
            sys.exit(1)
        client.list_collections()
        return

    paper_data = read_input(args)
    run_push(
        client=client,
        pdf_handler=None,  # WoS doesn't support direct PDF download
        build_item=build_zotero_item,
        paper_data=paper_data,
        uri_extractor=extract_uri,
    )


if __name__ == "__main__":
    main()
