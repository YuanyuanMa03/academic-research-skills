# Architecture Overview

## System Design

academic-research-skills is a plugin marketplace for AI-powered academic research tools. Each plugin provides skills that integrate with AI coding assistants (Claude Code, Codex, and others) via the SKILL.md protocol. 47 plugins: 46 platform search/navigation skills + 1 `scansci-pdf` retrieval bridge.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     AI Assistant Runtime                     │
│           (Claude Code / Codex / other agents)               │
│                                                              │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ SKILL.md   │  │ Chrome       │  │ scansci-pdf MCP      │ │
│  │ Protocol   │  │ DevTools MCP │  │ server (PyPI, MIT)   │ │
│  └─────┬──────┘  └─────┬────────┘  └──────────┬───────────┘ │
└────────┼───────────────┼──────────────────────┼─────────────┘
         │               │                      │
    ┌────▼────┐    ┌─────▼──────┐    ┌──────────▼───────────┐
    │ SKILL   │    │ Browser    │    │ OA / publisher API / │
    │ FILES   │    │ automation │    │ institutional routes │
    │(47 pips)│    │(platform   │    │ → PDF / citations /  │
    │         │    │ DOM flows) │    │   Zotero push        │
    └─────────┘    └────────────┘    └──────────────────────┘
```

## Plugin Lifecycle

1. **Discovery**: AI assistant reads SKILL.md frontmatter to understand skill capabilities
2. **Invocation**: User triggers skill via slash command or AI suggestion
3. **Execution**: AI follows SKILL.md workflow steps, executing code blocks and tool calls
4. **Output**: Results formatted per Output Contract section

## Skill Structure

Each skill follows this minimal structure:

```
{skill-name}/
├── SKILL.md           # Main instructions (required)
├── scripts/           # Executable scripts (optional)
└── references/        # Supporting docs (optional)
```

## Capability Layers

| Layer | What it does | How |
|---|---|---|
| Platform search/navigation (46 skills) | In-platform search, detail parsing, paging, journal browsing on CNKI/GS/SD/WoS/PubMed/IEEE; Nature writing assistance | Browser automation via Chrome DevTools MCP (PubMed search is API-first via a standalone NCBI script; pm-fulltext uses the PMC API) |
| Literature retrieval (`scansci-pdf`) | PDF download (tiered racing: OA → publisher API → institutional), batch queues, citation export, Zotero push, diagnostics | Bundled `.mcp.json` starts the scansci-pdf MCP server (`scansci-pdf run`, Python >= 3.11, pip install) |

## Integration Patterns

| Platform | Search path | Notes |
|----------|-------------|-------|
| CNKI / GS / SD / WoS / IEEE | Browser automation (chrome-devtools MCP) | GS and IEEE were timing out as of the 2026-06-23 test run — see `docs/PLAYBOOK.md` status table |
| WoS search | Platform-internal API via page fetch, DOM fallback on `no_session` | |
| PubMed | API-first dual path: standalone E-utilities script (default) or browser page-context fetch; never DOM scraping | pm-search is the paradigm for new search skills |
| PubMed fulltext | PMC API | |
| Nature | Pure prompt-based; `nature-academic-search` bundles its own MCP server | |
| Literature retrieval | scansci-pdf MCP server | Gray sources only with explicit user choice |

## scansci-pdf Integration

The `plugins/scansci-pdf` bridge plugin wires the external [scansci-pdf](https://github.com/Rimagination/scansci-pdf) PyPI package (MIT) into this marketplace: `.mcp.json` starts its stdio MCP server, and the Chinese SKILL.md routes intents (`scansci_pdf_download`, `scansci_pdf_citation`, `scansci_pdf_zotero_push`, `scansci_pdf_diagnostics`, …) with install bootstrap and compliance boundaries. No upstream code is vendored — upgrades flow from PyPI.

## Adding a New Plugin

1. Create `plugins/{platform}-{action}/` with `skills/{name}/SKILL.md`
2. Add `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`
3. Register in BOTH marketplaces (`.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`)
4. Add a routing entry in `docs/REFERENCE.md`
5. If browser automation is needed, copy the canonical `.mcp.json` from `plugins/cnki-search/`
6. Search skills follow the pm-search dual-path paradigm (standalone API script first, browser fallback, never DOM scraping when an API exists)
7. Run all `scripts/` checks (CI enforces marketplace consistency, MCP template drift, and REFERENCE coverage)
