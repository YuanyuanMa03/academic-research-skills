# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2026-10-29

Fixed hardening from the first end-to-end workflow test (evidence: `docs/test-evidence/2026-10-29-e2e-workflow/`):

- `scansci-pdf` SKILL.md: added the three-skill quick workflow (platform search → scansci-pdf retrieval → nature-* writing); search-source guidance (precise topics → platform skills like pm-search; scansci-pdf search is a broad discovery engine needing relevance filtering); strong recommendation to install the optional browser backend (`pip install "scansci-pdf[camoufox]"`) — without it only repository-direct-link OA papers are downloadable; two new troubleshooting rows (cache-hit returns old path ignoring `--output`; CLI has no citation command — agents should construct BibTeX from search metadata or enable the MCP server). Plugin version 1.0.0 → 1.0.1.
- `docs/REFERENCE.md`: topic-based search-source selection (biomedical → pm-search; materials/physics → nature-academic-search / scansci-pdf) and three new symptom rows.
- `docs/PLAYBOOK.md`: dated pitfalls from the live test (cache behavior, CLI citation gap, OA coverage without browser backend, search relevance, PubMed topic coverage).
- README/README_zh rewritten around the verified three-step workflow: the stale 2026-06-23 platform table is replaced by the 2026-10-29 end-to-end test results (per-stage verification table, honest boundaries section), with the old platform snapshot moved to PLAYBOOK.

## [1.2.0] - 2026-10-28

### Added
- **`scansci-pdf` bridge plugin**: literature retrieval now routes through the open-source [scansci-pdf](https://github.com/Rimagination/scansci-pdf) MCP server (MIT) — multi-route PDF download (open access → publisher API → institutional channels), batch queues, citation export (BibTeX/RIS/EndNote), Zotero push, and environment diagnostics. Chinese SKILL.md adapted from upstream's ZCode edition, with install bootstrap (Python >= 3.11) and compliance boundaries (gray sources require explicit user choice).
- **`AGENTS.md`**: canonical agent entry point (repository layout, dev commands, host adapters, guardrails). `CLAUDE.md` slimmed to a thin pointer.
- **`docs/PLAYBOOK.md`**: maintenance handbook — iron rules tied to real incidents, per-platform failure-signature table (dated), the pm-search dual-path paradigm, MCP template registry, and the decision record for the skill removals below.
- **`docs/REFERENCE.md`**: intent-routing manual ("want to do X → use skill Y") covering all 47 plugins, plus a migration table for removed skills and a symptom → first-action troubleshooting table.
- **`scripts/check_marketplace_consistency.py`**: enforces plugins/ ↔ Claude marketplace ↔ Codex marketplace ↔ REFERENCE.md consistency, and version alignment between manifests. Wired into pre-commit and CI.

### Removed
- 12 obsolete plugins, replaced by `scansci-pdf`: `cnki-download`, `gs-fulltext`, `ieee-download`, `sd-download`, `wos-download` (browser DOM + paywall, GS/IEEE were timing out), and `cnki-export`, `gs-export`, `ieee-export`, `pm-export`, `sd-export`, `wos-export`, `zotero-csl` (six near-duplicate `push_to_zotero.py` variants on the outdated Zotero Connector route). Migration table in `docs/REFERENCE.md`.

### Changed
- `scripts/check_shared_assets.py`: dropped the Zotero script manifest (targets deleted); now also flags browser skills that reference chrome-devtools without shipping `.mcp.json`; registered the scansci-pdf MCP template.
- Codex marketplace backfilled: `nature-paper-to-patent` and `nature-reviewer` now registered (they had silently lagged behind the Claude marketplace), with `.codex-plugin/plugin.json` added.
- One-time version alignment: 33 plugins whose Claude/Codex manifests drifted (1.0.0 vs 1.0.1) aligned to the highest version.
- README/README_zh: platform tables, install lists (47), acknowledgments; `docs/architecture.md` updated for the scansci-pdf layer.

### Fixed
- **lint.yml**: `HARDcoded`/`HARDCODED` variable-name typo meant the hardcoded-path check could never fail; fixed and verified zero false positives on current content.

## [1.1.0] - 2025-06-07

> Note: the `shared/zotero/` refactor described below was later reverted (commit c0b84e6) — this repo keeps every plugin standalone by design. The Zotero push scripts it describes were removed entirely in 1.2.0.

### Added
- **LICENSE**: Added MIT license file to repository root
- **.gitignore**: Added comprehensive ignore rules for Python, IDE, OS files
- **CI/CD**: GitHub Actions workflows for lint/validation (`lint.yml`) and testing (`test.yml`)
- **Validation scripts**: `scripts/validate_skills.py` and `scripts/validate_plugin_json.py`
- **Documentation**: CONTRIBUTING.md, architecture docs

### Fixed
- **Hardcoded paths**: Removed 6 hardcoded Windows paths (`e:\`, `E:/`) and 1 macOS path (`/Users/`) from SKILL.md and eval files
- **Legal inconsistency**: LICENSE file now matches `plugin.json` MIT declarations
