# CLAUDE.md

This file guides Claude Code when working in this repository.

**Read [`AGENTS.md`](AGENTS.md) first** — it is the canonical agent entry point: repository layout, development commands, host adapters, and guardrails (dual-marketplace sync, standalone-install constraint, PLAYBOOK pre-reading for browser/anti-scraping skills).

Quick reference — run all of these before committing (CI repeats them):

```bash
python scripts/validate_skills.py               # SKILL.md validation
python scripts/validate_plugin_json.py          # plugin.json validation
python scripts/check_shared_assets.py           # .mcp.json template drift
python scripts/check_marketplace_consistency.py # plugins/ <-> both marketplaces <-> REFERENCE.md
ruff check plugins/ scripts/ && ruff format --check plugins/ scripts/
```

Key facts:

- 16 plugins: 4 platform skills (`cnki-search`, `sd-search`, `wos-search`, `pm-search` — one per platform, sub-workflows in `references/`), 11 `nature-*` writing skills, 1 `scansci-pdf` retrieval bridge (paper download, citations, Zotero push via the scansci-pdf MCP server, MIT).
- Literature retrieval (download/export/Zotero) belongs to `scansci-pdf`; the old `*-download`/`*-export`/`zotero-csl` skills were removed (decision record in [`docs/PLAYBOOK.md`](docs/PLAYBOOK.md)).
- New plugins must be registered in BOTH marketplaces (`.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json`) and covered in `docs/REFERENCE.md`.
- Maintenance handbook (failure signatures, platform status, iron rules): [`docs/PLAYBOOK.md`](docs/PLAYBOOK.md). Intent-routing manual: [`docs/REFERENCE.md`](docs/REFERENCE.md).
