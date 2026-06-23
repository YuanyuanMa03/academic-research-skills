# Academic Research Skills

[中文介绍](./README_zh.md)

Claude Code plugin marketplace for academic research workflows.

## Quick Start (Any Agent)

Just send this to your agent:

```
Install all academic research skills from this repo:
https://github.com/YuanyuanMa03/academic-research-skills
```

Works with Claude Code, Copilot CLI, Codex, Gemini CLI, ChatGPT, Qwen, DeepSeek, or any LLM agent that can read GitHub repos.

## Platforms

| Platform | Prefix | Skills | Count |
|----------|--------|--------|-------|
| CNKI | `cnki-*` | search, download, export, journal browse, paper detail | 10 |
| Google Scholar | `gs-*` | search, advanced search, cited-by, fulltext, export | 6 |
| ScienceDirect | `sd-*` | search, download, export, journal browse, paper detail | 8 |
| Web of Science | `wos-*` | search, download, export, paper detail | 7 |
| PubMed | `pm-*` | search, advanced search, export, fulltext, paper detail | 6 |
| IEEE Xplore | `ieee-*` | search, download, export, journal browse, standards | 9 |
| Zotero CSL | `zotero-*` | citation style generation | 1 |
| Nature | `nature-*` | academic search, writing, polishing, figures, reader, patent, reviewer | 11 |

**58 skills total** — 8 academic platforms covered.

