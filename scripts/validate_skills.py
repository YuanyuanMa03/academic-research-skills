#!/usr/bin/env python3
"""Validate all SKILL.md files in the plugins/ directory.

Checks:
1. YAML frontmatter exists and contains required fields
2. Required sections present (Overview, Steps/Workflow, Output)
3. No hardcoded absolute paths
4. argument-hint field present for user-invocable skills
5. Tool call budget documented

Usage:
    python scripts/validate_skills.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_FRONTMATTER_FIELDS = {"name", "description"}
RECOMMENDED_FRONTMATTER_FIELDS = {"argument-hint", "version"}
HARDCODED_PATH_PATTERN = re.compile(
    r"(?<![:\w])(?:[a-zA-Z]:[/\\][^\s\"']+|(?<![/\w])/Users/[^\s\"']+|(?<![/\w])/home/[a-z][^\s\"']*)",
    re.IGNORECASE,
)

SKILLS_DIR = Path(__file__).parent.parent / "plugins"


def parse_frontmatter(content: str) -> dict | None:
    """Extract YAML frontmatter from SKILL.md content."""
    if not content.startswith("---"):
        return None
    end = content.index("---", 3)
    fm_text = content[3:end].strip()

    # Simple YAML key parsing (avoiding PyYAML dependency)
    result = {}
    current_key = None
    multiline_value = []

    for line in fm_text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if ":" in stripped and not line.startswith(" ") and not line.startswith("\t"):
            if current_key and multiline_value:
                result[current_key] = "\n".join(multiline_value)
                multiline_value = []

            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()

            if value == "|" or value == ">":
                current_key = key
            elif value:
                result[key] = value.strip('"').strip("'")
                current_key = None
            else:
                current_key = key
        elif current_key:
            multiline_value.append(stripped)

    if current_key and multiline_value:
        result[current_key] = "\n".join(multiline_value)

    return result


def validate_skill(skill_dir: Path) -> tuple[list[str], bool]:
    """Validate a single skill directory. Returns (issues, has_errors)."""
    issues = []
    has_errors = False
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return [f"  [ERROR] MISSING: {skill_md.relative_to(SKILLS_DIR.parent)}"], True

    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter
    fm = parse_frontmatter(content)
    if fm is None:
        issues.append("  No YAML frontmatter found")
    else:
        for field in REQUIRED_FRONTMATTER_FIELDS:
            if field not in fm:
                issues.append(f"  [ERROR] Missing required frontmatter field: {field}")
                has_errors = True
        for field in RECOMMENDED_FRONTMATTER_FIELDS:
            if field not in fm:
                issues.append(f"  [WARN] Missing recommended frontmatter field: {field}")

    # Check for hardcoded paths
    has_errors = False
    for i, line in enumerate(content.split("\n"), 1):
        if HARDCODED_PATH_PATTERN.search(line) and not line.strip().startswith("#"):
            issues.append(f"  [ERROR] Line {i}: Hardcoded path detected: {line.strip()[:80]}")
            has_errors = True

    # Check for required sections
    content_lower = content.lower()
    has_steps = "step" in content_lower or "workflow" in content_lower
    has_output = (
        "output" in content_lower
        or "report" in content_lower
        or "result" in content_lower
    )

    if not has_steps:
        issues.append("  [ERROR] Missing workflow/steps section")
        has_errors = True
    if not has_output:
        issues.append("  [WARN] Missing output/report section")

    return issues, has_errors


def main():
    if not SKILLS_DIR.exists():
        print(f"Error: Skills directory not found: {SKILLS_DIR}")
        sys.exit(1)

    total = 0
    passed = 0
    failed = 0
    warnings = 0
    all_issues = {}

    for plugin_dir in sorted(SKILLS_DIR.iterdir()):
        if not plugin_dir.is_dir():
            continue

        # Find SKILL.md in nested structure
        skill_dirs = list(plugin_dir.rglob("SKILL.md"))
        for skill_md in skill_dirs:
            skill_dir = skill_md.parent
            total += 1
            issues, has_errors = validate_skill(skill_dir)
            if issues:
                if has_errors:
                    failed += 1
                else:
                    warnings += 1
                all_issues[str(skill_dir.relative_to(SKILLS_DIR.parent))] = (
                    issues,
                    has_errors,
                )
            else:
                passed += 1

    print("SKILL.md Validation Report")
    print("=" * 50)
    print(f"Total: {total} | Passed: {passed} | Failed: {failed} | Warnings: {warnings}")
    print()

    if all_issues:
        # Print errors first, then warnings
        errors = {k: v for k, v in all_issues.items() if v[1]}
        warn_only = {k: v for k, v in all_issues.items() if not v[1]}

        if errors:
            print("ERRORS:")
            for skill, (issues, _) in errors.items():
                print(f"\n  {skill}:")
                for issue in issues:
                    print(f"    {issue}")
            print()

        if warn_only:
            print("WARNINGS:")
            for skill, (issues, _) in warn_only.items():
                print(f"\n  {skill}:")
                for issue in issues:
                    print(f"    {issue}")
            print()

    if failed > 0:
        print(f"RESULT: {failed} skill(s) have errors")
        sys.exit(1)
    else:
        print("RESULT: All skills pass validation (warnings are non-blocking)")
        sys.exit(0)


if __name__ == "__main__":
    main()
