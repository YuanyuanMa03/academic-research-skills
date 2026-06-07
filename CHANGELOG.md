# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-06-07

### Added
- **LICENSE**: Added MIT license file to repository root
- **.gitignore**: Added comprehensive ignore rules for Python, IDE, OS files
- **Shared Zotero module** (`shared/zotero/`): Unified Zotero Connector API client, PDF handler, and CLI framework
  - `core.py`: ZoteroClient with request, session management, save_items, save_attachment, import_ris
  - `pdf.py`: PdfHandler with download, PMC fallback, batch attachment
  - `cli.py`: Shared argparse-based CLI framework for all platform push scripts
  - `adapters/cnki.py`: CNKI ELEARNING parsing and item building
  - `adapters/gs.py`: PubMed author parsing and PMC PDF fallback
  - `adapters/sd.py`: ScienceDirect item building with RIS backward compatibility
  - `adapters/wos.py`: WoS author parsing and metadata enrichment
- **Shared output templates** (`shared/output_templates/`): Standard report templates for search, export, and detail skills
- **Shared Python base** (`shared/python_base/`): Logging configuration with JSON and text formatters
- **CI/CD**: GitHub Actions workflows for lint/validation (`lint.yml`) and testing (`test.yml`)
- **Validation scripts**: `scripts/validate_skills.py` and `scripts/validate_plugin_json.py`
- **Documentation**: CONTRIBUTING.md, architecture docs, troubleshooting guide

### Changed
- **Refactored push_to_zotero.py**: All 4 platform scripts (CNKI, GS, SD, WoS) now use shared module
  - Reduced from 4 self-contained scripts (~1411 lines) to 4 thin wrappers + 1 shared module (~1320 lines with full type hints and docs)
  - Unified CLI: all scripts now use argparse (was inconsistent: 3 used sys.argv, 1 used argparse)
  - Added type hints and docstrings to all Python code

### Fixed
- **Hardcoded paths**: Removed 6 hardcoded Windows paths (`e:\`, `E:/`) and 1 macOS path (`/Users/`) from SKILL.md and eval files
- **Legal inconsistency**: LICENSE file now matches `plugin.json` MIT declarations
