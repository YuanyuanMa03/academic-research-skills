#!/usr/bin/env python3
"""Consistency check: plugin directories vs both marketplace manifests.

Every plugin under plugins/ must be registered in BOTH marketplaces
(.claude-plugin/marketplace.json for Claude Code, .agents/plugins/marketplace.json
for Codex), ship both plugin manifests, and be covered by docs/REFERENCE.md.
The Claude marketplace version must match the plugin's .claude-plugin/plugin.json.

Motivation (see docs/PLAYBOOK.md): the Codex marketplace silently lagged behind
the Claude marketplace (two plugins were never registered), and marketplace
entries drifted from plugin manifests. This check makes such drift fail CI
instead of shipping to users.

Usage:
    python3 scripts/check_marketplace_consistency.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MARKETPLACE = REPO_ROOT / ".claude-plugin/marketplace.json"
CODEX_MARKETPLACE = REPO_ROOT / ".agents/plugins/marketplace.json"
REFERENCE = REPO_ROOT / "docs/REFERENCE.md"


def plugin_dirs() -> set[str]:
    """Names of plugin directories (plugins/<name> containing skills/)."""
    return {
        p.name
        for p in (REPO_ROOT / "plugins").iterdir()
        if p.is_dir() and (p / "skills").is_dir()
    }


def marketplace_names(path: Path, source_key: str = "source") -> dict[str, str]:
    """Map plugin name -> declared source path for a marketplace manifest."""
    data = json.loads(path.read_text(encoding="utf-8"))
    result: dict[str, str] = {}
    for entry in data["plugins"]:
        source = entry["source"]
        result[entry["name"]] = (
            source[source_key] if isinstance(source, dict) else source
        )
    return result


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    dirs = plugin_dirs()
    claude = marketplace_names(CLAUDE_MARKETPLACE)
    codex = marketplace_names(CODEX_MARKETPLACE, source_key="path")

    # 1. Same plugin set everywhere.
    for label, names in (
        ("plugins/ dirs", dirs),
        ("Claude marketplace", set(claude)),
        ("Codex marketplace", set(codex)),
    ):
        for other_label, other in (
            ("plugins/ dirs", dirs),
            ("Claude marketplace", set(claude)),
            ("Codex marketplace", set(codex)),
        ):
            if label == other_label:
                continue
            for name in sorted(names - other):
                errors.append(f"{label} has '{name}' but {other_label} does not")

    # 2. Declared source paths must point at real plugin dirs.
    for name, source in claude.items():
        if not (REPO_ROOT / source).is_dir():
            errors.append(
                f"Claude marketplace: source '{source}' for {name} does not exist"
            )
    for name, source in codex.items():
        if not (REPO_ROOT / source).is_dir():
            errors.append(
                f"Codex marketplace: source '{source}' for {name} does not exist"
            )

    # 3. Every plugin ships both manifests; versions line up with the marketplace.
    claude_entry_version = {
        e["name"]: e.get("version", "")
        for e in json.loads(CLAUDE_MARKETPLACE.read_text(encoding="utf-8"))["plugins"]
    }
    for name in sorted(dirs):
        claude_manifest = REPO_ROOT / "plugins" / name / ".claude-plugin/plugin.json"
        codex_manifest = REPO_ROOT / "plugins" / name / ".codex-plugin/plugin.json"
        if not claude_manifest.exists():
            errors.append(f"{name}: missing .claude-plugin/plugin.json")
        else:
            version = json.loads(claude_manifest.read_text(encoding="utf-8")).get(
                "version", ""
            )
            if claude_entry_version.get(name, "") != version:
                errors.append(
                    f"{name}: Claude marketplace version "
                    f"'{claude_entry_version.get(name, '')}' != plugin.json version '{version}'"
                )
        if not codex_manifest.exists():
            errors.append(f"{name}: missing .codex-plugin/plugin.json")
        elif claude_manifest.exists():
            v1 = json.loads(claude_manifest.read_text(encoding="utf-8")).get(
                "version", ""
            )
            v2 = json.loads(codex_manifest.read_text(encoding="utf-8")).get(
                "version", ""
            )
            if v1 != v2:
                warnings.append(
                    f"{name}: .claude-plugin version {v1} != .codex-plugin version {v2}"
                )

    # 4. docs/REFERENCE.md must mention every plugin.
    if not REFERENCE.exists():
        errors.append("docs/REFERENCE.md is missing")
    else:
        text = REFERENCE.read_text(encoding="utf-8")
        for name in sorted(dirs):
            if name not in text:
                errors.append(f"{name} is not covered in docs/REFERENCE.md")

    for w in warnings:
        print(f"  [WARN] {w}")
    if errors:
        print("Marketplace consistency failures:")
        for e in errors:
            print(f"  [FAIL] {e}")
        return 1
    print(
        f"OK: {len(dirs)} plugins consistent across plugins/, both marketplaces, "
        "and docs/REFERENCE.md"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
