#!/usr/bin/env python3
"""ScienceDirect adapter for Zotero integration.

ScienceDirect-specific logic:
- Simple author list (name strings)
- Extra field: articleType
- PDF download with Elsevier referer
- RIS import backward compatibility
"""

from __future__ import annotations

from datetime import datetime, timezone


def build_zotero_item(paper: dict) -> dict:
    """Build Zotero journalArticle item from ScienceDirect paper data."""
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
            {"name": a, "creatorType": "author"} for a in paper.get("authors", [])
        ],
        "tags": [{"tag": k, "type": 1} for k in paper.get("keywords", [])],
        "attachments": [],
    }

    if paper.get("issn"):
        item["ISSN"] = paper["issn"]
    if paper.get("articleType"):
        item["extra"] = f"articleType: {paper['articleType']}"

    return item


def extract_uri(paper: dict) -> str:
    """Extract source URI from ScienceDirect paper data."""
    return paper.get("url", "")
