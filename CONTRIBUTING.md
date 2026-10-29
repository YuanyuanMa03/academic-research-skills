# Contributing to academic-research-skills

Thank you for your interest in contributing! This guide covers how to create new skills and the quality standards we follow.

## Repository Structure

```
academic-research-skills/
├── plugins/                 # One directory per plugin
│   └── {plugin-name}/
│       ├── .claude-plugin/
│       │   └── plugin.json  # Claude plugin metadata (required)
│       ├── .codex-plugin/
│       │   └── plugin.json  # Codex plugin metadata (required)
│       ├── .mcp.json        # MCP config (browser skills / scansci-pdf)
│       └── skills/
│           └── {skill-name}/
│               ├── SKILL.md     # Skill instructions (required)
│               ├── scripts/     # Executable scripts (optional)
│               └── references/  # Reference documents (optional)
├── scripts/                 # Repository-level validation tools
└── docs/                    # PLAYBOOK.md (maintenance) + REFERENCE.md (routing)
```

## Creating a New Skill

### 1. Create the plugin directory

```bash
mkdir -p plugins/{series}-{action}/.claude-plugin plugins/{series}-{action}/.codex-plugin
mkdir -p plugins/{series}-{action}/skills/{series}-{action}
```

### 2. Create both plugin.json manifests

`.claude-plugin/plugin.json`:

```json
{
  "name": "{series}-{action}",
  "description": "Brief description of what this skill does.",
  "version": "1.0.0",
  "author": { "name": "YourGitHubUsername" },
  "license": "MIT",
  "keywords": ["academic", "research", "{series}"]
}
```

Also add `.codex-plugin/plugin.json` (see any existing plugin for the schema), register the plugin in BOTH `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json`, and add a routing entry in `docs/REFERENCE.md` — `scripts/check_marketplace_consistency.py` enforces all of this.

### 3. Write SKILL.md

Follow the SKILL.md Specification v1. Required structure:

```yaml
---
name: {series}-{action}
description: |
  English description.
  中文描述。
argument-hint: "<query>"
version: "1.0.0"
requires:
  - chrome-devtools-mcp
tags: [academic, research, {series}]
---
```

Required sections: Overview, Prerequisites, Workflow (numbered steps with executable code), Output Contract, Error Handling.

## Quality Standards

### SKILL.md Quality Checklist

- [ ] YAML frontmatter has all required fields (name, description, argument-hint)
- [ ] All code blocks are executable (tested manually)
- [ ] Output Contract section with standard format
- [ ] Error Handling section with recovery strategies
- [ ] Tool call budget documented
- [ ] No hardcoded absolute paths

### Python Script Quality Checklist

- [ ] Type hints on all function signatures
- [ ] Docstrings on all public functions
- [ ] Use `logging` module instead of `print()`
- [ ] Use `argparse` for CLI argument parsing
- [ ] Error handling with meaningful error messages
- [ ] UTF-8 encoding safety

### Testing

Add eval fixtures in `evals/evals.json`:

```json
{
  "skill_name": "{series}-{action}",
  "evals": [
    {
      "id": 1,
      "prompt": "Test prompt that exercises the skill",
      "expected_output": "Description of expected behavior"
    }
  ]
}
```

## Validation

Run all validation checks before submitting:

```bash
python scripts/validate_skills.py
python scripts/validate_plugin_json.py
```

## Naming Convention

Plugin names follow the pattern: `{platform}-{action}`

| Platform prefix | Full name |
|----------------|-----------|
| `cnki-` | China National Knowledge Infrastructure |
| `gs-` | Google Scholar |
| `sd-` | ScienceDirect |
| `wos-` | Web of Science |
| `pm-` | PubMed |
| `ieee-` | IEEE Xplore |
| `nature-` | Nature / Springer Nature |

Since v2.0.0 the convention is **one plugin per platform**: a platform plugin (e.g. `cnki-search`) contains the full workflow — the SKILL.md holds a scenario-routing table plus the primary flow, and each additional action (advanced search, paper detail, result parsing, paging, journal browsing) lives in `references/<action>.md`. Do not split per-action skills into separate plugins.

Download / citation export / Zotero push do NOT get per-platform skills — they all route through the `scansci-pdf` bridge plugin (see `docs/REFERENCE.md`).

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-skill-name`
2. Run validation: `python scripts/validate_skills.py`, `python scripts/validate_plugin_json.py`, `python scripts/check_shared_assets.py`, `python scripts/check_marketplace_consistency.py`
3. Ensure CI passes (lint + test workflows)
4. Submit PR with description of what the skill does
