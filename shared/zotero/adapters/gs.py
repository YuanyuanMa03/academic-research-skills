#!/usr/bin/env python3
"""Google Scholar / PubMed adapter for Zotero integration.

Google Scholar-specific logic:
- Author parsing: PubMed "LastName Initials" format
- Extra field: PMID, PMCID, publication type
- URL: PubMed link via PMID
- PDF: PMC fallback for PDF download
"""

from __future__ import annotations

import re
from datetime import datetime, timezone


def parse_pubmed_authors(author_str: str) -> list[dict]:
    """Parse PubMed author string into Zotero creator list.

    PubMed format: "LastName Initials" e.g. "Vasa F, Misic B"
    or "LastName ForeName" e.g. "Smith John A"
    """
    if not author_str:
        return []
    authors = []
    for name in re.split(r",\s*", author_str):
        name = name.strip()
        if not name:
            continue
        parts = name.split(" ", 1)
        if len(parts) == 2:
            authors.append(
                {
                    "lastName": parts[0],
                    "firstName": parts[1],
                    "creatorType": "author",
                }
            )
        else:
            authors.append({"name": name, "creatorType": "author"})
    return authors


def build_zotero_item(paper: dict) -> dict:
    """Build Zotero item JSON from Google Scholar / PubMed paper data."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Parse authors - handle multiple input formats
    if isinstance(paper.get("authors"), list) and paper["authors"]:
        if isinstance(paper["authors"][0], dict):
            creators = []
            for a in paper["authors"]:
                if "lastName" in a:
                    creators.append(
                        {
                            "lastName": a["lastName"],
                            "firstName": a.get("firstName", a.get("initials", "")),
                            "creatorType": "author",
                        }
                    )
                elif "name" in a:
                    parts = a["name"].split(" ", 1)
                    if len(parts) == 2:
                        creators.append(
                            {
                                "lastName": parts[0],
                                "firstName": parts[1],
                                "creatorType": "author",
                            }
                        )
                    else:
                        creators.append({"name": a["name"], "creatorType": "author"})
        else:
            creators = parse_pubmed_authors(", ".join(paper["authors"]))
    elif isinstance(paper.get("authors"), str):
        creators = parse_pubmed_authors(paper["authors"])
    else:
        creators = []

    item = {
        "itemType": "journalArticle",
        "title": paper.get("title", ""),
        "abstractNote": paper.get("abstract", ""),
        "date": paper.get("pubDate") or paper.get("pubdate", ""),
        "language": paper.get("language", "en"),
        "libraryCatalog": paper.get("libraryCatalog", "PubMed"),
        "accessDate": now,
        "volume": paper.get("volume", ""),
        "pages": paper.get("pages", ""),
        "publicationTitle": paper.get("journal") or paper.get("fulljournalname", ""),
        "journalAbbreviation": paper.get("journalAbbr") or paper.get("source", ""),
        "issue": paper.get("issue", ""),
        "DOI": paper.get("doi", ""),
        "url": (
            f"https://pubmed.ncbi.nlm.nih.gov/{paper['pmid']}/"
            if paper.get("pmid")
            else ""
        ),
        "creators": creators,
        "tags": [{"tag": k, "type": 1} for k in paper.get("keywords", [])],
        "attachments": [],
    }

    # ISSN
    if paper.get("issn"):
        item["ISSN"] = paper["issn"]

    # Extra field with PubMed metadata
    extra_parts = []
    if paper.get("pmid"):
        extra_parts.append(f"PMID: {paper['pmid']}")
    if paper.get("pmcid"):
        extra_parts.append(f"PMCID: {paper['pmcid']}")
    if paper.get("pubtype"):
        pub_types = (
            paper["pubtype"]
            if isinstance(paper["pubtype"], str)
            else ", ".join(str(t) for t in paper["pubtype"])
        )
        extra_parts.append(f"Publication Type: {pub_types}")
    if extra_parts:
        item["extra"] = "\n".join(extra_parts)

    return item


def extract_uri(paper: dict) -> str:
    """Extract source URI from Google Scholar / PubMed paper data."""
    if paper.get("pmid"):
        return f"https://pubmed.ncbi.nlm.nih.gov/{paper['pmid']}/"
    return ""


def resolve_pdf_url(paper: dict) -> str:
    """Get the best PDF URL, with PMC fallback."""
    pdf_url = paper.get("pdfUrl") or paper.get("fullTextUrl") or ""
    if pdf_url:
        return pdf_url
    if paper.get("pmcid"):
        pmcid = paper["pmcid"]
        if not pmcid.startswith("PMC"):
            pmcid = f"PMC{pmcid}"
        return f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
    return ""
