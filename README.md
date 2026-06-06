# Academic Research Skills Marketplace

[中文介绍](./README_zh.md)

Claude Code plugin marketplace for academic research workflows.

## Platforms

| Platform | Prefix | Skills |
|----------|--------|--------|
| CNKI | `cnki-*` | search, download, export, journal browse, paper detail |
| Google Scholar | `gs-*` | search, advanced search, cited-by, fulltext, export |
| ScienceDirect | `sd-*` | search, download, export, journal browse, paper detail |
| Web of Science | `wos-*` | search, download, export, paper detail |
| Nature | `nature-*` | academic search, writing, polishing, figures, reader |

## Installation

### Claude Code (Recommended)

```bash
# Add marketplace
/plugin marketplace add YuanyuanMa03/academic-research-skills-marketplace

# Install skills
/plugin install cnki-search@academic-research-skills-marketplace
/plugin install gs-search@academic-research-skills-marketplace
/plugin install nature-writing@academic-research-skills-marketplace
```

### Copilot CLI

```bash
# Clone the repo
git clone https://github.com/YuanyuanMa03/academic-research-skills-marketplace.git

# Copy skills to Copilot CLI skills directory
mkdir -p ~/.copilot/skills
cp -R academic-research-skills-marketplace/plugins/*/skills/* ~/.copilot/skills/

# Or install specific skills
cp -R academic-research-skills-marketplace/plugins/cnki-search/skills/cnki-search ~/.copilot/skills/
cp -R academic-research-skills-marketplace/plugins/gs-search/skills/gs-search ~/.copilot/skills/
```

Skills activate via `/skill` command or automatically when you ask about research tasks.

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
# Clone the repo
git clone https://github.com/YuanyuanMa03/academic-research-skills-marketplace.git

# Copy skills to Codex skills directory
mkdir -p ~/.codex/skills
cp -R academic-research-skills-marketplace/plugins/*/skills/* ~/.codex/skills/

# Or install specific skills
cp -R academic-research-skills-marketplace/plugins/cnki-search/skills/cnki-search ~/.codex/skills/
cp -R academic-research-skills-marketplace/plugins/gs-search/skills/gs-search ~/.codex/skills/
```

Skills load natively in Codex — just follow the instructions in SKILL.md.

| Skill tool | Codex equivalent |
|------------|------------------|
| `Read`, `Write`, `Edit` | Native file tools |
| `Bash` | Native shell tools |
| `Skill` tool | Skills load natively |

### Gemini CLI

```bash
# Clone the repo
git clone https://github.com/YuanyuanMa03/academic-research-skills-marketplace.git

# Copy skills to Gemini CLI skills directory
mkdir -p ~/.gemini/skills
cp -R academic-research-skills-marketplace/plugins/*/skills/* ~/.gemini/skills/

# Or install specific skills
cp -R academic-research-skills-marketplace/plugins/cnki-search/skills/cnki-search ~/.gemini/skills/
cp -R academic-research-skills-marketplace/plugins/gs-search/skills/gs-search ~/.gemini/skills/
```

Activate skills via `activate_skill` tool or by referencing them in your prompt.

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
# Clone the repo
git clone https://github.com/YuanyuanMa03/academic-research-skills-marketplace.git

# Copy skills to OpenClaw skills directory
mkdir -p ~/.openclaw/skills
cp -R academic-research-skills-marketplace/plugins/*/skills/* ~/.openclaw/skills/

# Or install specific skills
cp -R academic-research-skills-marketplace/plugins/cnki-search/skills/cnki-search ~/.openclaw/skills/
cp -R academic-research-skills-marketplace/plugins/gs-search/skills/gs-search ~/.openclaw/skills/
```

Skills are loaded as context files. Reference them in your agent configuration or include them in your prompt.

### Other Agents (Generic)

For any AI coding agent that supports skill/context files:

```bash
# Clone the repo
git clone https://github.com/YuanyuanMa03/academic-research-skills-marketplace.git

# The skills are plain Markdown files — copy them anywhere
# Each skill is self-contained in its directory
cp -R academic-research-skills-marketplace/plugins/cnki-search/skills/cnki-search /path/to/your/agent/skills/
```

**Skill structure (universal):**
```
<skill-name>/
├── SKILL.md              # Main instructions (always present)
├── references/           # Supporting guides (optional)
├── examples/             # Annotated examples (optional)
└── scripts/              # Helper scripts (optional)
```

**How to use in any agent:**
1. Copy the skill directory to your agent's skill/context location
2. Reference `SKILL.md` in your agent's system prompt or context
3. The agent follows the instructions in SKILL.md when the topic is triggered

### Don't Know Your Agent? Just Paste It

If you're not sure how your agent handles skills, the simplest approach: **paste the SKILL.md content directly into the chat.**

```bash
# 1. Clone the repo
git clone https://github.com/YuanyuanMa03/academic-research-skills-marketplace.git

# 2. Read the skill you want
cat academic-research-skills-marketplace/plugins/cnki-search/skills/cnki-search/SKILL.md

# 3. Copy the entire content and paste it into your agent's chat
# 4. Then ask your question — the agent will follow the instructions
```

**Example prompt to your agent:**
```
I'm going to paste a skill document. Please follow its instructions when I ask about academic search.

[PASTE SKILL.md CONTENT HERE]

Now search CNKI for papers on neural rendering.
```

This works with **any** LLM-based agent — ChatGPT, Gemini, Claude, Qwen, DeepSeek, etc. The SKILL.md is just a Markdown instruction file that any model can understand and follow.

## Usage

Once installed, skills activate automatically:

- "Search CNKI for papers on neural rendering"
- "Find citing papers on Google Scholar"
- "Download this ScienceDirect paper"
- "Help me write a Nature-style introduction"

## Adding Plugins

To contribute a new skill:

1. Create `plugins/your-skill-name/skills/your-skill-name/SKILL.md`
2. Add `plugins/your-skill-name/.claude-plugin/plugin.json`
3. Add entry to `.claude-plugin/marketplace.json`
4. Submit a pull request

## License

MIT
