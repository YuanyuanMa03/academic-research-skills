# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

academic-research-skills is a plugin marketplace for AI-powered academic research tools. It provides 58+ skills across 8 academic platforms (CNKI, Google Scholar, ScienceDirect, Web of Science, PubMed, IEEE Xplore, Nature, Zotero) for Claude Code, Copilot CLI, Codex, Gemini CLI, and other AI assistants.

## Repository Structure

```
academic-research-skills/
├── plugins/                 # One directory per plugin
│   └── {platform}-{action}/
│       ├── .claude-plugin/
│       │   └── plugin.json  # Plugin metadata (required)
│       └── skills/
│           └── {skill-name}/
│               ├── SKILL.md     # Skill instructions (required)
│               ├── scripts/     # Executable scripts (optional)
│               └── references/  # Reference documents (optional)
├── scripts/                 # Validation tools
│   ├── validate_skills.py   # SKILL.md validator
│   └── validate_plugin_json.py
└── docs/
    └── architecture.md      # System architecture
```

## Development Commands

### Validation (run before committing)
```bash
python scripts/validate_skills.py      # Validate all SKILL.md files
python scripts/validate_plugin_json.py # Validate plugin.json files
```

### Linting
```bash
ruff check plugins/ scripts/           # Lint Python files
ruff format --check plugins/ scripts/  # Format check
```

## Plugin Architecture

### Two Plugin Types

1. **Browser-based skills** (CNKI, GS, SD, WoS, PubMed, IEEE): Use Chrome DevTools MCP for DOM automation. Each plugin.json includes `mcpServers` config for `chrome-devtools-mcp`.

2. **Pure prompt-based skills** (Nature): Work with any LLM, no browser required.

### Plugin Naming Convention

Pattern: `{platform}-{action}`

| Platform | Prefix |
|----------|--------|
| CNKI | `cnki-` |
| Google Scholar | `gs-` |
| ScienceDirect | `sd-` |
| Web of Science | `wos-` |
| PubMed | `pm-` |
| IEEE Xplore | `ieee-` |
| Nature | `nature-` |
| Zotero | `zotero-` |

Actions: `-search`, `-advanced-search`, `-download`, `-export`, `-paper-detail`, `-parse-results`, `-navigate-pages`, `-journal-browse`

### SKILL.md Specification

Required YAML frontmatter:
```yaml
---
name: {platform}-{action}
description: Brief description of what this skill does.
argument-hint: "<query>"
---
```

Required sections: Overview/Steps/Workflow, Output Contract, Error Handling.

## Adding a New Plugin

1. Create directory structure:
   ```bash
   mkdir -p plugins/{platform}-{action}/.claude-plugin
   mkdir -p plugins/{platform}-{action}/skills/{platform}-{action}
   ```

2. Create `plugin.json` with required fields: `name`, `description`, `version`, `author`, `license`

3. Write `SKILL.md` following the specification

4. Add entry to `.claude-plugin/marketplace.json`

5. Run validation:
   ```bash
   python scripts/validate_skills.py
   python scripts/validate_plugin_json.py
   ```

## CI/CD

Two GitHub Actions workflows:

1. **lint.yml**: Validates SKILL.md files, checks for hardcoded paths, lints Python with ruff
2. **test.yml**: Runs lint checks (shared/ tests removed)

Both run on push to `main` and `feature/**` branches, and on PRs to `main`.

## Common Patterns

### Hardcoded Path Detection

CI rejects any absolute paths in plugins:
- Windows: `C:\...`, `D:/...`
- macOS: `/Users/...`
- Linux: `/home/...`

Use relative paths or dynamic path resolution.

### Python Script Quality

- Type hints on all function signatures
- Docstrings on all public functions
- Use `logging` module for output
- UTF-8 encoding safety

## Platform Integration

| Platform | Browser MCP | Zotero Export |
|----------|:-----------:|:-------------:|
| CNKI | Yes | Yes (self-contained script) |
| Google Scholar | Yes | Yes (self-contained script) |
| ScienceDirect | Yes | Yes (self-contained script) |
| Web of Science | Yes | Yes (self-contained script) |
| PubMed | Yes | Yes (self-contained script) |
| IEEE Xplore | Yes | Yes (self-contained script) |
| Nature | No | No |

**Note**: Zotero export scripts are self-contained in each skill's `scripts/` directory, using Zotero's local Connector API (localhost:23119).
