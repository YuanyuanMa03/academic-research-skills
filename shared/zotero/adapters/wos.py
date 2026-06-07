#!/usr/bin/env python3
"""Web of Science adapter for Zotero integration.

WoS-specific logic:
- Author parsing: "LastName, FirstInitials" format
- Extra field: WoS ID, citation counts, JIF, JCR quartile, research areas
- URL: WoS full-record link via accession number
- No PDF attachment support (WoS API doesn't provide direct PDF links)
"""

from __future__ import annotations


def build_zotero_item(paper: dict) -> dict:
    """Build Zotero journalArticle item from WoS paper data."""
    # Handle authors - accept both string ("A; B; C") and list formats
    authors_raw = paper.get("authors", [])
    if isinstance(authors_raw, str):
        authors_raw = [a.strip() for a in authors_raw.split(";") if a.strip()]

    creators = []
    for name in authors_raw:
        name = name.strip()
        if not name:
            continue
        # WoS standard format: "LastName, FirstInitials" e.g. "Gronroos, C"
        if "," in name:
            parts = name.split(",", 1)
            creators.append(
                {
                    "lastName": parts[0].strip(),
                    "firstName": parts[1].strip(),
                    "creatorType": "author",
                }
            )
        else:
            creators.append({"name": name, "creatorType": "author"})

    # Build date
    date = paper.get("published", "") or str(paper.get("year", ""))

    item = {
        "itemType": "journalArticle",
        "title": paper.get("title", ""),
        "abstractNote": paper.get("abstract", ""),
        "date": date,
        "language": paper.get("language", "en"),
        "libraryCatalog": "Web of Science",
        "publicationTitle": paper.get("source", ""),
        "volume": str(paper.get("volume", "") or ""),
        "issue": str(paper.get("issue", "") or ""),
        "pages": str(paper.get("pages", "") or ""),
        "DOI": paper.get("doi", ""),
        "ISSN": paper.get("issn", ""),
        "creators": creators,
        "tags": [],
        "attachments": [],
    }

    # URL
    wos_id = paper.get("accessionNumber", "") or paper.get("wosId", "")
    if wos_id:
        item["url"] = f"https://www.webofscience.com/wos/woscc/full-record/{wos_id}"

    # Keywords as tags
    for kw in paper.get("authorKeywords", []):
        item["tags"].append({"tag": kw, "type": 1})
    for kw in paper.get("keywordsPlus", []):
        item["tags"].append({"tag": kw, "type": 1})

    # Extra field - WoS-specific metadata
    extra_parts = []
    if wos_id:
        extra_parts.append(f"WoS ID: {wos_id}")
    cited = paper.get("citedCount", "") or paper.get("citations", "")
    if cited:
        alldb = paper.get("alldbCited", "") or paper.get("citationsAll", "")
        if alldb:
            extra_parts.append(f"Cited: {cited} (WOSCC) / {alldb} (All DB)")
        else:
            extra_parts.append(f"Cited: {cited}")
    if paper.get("jif"):
        jif_str = f'JIF: {paper["jif"]}'
        if paper.get("jifYear"):
            jif_str += f' ({paper["jifYear"]})'
        extra_parts.append(jif_str)
    if paper.get("jcrQuartile"):
        extra_parts.append(f'JCR: {paper["jcrQuartile"]}')
    if paper.get("researchAreas"):
        extra_parts.append(f'Research Areas: {paper["researchAreas"]}')
    if paper.get("wosCategories"):
        extra_parts.append(f'WoS Categories: {paper["wosCategories"]}')
    if paper.get("docType"):
        extra_parts.append(f'Document Type: {paper["docType"]}')
    if extra_parts:
        item["extra"] = "\n".join(extra_parts)

    return item


def extract_uri(paper: dict) -> str:
    """Extract source URI from WoS paper data."""
    wos_id = paper.get("accessionNumber", "") or paper.get("wosId", "")
    if wos_id:
        return f"https://www.webofscience.com/wos/woscc/full-record/{wos_id}"
    return paper.get("url", "")
