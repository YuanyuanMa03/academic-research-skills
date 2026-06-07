#!/usr/bin/env python3
"""Tests for platform adapters."""

from __future__ import annotations

import sys
import os

import pytest

# Add repo root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))


class TestWoSAdapter:
    def test_build_zotero_item_basic(self):
        from shared.zotero.adapters.wos import build_zotero_item

        paper = {
            "title": "Test Paper",
            "authors": "Smith, J; Doe, A",
            "source": "Nature",
            "year": 2024,
            "doi": "10.1234/test",
        }
        item = build_zotero_item(paper)
        assert item["itemType"] == "journalArticle"
        assert item["title"] == "Test Paper"
        assert item["publicationTitle"] == "Nature"
        assert len(item["creators"]) == 2
        assert item["creators"][0]["lastName"] == "Smith"
        assert item["creators"][0]["firstName"] == "J"
        assert item["DOI"] == "10.1234/test"

    def test_build_zotero_item_wos_metadata(self):
        from shared.zotero.adapters.wos import build_zotero_item

        paper = {
            "title": "WoS Paper",
            "authors": [],
            "accessionNumber": "WOS:000123456789",
            "citedCount": "42",
            "jif": "5.2",
            "jifYear": "2024",
            "jcrQuartile": "Q1",
            "docType": "Article",
        }
        item = build_zotero_item(paper)
        assert "WoS ID: WOS:000123456789" in item["extra"]
        assert "JIF: 5.2" in item["extra"]
        assert "JCR: Q1" in item["extra"]

    def test_extract_uri(self):
        from shared.zotero.adapters.wos import extract_uri

        assert "WOS:000123456789" in extract_uri({"accessionNumber": "WOS:000123456789"})
        assert extract_uri({}) == ""


class TestGSAdapter:
    def test_build_zotero_item_basic(self):
        from shared.zotero.adapters.gs import build_zotero_item

        paper = {
            "title": "GS Paper",
            "authors": [{"lastName": "Smith", "firstName": "J"}],
            "journal": "Science",
            "pubdate": "2024",
            "pmid": "12345678",
        }
        item = build_zotero_item(paper)
        assert item["itemType"] == "journalArticle"
        assert "pubmed" in item["url"]
        assert "PMID: 12345678" in item["extra"]

    def test_parse_pubmed_authors(self):
        from shared.zotero.adapters.gs import parse_pubmed_authors

        creators = parse_pubmed_authors("Smith JA, Doe B")
        assert len(creators) == 2
        assert creators[0]["lastName"] == "Smith"
        assert creators[0]["firstName"] == "JA"

    def test_resolve_pdf_url_pmc_fallback(self):
        from shared.zotero.adapters.gs import resolve_pdf_url

        url = resolve_pdf_url({"pmcid": "PMC12345"})
        assert "PMC12345" in url
        assert url == ""  # pmcid_base not provided

    def test_resolve_pdf_url_direct(self):
        from shared.zotero.adapters.gs import resolve_pdf_url

        url = resolve_pdf_url({"pdfUrl": "https://example.com/paper.pdf"})
        assert url == "https://example.com/paper.pdf"


class TestCNKIAdapter:
    def test_parse_elearning(self):
        from shared.zotero.adapters.cnki import parse_elearning

        text = (
            "Title-题名: 深度学习综述<br>"
            "Author-作者: 张三;李四<br>"
            "Source-刊名: 计算机学报<br>"
            "Year-年: 2024<br>"
            "Keyword-关键词: 深度学习;神经网络"
        )
        result = parse_elearning(text)
        assert result["title"] == "深度学习综述"
        assert len(result["authors"]) == 2
        assert result["journal"] == "计算机学报"
        assert len(result["keywords"]) == 2

    def test_build_zotero_item_chinese(self):
        from shared.zotero.adapters.cnki import build_zotero_item

        paper = {
            "title": "测试论文",
            "authors": ["张三", "李四"],
            "journal": "计算机学报",
            "language": "zh-CN",
            "dbcode": "CJFQ",
            "dbname": "TEST",
            "filename": "test.xml",
            "cif": "5.2",
        }
        item = build_zotero_item(paper)
        assert item["language"] == "zh-CN"
        assert item["libraryCatalog"] == "CNKI"
        assert "CJFQ" in item["extra"]
        assert "CIF: 5.2" in item["extra"]
        assert "kns.cnki.net" in item["url"]


class TestSDAdapter:
    def test_build_zotero_item_basic(self):
        from shared.zotero.adapters.sd import build_zotero_item

        paper = {
            "title": "SD Paper",
            "authors": ["Smith, J.", "Doe, A."],
            "journal": "Cell",
            "doi": "10.1016/test",
            "articleType": "Research Article",
        }
        item = build_zotero_item(paper)
        assert item["libraryCatalog"] == "ScienceDirect"
        assert "articleType" in item.get("extra", "")
        assert len(item["creators"]) == 2

    def test_extract_uri(self):
        from shared.zotero.adapters.sd import extract_uri

        assert extract_uri({"url": "https://sd.com/paper"}) == "https://sd.com/paper"
        assert extract_uri({}) == ""
