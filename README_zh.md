# 学术研究技能

[English](./README.md)

Claude Code 插件市场，提供学术研究工作流相关技能。

## 支持平台

| 平台 | 前缀 | 技能 |
|------|------|------|
| 知网 (CNKI) | `cnki-*` | 搜索、下载、导出、期刊浏览、论文详情 |
| 谷歌学术 (Google Scholar) | `gs-*` | 搜索、高级搜索、引用追踪、全文获取、导出 |
| ScienceDirect | `sd-*` | 搜索、下载、导出、期刊浏览、论文详情 |
| Web of Science | `wos-*` | 搜索、下载、导出、论文详情 |
| Nature | `nature-*` | 学术搜索、写作、润色、图表、阅读 |

## 安装方式

### Claude Code（推荐）

```bash
# 添加市场
/plugin marketplace add YuanyuanMa03/academic-research-skills

# 安装全部技能
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
/plugin install nature-academic-search@academic-research-skills
/plugin install nature-citation@academic-research-skills
/plugin install nature-crop-simple@academic-research-skills
/plugin install nature-data@academic-research-skills
/plugin install nature-figure@academic-research-skills
/plugin install nature-paper2ppt@academic-research-skills
/plugin install nature-polishing@academic-research-skills
/plugin install nature-reader@academic-research-skills
/plugin install nature-response@academic-research-skills
/plugin install nature-writing@academic-research-skills
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
```

### Copilot CLI

```bash
git clone https://github.com/YuanyuanMa03/academic-research-skills.git
mkdir -p ~/.copilot/skills
cp -R academic-research-skills/plugins/*/skills/* ~/.copilot/skills/
```

| 技能工具 | Copilot CLI 等价工具 |
|----------|---------------------|
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

或安装特定技能：

```bash
# 知网 (CNKI)
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

# 谷歌学术 (Google Scholar)
cp -R academic-research-skills/plugins/gs-advanced-search/skills/gs-advanced-search ~/.codex/skills/
cp -R academic-research-skills/plugins/gs-cited-by/skills/gs-cited-by ~/.codex/skills/
cp -R academic-research-skills/plugins/gs-export/skills/gs-export ~/.codex/skills/
cp -R academic-research-skills/plugins/gs-fulltext/skills/gs-fulltext ~/.codex/skills/
cp -R academic-research-skills/plugins/gs-navigate-pages/skills/gs-navigate-pages ~/.codex/skills/
cp -R academic-research-skills/plugins/gs-search/skills/gs-search ~/.codex/skills/

# Nature
cp -R academic-research-skills/plugins/nature-academic-search/skills/nature-academic-search ~/.codex/skills/
cp -R academic-research-skills/plugins/nature-citation/skills/nature-citation ~/.codex/skills/
cp -R academic-research-skills/plugins/nature-crop-simple/skills/nature-crop-simple ~/.codex/skills/
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

技能在 Codex 中原生加载 — 只需按照 SKILL.md 中的说明操作。

| 技能工具 | Codex 等价工具 |
|----------|---------------|
| `Read`, `Write`, `Edit` | 原生文件工具 |
| `Bash` | 原生 Shell 工具 |
| `Skill` 工具 | 技能原生加载 |

### Gemini CLI

```bash
git clone https://github.com/YuanyuanMa03/academic-research-skills.git
mkdir -p ~/.gemini/skills
cp -R academic-research-skills/plugins/*/skills/* ~/.gemini/skills/
```

| 技能工具 | Gemini CLI 等价工具 |
|----------|---------------------|
| `Read` | `read_file` |
| `Write` | `write_file` |
| `Edit` | `replace` |
| `Bash` | `run_shell_command` |
| `Grep` | `grep_search` |
| `Skill` 工具 | `activate_skill` |
| `WebSearch` | `google_web_search` |
| `WebFetch` | `web_fetch` |

### OpenClaw

```bash
git clone https://github.com/YuanyuanMa03/academic-research-skills.git
mkdir -p ~/.openclaw/skills
cp -R academic-research-skills/plugins/*/skills/* ~/.openclaw/skills/
```

### 其他 Agent（通用）

```bash
git clone https://github.com/YuanyuanMa03/academic-research-skills.git
cp -R academic-research-skills/plugins/cnki-search/skills/cnki-search /path/to/your/agent/skills/
```

**技能结构（通用）：**
```
<技能名>/
├── SKILL.md              # 主要说明
├── references/           # 辅助指南（可选）
├── examples/             # 标注示例（可选）
└── scripts/              # 辅助脚本（可选）
```

### 不知道怎么用？直接粘贴给 Agent

把 SKILL.md 内容直接粘贴到任何 LLM 聊天中：

```bash
cat academic-research-skills/plugins/cnki-search/skills/cnki-search/SKILL.md
# 复制并粘贴到 ChatGPT、Gemini、Claude、通义千问、DeepSeek 等
```

## 使用方式

- "帮我在知网上搜索关于 neural rendering 的论文"
- "在谷歌学术上找引用这篇论文的文献"
- "下载这篇 ScienceDirect 的论文"
- "帮我用 Nature 风格写一个 Introduction"

## 添加插件

1. 创建 `plugins/your-skill-name/skills/your-skill-name/SKILL.md`
2. 添加 `plugins/your-skill-name/.claude-plugin/plugin.json`
3. 在 `.claude-plugin/marketplace.json` 中添加条目
4. 提交 Pull Request

## 许可证

MIT
