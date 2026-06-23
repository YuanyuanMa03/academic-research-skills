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
    │  │ CNKI (10)│ │ GS  (6)  │ │ Nature (11)      │ │
    │  └──────────┘ └──────────┘ └──────────────────┘ │
    │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
    │  │ SD  (8)  │ │ WoS (7)  │ │ IEEE (9)         │ │
    │  └──────────┘ └──────────┘ └──────────────────┘ │
    │  ┌──────────┐ ┌──────────┐                      │
    │  │ PM  (6)  │ │ Zotero(1)│                      │
    │  └──────────┘ └──────────┘                      │
    └──────────────────────────────────────────────────┘
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

## Platform Integration Patterns

| Platform | Browser MCP | Zotero Export | Export Method |
|----------|:-----------:|:-------------:|---------------|
| CNKI | Yes (DOM scraping) | Yes | Self-contained script (localhost:23119) |
| Google Scholar | Yes (DOM scraping) | Yes | Self-contained script (localhost:23119) |
| ScienceDirect | Yes (DOM scraping) | Yes | Self-contained script (localhost:23119) |
| Web of Science | Yes (DOM scraping) | Yes | Self-contained script (localhost:23119) |
| PubMed | Yes | Yes | Self-contained script (localhost:23119) |
| IEEE Xplore | Yes | Yes | Self-contained script (localhost:23119) |
| Nature | No | No | Pure prompt-based |

## Zotero Integration

Export skills (`*-export`) use Zotero's local Connector API at `http://127.0.0.1:23119/connector`. Each export script is self-contained with:

- Deterministic session ID generation (content hash)
- Idempotent save operations (201 = saved, 409 = already saved)
- PDF attachment support
- Collection selection

## Adding a New Platform

To add support for a new academic platform:

1. Create `plugins/{platform}-{action}/` directories for each action
2. Write SKILL.md files following the specification in CONTRIBUTING.md
3. If Zotero integration is needed, create a self-contained `push_to_zotero.py` script
4. Add eval fixtures for each skill
5. Update marketplace.json
