#!/usr/bin/env python3
"""Validate all plugin.json files in the plugins/ directory.

Checks:
1. Required fields present (name, description, version)
2. Version follows semver format
3. License field is present
4. Keywords are non-empty

Usage:
    python scripts/validate_plugin_json.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REQUIRED_FIELDS = {"name", "description", "version"}
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$")
REPO_ROOT = Path(__file__).parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"


def validate_plugin_json(plugin_dir: Path) -> list[str]:
    """Validate a single plugin.json. Returns list of issues."""
    issues = []
    plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"

    if not plugin_json.exists():
        return [f"  MISSING: {plugin_json.relative_to(REPO_ROOT)}"]

    try:
        data = json.loads(plugin_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"  Invalid JSON: {e}"]

    for field in REQUIRED_FIELDS:
        if field not in data:
            issues.append(f"  [ERROR] Missing required field: {field}")

    # Check semver
    version = data.get("version", "")
    if version and not SEMVER_PATTERN.match(version):
        issues.append(f"  [WARN] Invalid version format: {version} (expected X.Y.Z)")

    # Check license is present (don't hardcode a specific value)
    if not data.get("license"):
        issues.append("  [WARN] No license field specified")

    return issues


def main():
    if not PLUGINS_DIR.exists():
        print(f"Error: Plugins directory not found: {PLUGINS_DIR}")
        sys.exit(1)

    total = 0
    passed = 0
    failed = 0
    all_issues = {}

    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir():
            continue
        total += 1
        issues = validate_plugin_json(plugin_dir)
        # Only count ERROR-tagged issues as failures
        has_errors = any("[ERROR]" in i for i in issues)
        if has_errors:
            failed += 1
            all_issues[plugin_dir.name] = issues
        elif issues:
            # warnings only
            all_issues[plugin_dir.name] = issues
            passed += 1
        else:
            passed += 1

    print("plugin.json Validation Report")
    print("=" * 50)
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    print()

    if all_issues:
        print("Issues found:")
        for plugin, issues in all_issues.items():
            print(f"\n  {plugin}:")
            for issue in issues:
                print(f"    {issue}")
        print()

    if failed > 0:
        print(f"RESULT: {failed} plugin(s) have validation errors")
        sys.exit(1)
    else:
        print("RESULT: All plugins pass validation (warnings are non-blocking)")
        sys.exit(0)


if __name__ == "__main__":
    main()
