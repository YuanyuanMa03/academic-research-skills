#!/usr/bin/env python3
"""Drift guard for shared assets replicated across plugins.

This repo duplicates a few assets across per-plugin packages (the packaging
model installs each plugin standalone, so copies are intentional). Duplication
is fine; *silent* divergence is not — e.g. commit 2a1a086 had to backfill
mcpServers config that only some plugins received.

Rules enforced:
1. Every plugins/*/.mcp.json must match one of the canonical templates by
   SHA-256 (see MCP_TEMPLATES). Adding a new MCP server shape requires
   registering it here deliberately.

History: this script previously also pinned SHA-256 hashes for six
push_to_zotero.py copies. Those skills (along with *-download and zotero-csl)
were removed when literature retrieval switched to the scansci-pdf MCP
server; see docs/PLAYBOOK.md for the decision record.

Usage:
    python3 scripts/check_shared_assets.py
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Canonical .mcp.json exemplars: every plugins/*/.mcp.json must be byte-identical
# to one of these. Adding a new MCP server shape means registering a new exemplar
# here deliberately.
MCP_TEMPLATES = {
    "chrome-devtools": REPO_ROOT / "plugins/cnki-search/.mcp.json",
    "academic-search": REPO_ROOT / "plugins/nature-academic-search/.mcp.json",
    "scansci-pdf": REPO_ROOT / "plugins/scansci-pdf/.mcp.json",
}

# Browser-automation skills that intentionally ship no .mcp.json:
# - wos-dom: static DOM-structure reference document, no runtime tools.
# - wos-parse-results: parses already-saved page snapshots offline.
# - nature-* prompt skills: no browser, no MCP needs.
# (Prompt-only and reference skills do not need MCP config.)
MCP_EXEMPT = {
    "wos-dom",
    "wos-parse-results",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_mcp() -> list[str]:
    allowed = {sha256(p) for p in MCP_TEMPLATES.values() if p.exists()}
    errors = []
    for path in sorted(REPO_ROOT.glob("plugins/*/.mcp.json")):
        digest = sha256(path)
        if digest not in allowed:
            errors.append(
                f"{path.relative_to(REPO_ROOT)} does not match any canonical "
                f".mcp.json template (sha256 {digest[:12]}…). If you added a new "
                "MCP server shape, register it in scripts/check_shared_assets.py."
            )
    # Browser-automation skills must ship an MCP config unless exempted above.
    for plugin_dir in sorted(REPO_ROOT.glob("plugins/*")):
        name = plugin_dir.name
        if name in MCP_EXEMPT:
            continue
        skill = plugin_dir / "skills" / name / "SKILL.md"
        if not skill.exists() or (plugin_dir / ".mcp.json").exists():
            continue
        text = skill.read_text(encoding="utf-8")
        if "chrome-devtools" in text:
            errors.append(
                f"{name} references the chrome-devtools MCP but ships no "
                ".mcp.json (copy plugins/cnki-search/.mcp.json, or add the "
                "plugin to MCP_EXEMPT with a reason in docs/PLAYBOOK.md)."
            )
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args()

    errors = check_mcp()
    if errors:
        print("Shared-asset drift detected:")
        for e in errors:
            print(f"  [FAIL] {e}")
        return 1
    print(f"OK: .mcp.json files match {len(MCP_TEMPLATES)} canonical templates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
