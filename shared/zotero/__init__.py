"""Unified Zotero integration for academic-research-skills.

Provides a shared Zotero client, PDF handling, and CLI framework.
Each platform (CNKI, Google Scholar, ScienceDirect, WoS) implements
a thin adapter on top of this shared core.
"""

from shared.zotero.core import ZoteroClient
from shared.zotero.pdf import PdfHandler

__all__ = ["ZoteroClient", "PdfHandler"]
