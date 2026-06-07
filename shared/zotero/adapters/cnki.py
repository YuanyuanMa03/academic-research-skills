#!/usr/bin/env python3
"""CNKI (China National Knowledge Infrastructure) adapter for Zotero integration.

CNKI-specific logic:
- ELEARNING format parsing
- Chinese language defaults (zh-CN)
- Extra field: dbcode, dbname, filename, CIF, AIF, CLC
- PDF download with CNKI-specific cookies/referer
"""

from __future__ import annotations

import re
import urllib.parse
from datetime import datetime, timezone


def parse_elearning(text: str) -> dict:
    """Parse CNKI ELEARNING export format into structured fields.

    ELEARNING is CNKI's proprietary citation export format containing
    fields like Title-题名, Author-作者, Source-刊名, etc.
    """
    text = text.replace("<br>", "\n").replace("\r", "")
    text = re.sub(r"<[^>]+>", "", text)  # strip HTML tags

    def get(key: str) -> str:
        m = re.search(rf"{re.escape(key)}:[ \t]*(.+?)(?=\n|$)", text)
        return m.group(1).strip() if m else ""

    return {
        "title": get("Title-题名"),
        "authors": [a.strip() for a in get("Author-作者").split(";") if a.strip()],
        "journal": get("Source-刊名"),
        "year": get("Year-年"),
        "pubTime": get("PubTime-出版时间"),
        "keywords": [k.strip() for k in get("Keyword-关键词").split(";") if k.strip()],
        "abstract": get("Summary-摘要"),
        "volume": get("Roll-卷"),
        "issue": get("Period-期"),
        "pageCount": get("PageCount-页数"),
        "pages": get("Page-页码"),
        "organs": get("Organ-机构"),
        "link": get("Link-链接"),
        "srcDb": get("SrcDatabase-来源库"),
    }


def build_zotero_item(paper: dict) -> dict:
    """Build Zotero item JSON from CNKI paper data."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    item = {
        "itemType": "journalArticle",
        "title": paper.get("title", ""),
        "abstractNote": paper.get("abstract", ""),
        "date": paper.get("pubTime") or paper.get("year", ""),
        "language": "zh-CN",
        "libraryCatalog": "CNKI",
        "accessDate": now,
        "volume": paper.get("volume", ""),
        "pages": paper.get("pages", ""),
        "publicationTitle": paper.get("journal", ""),
        "issue": paper.get("issue", ""),
        "creators": [
            {"name": a, "creatorType": "author"} for a in paper.get("authors", [])
        ],
        "tags": [{"tag": k, "type": 1} for k in paper.get("keywords", [])],
        "attachments": [],
    }

    # URL
    dbcode = paper.get("dbcode", "")
    dbname = paper.get("dbname", "")
    filename = paper.get("filename", "")
    if dbcode and dbname and filename:
        item["url"] = (
            f"https://kns.cnki.net/KCMS/detail/detail.aspx"
            f"?dbcode={urllib.parse.quote(dbcode)}"
            f"&dbname={urllib.parse.quote(dbname)}"
            f"&filename={urllib.parse.quote(filename)}"
        )
    elif paper.get("link"):
        item["url"] = paper["link"]

    # ISSN
    if paper.get("issn"):
        item["ISSN"] = paper["issn"]

    # Extra field - CNKI-specific metadata
    extra_parts = []
    if paper.get("journalEN"):
        extra_parts.append(f"original-container-title: {paper['journalEN']}")
    if paper.get("foundation"):
        extra_parts.append(f"foundation: {paper['foundation']}")
    if paper.get("downloadCount"):
        extra_parts.append(f"download: {paper['downloadCount']}")
    if paper.get("album"):
        extra_parts.append(f"album: {paper['album']}")
    if paper.get("clcCode"):
        extra_parts.append(f"CLC: {paper['clcCode']}")
    if dbcode:
        extra_parts.append(f"dbcode: {dbcode}")
    if dbname:
        extra_parts.append(f"dbname: {dbname}")
    if filename:
        extra_parts.append(f"filename: {filename}")
    if paper.get("publicationTag"):
        extra_parts.append(f"publicationTag: {paper['publicationTag']}")
    if paper.get("cif"):
        extra_parts.append(f"CIF: {paper['cif']}")
    if paper.get("aif"):
        extra_parts.append(f"AIF: {paper['aif']}")
    if extra_parts:
        item["extra"] = "\n".join(extra_parts)

    return item


def extract_uri(paper: dict) -> str:
    """Extract source URI from CNKI paper data."""
    return paper.get("pageUrl", paper.get("link", ""))


def build_item_from_elearning(paper: dict) -> dict:
    """Build Zotero item from raw CNKI ELEARNING export data.

    Merges page-level fields (issn, dbcode, etc.) into parsed ELEARNING data.
    """
    parsed = parse_elearning(paper["ELEARNING"])
    # Merge page-level fields into parsed data
    merge_fields = [
        "issn",
        "dbcode",
        "dbname",
        "filename",
        "clcCode",
        "journalEN",
        "foundation",
        "downloadCount",
        "album",
        "publicationTag",
        "cif",
        "aif",
        "pageUrl",
    ]
    for k in merge_fields:
        if k in paper and paper[k]:
            parsed[k] = paper[k]
    return build_zotero_item(parsed)