> Browser skills (CNKI, GS, SD, WoS, PubMed, IEEE) require [Chrome DevTools MCP](https://github.com/nicekid1/chrome-devtools-mcp). Nature skills are pure prompt-based and work with any LLM.

## Installation

### Claude Code (Recommended)

```bash
# Add marketplace
/plugin marketplace add YuanyuanMa03/academic-research-skills

# Install all skills
/plugin install cnki-advanced-search@academic-research-skills
/plugin install cnki-download@academic-research-skills
/plugin install cnki-export@academic-research-skills
/plugin install cnki-journal-index@academic-research-skills
/plugin install cnki-journal-search@academic-research-skills
/plugin install cnki-journal-toc@academic-research-skills
/plugin install cnki-navigate-pages@academic-research-skills
/plugin install cnki-paper-detail@academic-research-skills
/plugin install cnki-parse-results@academic-research-skills
/plugin install cnki-search@academic-research-skills
/plugin install gs-advanced-search@academic-research-skills
/plugin install gs-cited-by@academic-research-skills
/plugin install gs-export@academic-research-skills
/plugin install gs-fulltext@academic-research-skills
/plugin install gs-navigate-pages@academic-research-skills
/plugin install gs-search@academic-research-skills
/plugin install ieee-advanced-search@academic-research-skills
/plugin install ieee-download@academic-research-skills
/plugin install ieee-export@academic-research-skills
/plugin install ieee-journal-browse@academic-research-skills
/plugin install ieee-navigate-pages@academic-research-skills
/plugin install ieee-paper-detail@academic-research-skills
/plugin install ieee-parse-results@academic-research-skills
/plugin install ieee-search@academic-research-skills
/plugin install ieee-standards-search@academic-research-skills
/plugin install nature-academic-search@academic-research-skills
/plugin install nature-citation@academic-research-skills
/plugin install nature-data@academic-research-skills
/plugin install nature-figure@academic-research-skills
/plugin install nature-paper2ppt@academic-research-skills
/plugin install nature-polishing@academic-research-skills
/plugin install nature-reader@academic-research-skills
/plugin install nature-response@academic-research-skills
/plugin install nature-writing@academic-research-skills
/plugin install nature-paper-to-patent@academic-research-skills
/plugin install nature-reviewer@academic-research-skills
/plugin install pm-advanced-search@academic-research-skills
/plugin install pm-export@academic-research-skills
/plugin install pm-fulltext@academic-research-skills
/plugin install pm-navigate-pages@academic-research-skills
/plugin install pm-paper-detail@academic-research-skills
/plugin install pm-search@academic-research-skills
/plugin install sd-advanced-search@academic-research-skills
/plugin install sd-download@academic-research-skills
/plugin install sd-export@academic-research-skills
/plugin install sd-journal-browse@academic-research-skills
/plugin install sd-navigate-pages@academic-research-skills
/plugin install sd-paper-detail@academic-research-skills
/plugin install sd-parse-results@academic-research-skills
/plugin install sd-search@academic-research-skills
/plugin install wos-dom@academic-research-skills
/plugin install wos-download@academic-research-skills
/plugin install wos-export@academic-research-skills
/plugin install wos-navigate-pages@academic-research-skills
/plugin install wos-paper-detail@academic-research-skills
/plugin install wos-parse-results@academic-research-skills
/plugin install wos-search@academic-research-skills
/plugin install zotero-csl@academic-research-skills
```

### Copilot CLI

```bash
git clone https://github.com/YuanyuanMa03/academic-research-skills.git
mkdir -p ~/.copilot/skills
cp -R academic-research-skills/plugins/*/skills/* ~/.copilot/skills/
```

| Skill tool | Copilot CLI equivalent |
|------------|----------------------|
| `Read` | `view` |
| `Write` | `create` |
| `Edit` | `edit` |
| `Bash` | `bash` |
| `Grep` | `grep` |
| `WebFetch` | `web_fetch` |

### Codex

```bash
git clone https://github.com/YuanyuanMa03/academic-research-skills.git
mkdir -p ~/.codex/skills
cp -R academic-research-skills/plugins/*/skills/* ~/.codex/skills/
```

Or install specific skills:

```bash
# CNKI
cp -R academic-research-skills/plugins/cnki-advanced-search/skills/cnki-advanced-search ~/.codex/skills/
cp -R academic-research-skills/plugins/cnki-download/skills/cnki-download ~/.codex/skills/
cp -R academic-research-skills/plugins/cnki-export/skills/cnki-export ~/.codex/skills/
cp -R academic-research-skills/plugins/cnki-journal-index/skills/cnki-journal-index ~/.codex/skills/
cp -R academic-research-skills/plugins/cnki-journal-search/skills/cnki-journal-search ~/.codex/skills/
cp -R academic-research-skills/plugins/cnki-journal-toc/skills/cnki-journal-toc ~/.codex/skills/
cp -R academic-research-skills/plugins/cnki-navigate-pages/skills/cnki-navigate-pages ~/.codex/skills/
cp -R academic-research-skills/plugins/cnki-paper-detail/skills/cnki-paper-detail ~/.codex/skills/
cp -R academic-research-skills/plugins/cnki-parse-results/skills/cnki-parse-results ~/.codex/skills/
cp -R academic-research-skills/plugins/cnki-search/skills/cnki-search ~/.codex/skills/

# Google Scholar
cp -R academic-research-skills/plugins/gs-advanced-search/skills/gs-advanced-search ~/.codex/skills/
cp -R academic-research-skills/plugins/gs-cited-by/skills/gs-cited-by ~/.codex/skills/
cp -R academic-research-skills/plugins/gs-export/skills/gs-export ~/.codex/skills/
cp -R academic-research-skills/plugins/gs-fulltext/skills/gs-fulltext ~/.codex/skills/
cp -R academic-research-skills/plugins/gs-navigate-pages/skills/gs-navigate-pages ~/.codex/skills/
cp -R academic-research-skills/plugins/gs-search/skills/gs-search ~/.codex/skills/

# Nature
cp -R academic-research-skills/plugins/nature-academic-search/skills/nature-academic-search ~/.codex/skills/
cp -R academic-research-skills/plugins/nature-citation/skills/nature-citation ~/.codex/skills/
cp -R academic-research-skills/plugins/nature-data/skills/nature-data ~/.codex/skills/
cp -R academic-research-skills/plugins/nature-figure/skills/nature-figure ~/.codex/skills/
cp -R academic-research-skills/plugins/nature-paper2ppt/skills/nature-paper2ppt ~/.codex/skills/
cp -R academic-research-skills/plugins/nature-polishing/skills/nature-polishing ~/.codex/skills/
cp -R academic-research-skills/plugins/nature-reader/skills/nature-reader ~/.codex/skills/
cp -R academic-research-skills/plugins/nature-response/skills/nature-response ~/.codex/skills/
cp -R academic-research-skills/plugins/nature-writing/skills/nature-writing ~/.codex/skills/

# ScienceDirect
cp -R academic-research-skills/plugins/sd-advanced-search/skills/sd-advanced-search ~/.codex/skills/
cp -R academic-research-skills/plugins/sd-download/skills/sd-download ~/.codex/skills/
cp -R academic-research-skills/plugins/sd-export/skills/sd-export ~/.codex/skills/
cp -R academic-research-skills/plugins/sd-journal-browse/skills/sd-journal-browse ~/.codex/skills/
cp -R academic-research-skills/plugins/sd-navigate-pages/skills/sd-navigate-pages ~/.codex/skills/
cp -R academic-research-skills/plugins/sd-paper-detail/skills/sd-paper-detail ~/.codex/skills/
cp -R academic-research-skills/plugins/sd-parse-results/skills/sd-parse-results ~/.codex/skills/
cp -R academic-research-skills/plugins/sd-search/skills/sd-search ~/.codex/skills/

# Web of Science
cp -R academic-research-skills/plugins/wos-dom/skills/wos-dom ~/.codex/skills/
cp -R academic-research-skills/plugins/wos-download/skills/wos-download ~/.codex/skills/
cp -R academic-research-skills/plugins/wos-export/skills/wos-export ~/.codex/skills/
cp -R academic-research-skills/plugins/wos-navigate-pages/skills/wos-navigate-pages ~/.codex/skills/
cp -R academic-research-skills/plugins/wos-paper-detail/skills/wos-paper-detail ~/.codex/skills/
cp -R academic-research-skills/plugins/wos-parse-results/skills/wos-parse-results ~/.codex/skills/
cp -R academic-research-skills/plugins/wos-search/skills/wos-search ~/.codex/skills/
```

Skills load natively in Codex — just follow the instructions in SKILL.md.

| Skill tool | Codex equivalent |
|------------|------------------|
| `Read`, `Write`, `Edit` | Native file tools |
| `Bash` | Native shell tools |
| `Skill` tool | Skills load natively |

### Gemini CLI

```bash
git clone https://github.com/YuanyuanMa03/academic-research-skills.git
mkdir -p ~/.gemini/skills
cp -R academic-research-skills/plugins/*/skills/* ~/.gemini/skills/
```

| Skill tool | Gemini CLI equivalent |
|------------|----------------------|
| `Read` | `read_file` |
| `Write` | `write_file` |
| `Edit` | `replace` |
| `Bash` | `run_shell_command` |
| `Grep` | `grep_search` |
| `Skill` tool | `activate_skill` |
| `WebSearch` | `google_web_search` |
| `WebFetch` | `web_fetch` |

### OpenClaw

```bash
git clone https://github.com/YuanyuanMa03/academic-research-skills.git
mkdir -p ~/.openclaw/skills
cp -R academic-research-skills/plugins/*/skills/* ~/.openclaw/skills/
```

### Other Agents (Generic)

```bash
git clone https://github.com/YuanyuanMa03/academic-research-skills.git
cp -R academic-research-skills/plugins/cnki-search/skills/cnki-search /path/to/your/agent/skills/
```

**Skill structure (universal):**
```
<skill-name>/
├── SKILL.md              # Main instructions
├── references/           # Supporting guides (optional)
├── examples/             # Annotated examples (optional)
└── scripts/              # Helper scripts (optional)
```

### Don't Know Your Agent? Just Paste It

Paste the SKILL.md content directly into any LLM chat:

```bash
cat academic-research-skills/plugins/cnki-search/skills/cnki-search/SKILL.md
# Copy and paste into ChatGPT, Gemini, Claude, Qwen, DeepSeek, etc.
```

## Usage

- "Search CNKI for papers on neural rendering"
- "Find citing papers on Google Scholar"
- "Download this ScienceDirect paper"
- "Help me write a Nature-style introduction"

## Adding Plugins

1. Create `plugins/your-skill-name/skills/your-skill-name/SKILL.md`
2. Add `plugins/your-skill-name/.claude-plugin/plugin.json`
3. Add entry to `.claude-plugin/marketplace.json`
4. Submit a pull request

## Acknowledgments

Nature skills (`nature-*`) are based on [nature-skills](https://github.com/Yuan1z0825/nature-skills) by [@Yuan1z0825](https://github.com/Yuan1z0825).

## License

MIT
