# Academic Research Skills Marketplace

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

```bash
# Add marketplace
/plugin marketplace add YuanyuanMa03/academic-research-skills-marketplace

# Install all CNKI skills
/plugin install cnki-search@academic-research-skills-marketplace
/plugin install cnki-download@academic-research-skills-marketplace
/plugin install cnki-export@academic-research-skills-marketplace

# Install Google Scholar skills
/plugin install gs-search@academic-research-skills-marketplace
/plugin install gs-advanced-search@academic-research-skills-marketplace

# Install Nature writing skills
/plugin install nature-writing@academic-research-skills-marketplace
/plugin install nature-polishing@academic-research-skills-marketplace
```

## Usage

Once installed, skills activate automatically:

- "Search CNKI for papers on neural rendering"
- "Find citing papers on Google Scholar"
- "Download this ScienceDirect paper"
- "Help me write a Nature-style introduction"

## License

MIT
