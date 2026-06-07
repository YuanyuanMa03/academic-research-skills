#!/usr/bin/env python3
"""Unified PDF download and attachment handling for Zotero integration.

Shared across all platform adapters that support PDF attachment
(Google Scholar, CNKI, ScienceDirect).
"""

from __future__ import annotations

import urllib.error
import urllib.request
from typing import Optional


PDF_DOWNLOAD_TIMEOUT = 60
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/136.0.0.0 Safari/537.36"
)


class PdfHandler:
    """Download PDFs and attach them to Zotero items.

    Handles platform-specific headers (cookies, referer) while
    sharing the core download/upload logic.
    """

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        default_referer: str = "",
        download_timeout: int = PDF_DOWNLOAD_TIMEOUT,
    ):
        self.user_agent = user_agent
        self.default_referer = default_referer
        self.download_timeout = download_timeout

    def download_pdf(
        self,
        pdf_url: str,
        cookies: str = "",
        referer: Optional[str] = None,
    ) -> tuple[Optional[bytes], str]:
        """Download PDF from URL.

        Returns:
            (pdf_bytes, error_message)
            On success: (bytes, "")
            On failure: (None, error_description)
        """
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/pdf,*/*",
        }
        if cookies:
            headers["Cookie"] = cookies
        if referer or self.default_referer:
            headers["Referer"] = referer or self.default_referer

        req = urllib.request.Request(pdf_url, headers=headers)
        try:
            resp = urllib.request.urlopen(req, timeout=self.download_timeout)
            data = resp.read()
            content_type = resp.headers.get("Content-Type", "")

            if len(data) < 1024:
                return None, f"Too small ({len(data)} bytes), likely a redirect page"
            if data[:5] != b"%PDF-" and "application/pdf" not in content_type:
                return None, f"Not a PDF (Content-Type: {content_type})"

            return data, ""
        except urllib.error.HTTPError as e:
            return None, f"HTTP {e.code}"
        except urllib.error.URLError as e:
            return None, f"URL error: {e.reason}"
        except TimeoutError:
            return None, f"Download timeout ({self.download_timeout}s)"
        except Exception as e:
            return None, str(e)

    def resolve_pdf_url(self, paper: dict, pmcid_base: str = "") -> str:
        """Get the best PDF URL from paper data.

        Checks pdfUrl, fullTextUrl, then falls back to PMC PDF URL
        if pmcid_base is provided.
        """
        pdf_url = paper.get("pdfUrl") or paper.get("fullTextUrl") or ""
        if pdf_url:
            return pdf_url

        # PMC fallback (used by Google Scholar / PubMed)
        if pmcid_base and paper.get("pmcid"):
            pmcid = paper["pmcid"]
            if not pmcid.startswith("PMC"):
                pmcid = f"PMC{pmcid}"
            return f"{pmcid_base}{pmcid}/pdf/"

        return ""

    def attach_pdfs(
        self,
        zotero_client,
        session_id: str,
        items: list[dict],
        papers: list[dict],
        cookies: str = "",
    ) -> tuple[int, int]:
        """Download and attach PDFs for a list of saved Zotero items.

        Args:
            zotero_client: ZoteroClient instance
            session_id: Session ID from save_items
            items: Built Zotero items (with 'id' assigned)
            papers: Original paper data dicts
            cookies: Optional cookies for PDF download

        Returns:
            (success_count, failure_count)
        """
        ok = 0
        fail = 0

        col = zotero_client.get_selected_collection()
        files_editable = col.get("filesEditable", True) if col else True
        if not files_editable:
            print("  (Target collection does not support file attachments, skipping PDF)")
            return 0, 0

        for i, (paper, item) in enumerate(zip(papers, items)):
            pdf_url = self.resolve_pdf_url(paper)
            if not pdf_url:
                continue

            item_id = item.get("id", f"item_{session_id}_{i}")

            pdf_bytes, err = self.download_pdf(pdf_url, cookies=cookies)
            if not pdf_bytes:
                print(f"  PDF skip: {err} ({pdf_url[:80]})")
                fail += 1
                continue

            att_status, att_msg = zotero_client.save_attachment(
                session_id, item_id, pdf_bytes, pdf_url
            )
            if att_status in (200, 201):
                size_mb = len(pdf_bytes) / 1024 / 1024
                print(f"  PDF attached ({size_mb:.1f} MB): {item.get('title', '?')[:60]}")
                ok += 1
            else:
                print(f"  PDF attach failed ({att_status}): {att_msg or ''}")
                fail += 1

        if ok > 0 or fail > 0:
            print(f"PDFs: {ok} attached, {fail} failed")

        return ok, fail
