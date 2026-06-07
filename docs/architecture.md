# Architecture Overview

## System Design

academic-research-skills is a plugin marketplace for AI-powered academic research tools. Each plugin provides skills that integrate with AI coding assistants (Claude Code, Copilot CLI, Codex, etc.) via the SKILL.md protocol.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    AI Assistant Runtime                   │
│              (Claude Code / Copilot / Codex)              │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐ │
│  │ SKILL.md   │  │ JavaScript │  │ Chrome DevTools    │ │
│  │ Protocol   │  │ Execution  │  │ MCP Server         │ │
│  └─────┬──────┘  └─────┬──────┘  └─────────┬──────────┘ │
└────────┼───────────────┼───────────────────┼────────────┘
         │               │                   │
    ┌────▼────┐    ┌─────▼──────┐    ┌──────▼──────────┐
    │ SKILL   │    │ Browser    │    │ Zotero Desktop  │
    │ FILES   │    │ Automation │    │ localhost:23119 │
    └────┬────┘    └────────────┘    └─────────────────┘
         │
    ┌────▼────────────────────────────────────────────┐
    │                  plugins/                        │
    │                                                  │
    │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
    │  │ CNKI (10)│ │ GS  (6)  │ │ Nature (9)       │ │
    │  └──────────┘ └──────────┘ └──────────────────┘ │
    │  ┌──────────┐ ┌──────────┐                      │
    │  │ SD  (8)  │ │ WoS (7)  │                      │
    │  └──────────┘ └──────────┘                      │
    │                                                  │
    │  ┌─────────────────────────────────────────────┐ │
    │  │           shared/                            │ │
    │  │  zotero/core.py   → Unified API client      │ │
    │  │  zotero/pdf.py    → PDF download & attach    │ │
    │  │  zotero/cli.py    → CLI framework            │ │
    │  │  zotero/adapters/ → Platform-specific logic │ │
    │  │  output_templates/→ Standard report formats  │ │
    │  │  python_base/     → Logging & utilities      │ │
    │  └─────────────────────────────────────────────┘ │
    └──────────────────────────────────────────────────┘
```

## Plugin Lifecycle

1. **Discovery**: AI assistant reads SKILL.md frontmatter to understand skill capabilities
2. **Invocation**: User triggers skill via slash command or AI suggestion
3. **Execution**: AI follows SKILL.md workflow steps, executing code blocks and tool calls
4. **Output**: Results formatted per Output Contract section

## Shared Module Dependency Graph

```
plugins/cnki-export/scripts/push_to_zotero.py
    ├── shared/zotero/core.py      (ZoteroClient)
    ├── shared/zotero/pdf.py       (PdfHandler)
    ├── shared/zotero/cli.py       (CLI framework)
    └── shared/zotero/adapters/cnki.py  (CNKI adapter)

plugins/gs-export/scripts/push_to_zotero.py
    ├── shared/zotero/core.py
    ├── shared/zotero/pdf.py
    ├── shared/zotero/cli.py
    └── shared/zotero/adapters/gs.py    (GS/PubMed adapter)

plugins/sd-export/scripts/push_to_zotero.py
    ├── shared/zotero/core.py
    ├── shared/zotero/pdf.py
    └── shared/zotero/adapters/sd.py    (SD adapter, has argparse for RIS)

plugins/wos-export/scripts/push_to_zotero.py
    ├── shared/zotero/core.py
    ├── shared/zotero/cli.py
    └── shared/zotero/adapters/wos.py   (WoS adapter, no PDF support)
```

## Platform Integration Patterns

| Platform | Browser MCP | API Access | PDF Source |
|----------|:-----------:|:----------:|:----------:|
| CNKI | Yes (DOM scraping) | Export API only | CNKI CDN (requires cookies) |
| Google Scholar | Yes (DOM scraping) | None | Publisher + PMC fallback |
| ScienceDirect | Yes (DOM scraping) | None (RIS export) | Elsevier CDN (requires cookies) |
| Web of Science | Yes (DOM scraping) | Clarivate API | Not available |
| Nature | MCP Server | CrossRef + PubMed + arXiv APIs | Publisher |

## Adding a New Platform

To add support for a new academic platform:

1. Create `plugins/{platform}-{action}/` directories for each action
2. Write SKILL.md files following the specification in CONTRIBUTING.md
3. If Zotero integration is needed, create `shared/zotero/adapters/{platform}.py`
4. Add eval fixtures for each skill
5. Update marketplace.json
