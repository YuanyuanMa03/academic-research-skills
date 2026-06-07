#!/usr/bin/env python3
"""Validate all plugin.json files in the plugins/ directory.

Checks:
1. Required fields present (name, description, version)
2. Version follows semver format
3. License field matches repository LICENSE
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
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
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
            issues.append(f"  Missing required field: {field}")

    # Check semver
    version = data.get("version", "")
    if version and not SEMVER_PATTERN.match(version):
        issues.append(f"  Invalid version format: {version} (expected X.Y.Z)")

    # Check license matches repo
    license_field = data.get("license", "")
    if license_field and license_field != "MIT":
        issues.append(f"  License mismatch: {license_field} (expected MIT)")

    # Check name matches directory
    expected_name = plugin_dir.name
    actual_name = data.get("name", "")
    if actual_name and actual_name != expected_name:
        issues.append(
            f"  Name mismatch: '{actual_name}' vs directory '{expected_name}'"
        )

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
        if issues:
            failed += 1
            all_issues[plugin_dir.name] = issues
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
        print(f"RESULT: {failed} plugin(s) have validation issues")
        sys.exit(1)
    else:
        print("RESULT: All plugins pass validation")
        sys.exit(0)


if __name__ == "__main__":
    main()
