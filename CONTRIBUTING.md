# Contributing to academic-research-skills

Thank you for your interest in contributing! This guide covers how to create new skills and the quality standards we follow.

## Repository Structure

```
academic-research-skills/
├── plugins/                 # One directory per plugin
│   └── {plugin-name}/
│       ├── .claude-plugin/
│       │   └── plugin.json  # Plugin metadata
│       └── skills/
│           └── {skill-name}/
│               ├── SKILL.md     # Skill instructions (required)
│               ├── scripts/     # Executable scripts (optional)
│               └── references/  # Reference documents (optional)
├── scripts/                 # Repository-level validation tools
└── docs/                    # Documentation
```

## Creating a New Skill

### 1. Create the plugin directory

```bash
mkdir -p plugins/{series}-{action}/.claude-plugin
mkdir -p plugins/{series}-{action}/skills/{series}-{action}
```

### 2. Create plugin.json

```json
{
  "name": "{series}-{action}",
  "description": "Brief description of what this skill does.",
  "version": "1.0.0",
  "author": { "name": "YourGitHubUsername" },
  "license": "MIT",
  "keywords": ["academic", "research", "{series}"]
}
```

### 3. Write SKILL.md

Follow the SKILL.md Specification v1. Required structure:

```yaml
---
name: {series}-{action}
description: |
  English description.
  中文描述。
argument-hint: "<query>"
version: "1.0.0"
requires:
  - chrome-devtools-mcp
tags: [academic, research, {series}]
---
```

Required sections: Overview, Prerequisites, Workflow (numbered steps with executable code), Output Contract, Error Handling.

## Quality Standards

### SKILL.md Quality Checklist

- [ ] YAML frontmatter has all required fields (name, description, argument-hint)
- [ ] All code blocks are executable (tested manually)
- [ ] Output Contract section with standard format
- [ ] Error Handling section with recovery strategies
- [ ] Tool call budget documented
- [ ] No hardcoded absolute paths

### Python Script Quality Checklist

- [ ] Type hints on all function signatures
- [ ] Docstrings on all public functions
- [ ] Use `logging` module instead of `print()`
- [ ] Use `argparse` for CLI argument parsing
- [ ] Error handling with meaningful error messages
- [ ] UTF-8 encoding safety

### Testing

Add eval fixtures in `evals/evals.json`:

```json
{
  "skill_name": "{series}-{action}",
  "evals": [
    {
      "id": 1,
      "prompt": "Test prompt that exercises the skill",
      "expected_output": "Description of expected behavior"
    }
  ]
}
```

## Validation

Run all validation checks before submitting:

```bash
python scripts/validate_skills.py
python scripts/validate_plugin_json.py
```

## Naming Convention

Plugin names follow the pattern: `{platform}-{action}`

| Platform prefix | Full name |
|----------------|-----------|
| `cnki-` | China National Knowledge Infrastructure |
| `gs-` | Google Scholar |
| `sd-` | ScienceDirect |
| `wos-` | Web of Science |
| `pm-` | PubMed |
| `ieee-` | IEEE Xplore |
| `nature-` | Nature / Springer Nature |

| Action suffix | Description |
|--------------|-------------|
| `-search` | Basic keyword search |
| `-advanced-search` | Multi-field / Boolean search |
| `-paper-detail` | Full paper metadata extraction |
| `-parse-results` | Parse search results page |
| `-navigate-pages` | Paginate through results |
| `-export` | Export citations (Zotero / RIS / BibTeX) |
| `-download` | Download full-text PDF |

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-skill-name`
2. Run validation: `python scripts/validate_skills.py`
3. Ensure CI passes (lint + test workflows)
4. Submit PR with description of what the skill does
