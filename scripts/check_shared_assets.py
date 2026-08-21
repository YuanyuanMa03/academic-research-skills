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
2. Every plugins/*/skills/*/scripts/push_to_zotero.py must match the hash
   recorded in ZOTERO_SCRIPT_MANIFEST. The six platform variants are
   intentionally different; editing one copy must be a conscious decision,
   so regenerate the manifest entry (run with --update) and review whether
   the other five copies need the same fix.

Usage:
    python3 scripts/check_shared_assets.py           # check (CI mode)
    python3 scripts/check_shared_assets.py --update  # print refreshed manifest
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
_EXEMPLARS = {
    "chrome-devtools": REPO_ROOT / "plugins/cnki-search/.mcp.json",
    "academic-search": REPO_ROOT / "plugins/nature-academic-search/.mcp.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zotero_manifest() -> dict[str, str]:
    """Current relative-path -> sha256 map for all push_to_zotero.py copies."""
    return {
        str(p.relative_to(REPO_ROOT)): sha256(p)
        for p in sorted(REPO_ROOT.glob("plugins/*/skills/*/scripts/push_to_zotero.py"))
    }


def check_mcp() -> list[str]:
    allowed = {sha256(p) for p in _EXEMPLARS.values()}
    errors = []
    for path in sorted(REPO_ROOT.glob("plugins/*/.mcp.json")):
        digest = sha256(path)
        if digest not in allowed:
            errors.append(
                f"{path.relative_to(REPO_ROOT)} does not match any canonical "
                f".mcp.json template (sha256 {digest[:12]}…). If you added a new "
                "MCP server shape, register it in scripts/check_shared_assets.py."
            )
    return errors


def check_zotero(recorded: dict[str, str]) -> list[str]:
    errors = []
    current = zotero_manifest()
    for path, digest in sorted(current.items()):
        if path not in recorded:
            errors.append(
                f"new copy {path} is not in ZOTERO_SCRIPT_MANIFEST "
                "(run scripts/check_shared_assets.py --update and review)"
            )
        elif recorded[path] != digest:
            errors.append(
                f"{path} changed (expected {recorded[path][:12]}…, got {digest[:12]}…). "
                "If intended, update ZOTERO_SCRIPT_MANIFEST and check whether the "
                "other push_to_zotero.py copies need the same fix."
            )
    for path in recorded:
        if path not in current:
            errors.append(f"manifest entry {path} no longer exists on disk")
    return errors


def print_manifest() -> None:
    print("# Paste into ZOTERO_SCRIPT_MANIFEST in scripts/check_shared_assets.py:")
    print("ZOTERO_SCRIPT_MANIFEST = {")
    for path, digest in zotero_manifest().items():
        print(f'    "{path}": "{digest}",')
    print("}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--update",
        action="store_true",
        help="print refreshed manifest instead of checking",
    )
    args = ap.parse_args()

    if args.update:
        print_manifest()
        return 0

    errors = check_mcp() + check_zotero(ZOTERO_SCRIPT_MANIFEST)
    if errors:
        print("Shared-asset drift detected:")
        for e in errors:
            print(f"  [FAIL] {e}")
        return 1
    print(
        f"OK: .mcp.json templates consistent; {len(ZOTERO_SCRIPT_MANIFEST)} "
        "push_to_zotero.py copies match manifest"
    )
    return 0


# Recorded SHA-256 of every push_to_zotero.py copy (platform variants are
# intentionally different — this manifest only guards against silent drift).
# Regenerate with: python3 scripts/check_shared_assets.py --update
ZOTERO_SCRIPT_MANIFEST = {
    "plugins/cnki-export/skills/cnki-export/scripts/push_to_zotero.py": "c4d5bbda7ff568aea931ad153139b975842c756e96d57847838435fa7db4a5a3",
    "plugins/gs-export/skills/gs-export/scripts/push_to_zotero.py": "65f2a5650ed459b73df23db7965a9120d8b0e2a986d41930474e257ee10544c7",
    "plugins/ieee-export/skills/ieee-export/scripts/push_to_zotero.py": "5b31abae65d4b49800bb0ea6e12385e7172dac4d66419b3a7e427748ee4a62c2",
    "plugins/pm-export/skills/pm-export/scripts/push_to_zotero.py": "65f2a5650ed459b73df23db7965a9120d8b0e2a986d41930474e257ee10544c7",
    "plugins/sd-export/skills/sd-export/scripts/push_to_zotero.py": "4fcd50c48c93b7e6b8d81a1acc58a85826fec4ec957d7c4d7415025b777c2f18",
    "plugins/wos-export/skills/wos-export/scripts/push_to_zotero.py": "eb17be894fc9c5ebd8cf37dbdce03c1c4a75b62ebbc584048c872a2cb4c35484",
}


if __name__ == "__main__":
    sys.exit(main())
