# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

academic-research-skills is a plugin marketplace for AI-powered academic research tools. It provides 56+ skills across 8 academic platforms (CNKI, Google Scholar, ScienceDirect, Web of Science, PubMed, IEEE Xplore, Nature, Zotero) for Claude Code, Copilot CLI, Codex, Gemini CLI, and other AI assistants.

## Repository Structure

```
academic-research-skills/
├── shared/                  # Shared infrastructure (reuse, don't duplicate)
│   ├── zotero/              # Unified Zotero client & platform adapters
│   │   ├── core.py          # ZoteroClient (localhost:23119 API)
│   │   ├── pdf.py           # PDF download & attachment handling
│   │   ├── cli.py           # CLI framework for export scripts
│   │   └── adapters/        # Platform-specific: cnki.py, gs.py, sd.py, wos.py
│   ├── output_templates/    # Standard report formats (search, detail, export)
│   └── python_base/         # Logging config (get_logger)
├── plugins/                 # One directory per plugin
│   └── {platform}-{action}/
│       ├── .claude-plugin/
│       │   └── plugin.json  # Plugin metadata (required)
│       └── skills/
│           └── {skill-name}/
│               ├── SKILL.md     # Skill instructions (required)
│               ├── scripts/     # Executable scripts (optional)
│               ├── references/  # Supporting docs (optional)
│               └── evals/       # Test fixtures (optional)
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
ruff check shared/ scripts/ plugins/   # Lint Python files
ruff format --check shared/ scripts/   # Format check
```

### Testing
```bash
pytest shared/ -v                      # Run all tests
pytest shared/zotero/tests/ -v         # Run Zotero tests only
pytest shared/ --cov=shared --cov-report=term-missing --cov-fail-under=55
```

### Pre-commit Hooks (optional)
```bash
pre-commit install
pre-commit run --all-files
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

Required sections: Overview/Steps/Workflow, Output Contract (use templates from `shared/output_templates/`), Error Handling.

## Shared Modules

### Zotero Integration

When pushing citations to Zotero, use the shared module:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from shared.zotero.core import ZoteroClient
from shared.zotero.adapters.{platform} import build_zotero_item
```

Key classes:
- `ZoteroClient`: API client for Zotero's local Connector API (localhost:23119)
- `PdfHandler`: PDF download and attachment
- Platform adapters: `cnki.py`, `gs.py`, `sd.py`, `wos.py`

### Logging

Use structured logging instead of `print()`:

```python
from shared.python_base.logging_config import get_logger
logger = get_logger("skill-name")
logger.info("Processing %d items", count)
```

### Output Templates

Standard formats in `shared/output_templates/`:
- `search_report.md`: Search results format
- `detail_report.md`: Paper details format
- `export_report.md`: Export confirmation format

## Adding a New Plugin

1. Create directory structure:
   ```bash
   mkdir -p plugins/{platform}-{action}/.claude-plugin
   mkdir -p plugins/{platform}-{action}/skills/{platform}-{action}
   ```

2. Create `plugin.json` with required fields: `name`, `description`, `version`, `author`, `license`

3. Write `SKILL.md` following the specification

4. If Zotero integration needed, create adapter in `shared/zotero/adapters/{platform}.py`

5. Add entry to `.claude-plugin/marketplace.json`

6. Run validation:
   ```bash
   python scripts/validate_skills.py
   python scripts/validate_plugin_json.py
   ```

## CI/CD

Two GitHub Actions workflows:

1. **lint.yml**: Validates SKILL.md files, checks for hardcoded paths, lints Python with ruff
2. **test.yml**: Runs pytest on shared/ with coverage (Python 3.10, 3.11, 3.12)

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
- Use `argparse` for CLI arguments
- UTF-8 encoding safety (handled by `shared/zotero/core.py`)

## Platform Integration

| Platform | Browser MCP | API Access | Zotero Support |
|----------|:-----------:|:----------:|:--------------:|
| CNKI | Yes | Export API only | Yes |
| Google Scholar | Yes | None | Yes |
| ScienceDirect | Yes | RIS export | Yes |
| Web of Science | Yes | Clarivate API | Yes |
| PubMed | Yes | E-utilities | Yes |
| IEEE Xplore | Yes | None | Yes |
| Nature | No | CrossRef/PubMed/arXiv | No |
