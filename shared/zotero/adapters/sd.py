#!/usr/bin/env python3
"""ScienceDirect adapter for Zotero integration.

ScienceDirect-specific logic:
- Simple author list (name strings or dicts)
- Extra field: articleType, ISSN
- PDF download with Elsevier referer
- RIS import backward compatibility
"""

from __future__ import annotations

from datetime import datetime, timezone


def build_zotero_item(paper: dict) -> dict:
    """Build Zotero journalArticle item from ScienceDirect paper data."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Handle authors: accept both string and dict formats
    raw_authors = paper.get("authors") or []
    creators = []
    for a in raw_authors:
        if isinstance(a, dict):
            if "lastName" in a:
                creators.append(
                    {
                        "lastName": a["lastName"],
                        "firstName": a.get("given-name", a.get("firstName", "")),
                        "creatorType": "author",
                    }
                )
            elif "name" in a:
                creators.append({"name": a["name"], "creatorType": "author"})
        else:
            creators.append({"name": str(a), "creatorType": "author"})

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
        "creators": creators,
        "tags": [{"tag": k, "type": 1} for k in paper.get("keywords", [])],
        "attachments": [],
    }

    # ISSN
    if paper.get("issn"):
        item["ISSN"] = paper["issn"]

    # Extra field — accumulate all metadata parts
    extra_parts = []
    if paper.get("issn"):
        extra_parts.append(f"ISSN: {paper['issn']}")
    if paper.get("articleType"):
        extra_parts.append(f"articleType: {paper['articleType']}")
    if extra_parts:
        item["extra"] = "\n".join(extra_parts)

    return item


def extract_uri(paper: dict) -> str:
    """Extract source URI from ScienceDirect paper data."""
    return paper.get("url", "")
