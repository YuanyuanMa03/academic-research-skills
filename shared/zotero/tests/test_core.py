#!/usr/bin/env python3
"""Tests for shared/zotero/core.py — ZoteroClient unit tests.

Uses unittest.mock to avoid requiring a running Zotero instance.
"""

from __future__ import annotations

import sys
import os
from unittest.mock import patch, MagicMock

import pytest

# Add repo root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from shared.zotero.core import ZoteroClient


@pytest.fixture
def client():
    return ZoteroClient(id_prefix="test")


class TestMakeSessionId:
    """Test deterministic session ID generation."""

    def test_same_titles_same_id(self, client):
        items_a = [{"title": "Paper A"}, {"title": "Paper B"}]
        items_b = [{"title": "Paper B"}, {"title": "Paper A"}]
        assert client.make_session_id(items_a) == client.make_session_id(items_b)

    def test_different_titles_different_id(self, client):
        items_a = [{"title": "Paper A"}]
        items_b = [{"title": "Paper B"}]
        assert client.make_session_id(items_a) != client.make_session_id(items_b)

    def test_id_is_12_chars(self, client):
        items = [{"title": "Test Paper"}]
        session_id = client.make_session_id(items)
        assert len(session_id) == 12
        assert all(c in "0123456789abcdef" for c in session_id)

    def test_empty_title(self, client):
        items = [{}]
        session_id = client.make_session_id(items)
        assert len(session_id) == 12

    def test_chinese_title(self, client):
        items = [{"title": "深度学习在农业中的应用"}]
        session_id = client.make_session_id(items)
        assert len(session_id) == 12


class TestSaveItems:
    """Test save_items with mocked API responses."""

    @patch.object(ZoteroClient, "request")
    def test_save_success(self, mock_request, client):
        mock_request.return_value = (201, {"items": 1})
        items = [{"title": "Test Paper", "itemType": "journalArticle"}]
        status, msg, session_id = client.save_items(items)
        assert status == 201
        assert "Saved" in msg
        assert len(session_id) == 12

    @patch.object(ZoteroClient, "request")
    def test_save_duplicate_returns_success(self, mock_request, client):
        mock_request.return_value = (409, None)
        items = [{"title": "Already Saved Paper"}]
        status, msg, session_id = client.save_items(items)
        assert status == 201  # 409 treated as success
        assert "Already saved" in msg
        assert len(session_id) == 12

    @patch.object(ZoteroClient, "request")
    def test_save_zotero_not_running(self, mock_request, client):
        mock_request.return_value = (0, None)
        items = [{"title": "Test"}]
        status, msg, session_id = client.save_items(items)
        assert status == 0
        assert "not running" in msg.lower()
        assert len(session_id) == 12

    @patch.object(ZoteroClient, "request")
    def test_save_assigns_ids(self, mock_request, client):
        mock_request.return_value = (201, None)
        items = [{"title": "No ID Paper"}, {"title": "Another Paper"}]
        client.save_items(items)
        assert "id" in items[0]
        assert items[0]["id"].startswith("test_")
        assert "id" in items[1]


class TestPing:
    """Test Zotero connectivity check."""

    @patch.object(ZoteroClient, "request")
    def test_ping_success(self, mock_request, client):
        mock_request.return_value = (200, None)
        assert client.ping() is True

    @patch.object(ZoteroClient, "request")
    def test_ping_failure(self, mock_request, client):
        mock_request.return_value = (0, None)
        assert client.ping() is False

    @patch.object(ZoteroClient, "request")
    def test_ping_timeout(self, mock_request, client):
        mock_request.return_value = (-1, None)
        assert client.ping() is False


class TestImportRis:
    """Test RIS import functionality.

    import_ris uses urllib.request.urlopen directly (not self.request)
    because RIS is plain text, not JSON.
    """

    def test_empty_ris(self, client):
        result = client.import_ris("")
        assert result["success"] is False
        assert "Empty" in result["message"]

    def test_whitespace_ris(self, client):
        result = client.import_ris("   \n  ")
        assert result["success"] is False
        assert "Empty" in result["message"]

    @patch("urllib.request.urlopen")
    def test_ris_success(self, mock_urlopen, client):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"OK"
        mock_urlopen.return_value = mock_resp
        result = client.import_ris("TY  - JOUR\nTI  - Test\nER  -")
        assert result["success"] is True
        assert "Saved" in result["message"]

    @patch("urllib.request.urlopen")
    def test_ris_duplicate(self, mock_urlopen, client):
        """Test that HTTP 409 (Conflict) is treated as success."""
        from urllib.error import HTTPError
        import io

        mock_urlopen.side_effect = HTTPError(
            url="http://test",
            code=409,
            msg="Conflict",
            hdrs={},
            fp=io.BytesIO(b"Already exists"),
        )
        result = client.import_ris("TY  - JOUR\nTI  - Test\nER  -")
        assert result["success"] is True
        assert "Already saved" in result["message"]

    @patch("urllib.request.urlopen")
    def test_ris_connection_refused(self, mock_urlopen, client):
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("Connection refused")
        result = client.import_ris("TY  - JOUR\nTI  - Test\nER  -")
        assert result["success"] is False
        assert "Cannot connect" in result["message"]

    @patch("urllib.request.urlopen")
    def test_ris_http_error(self, mock_urlopen, client):
        from urllib.error import HTTPError
        import io

        mock_urlopen.side_effect = HTTPError(
            url="http://test",
            code=500,
            msg="Server Error",
            hdrs={},
            fp=io.BytesIO(b"Internal error"),
        )
        result = client.import_ris("TY  - JOUR\nTI  - Test\nER  -")
        assert result["success"] is False
        assert "HTTP 500" in result["message"]


class TestRequest:
    """Test the low-level request method."""

    @patch.object(ZoteroClient, "request")
    def test_request_with_empty_list(self, mock_request, client):
        """Ensure empty list [] is not converted to {}."""
        mock_request.return_value = (200, None)
        client.request("test", [])
        # Verify the mock was called with [] not {}
        mock_request.assert_called_once_with("test", [])


class TestListCollections:
    """Test collection listing."""

    @patch.object(ZoteroClient, "request")
    def test_list_collections_missing_keys(self, mock_request, client, capsys):
        """list_collections should not crash on missing name/id keys."""
        mock_request.return_value = (
            200,
            {
                "name": "Test",
                "id": "1",
                "targets": [
                    {"level": 0},  # missing name and id
                    {"name": "Sub", "id": "2", "level": 1},
                ],
            },
        )
        client.list_collections()
        captured = capsys.readouterr()
        assert "Test" in captured.out
        assert "?" in captured.out  # missing name shows as ?
