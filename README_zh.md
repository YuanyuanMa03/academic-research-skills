# 学术研究技能

[English](./README.md)

Claude Code 插件市场，提供学术研究工作流相关技能。

## 快速开始（任意 Agent）

直接发送给你的 agent：

```
从这个仓库安装所有学术研究技能：
https://github.com/YuanyuanMa03/academic-research-skills
```

适用于 Claude Code、Copilot CLI、Codex、Gemini CLI、ChatGPT、通义千问、DeepSeek，或任何能读取 GitHub 仓库的 LLM agent。

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

### Codex（推荐使用 Marketplace）

Codex 通过 plugin 分发可复用 skills。本仓库已提供 Codex marketplace
`.agents/plugins/marketplace.json`，并为每个 skill 提供
`plugins/<name>/.codex-plugin/plugin.json`。

先把本仓库加入 Codex marketplace，然后在插件目录里安装需要的技能：

```bash
codex plugin marketplace add YuanyuanMa03/academic-research-skills
codex
/plugins
```

在插件目录中选择 **Academic Research Skills**，打开需要的插件并选择
**Install plugin**。安装完成后新开一个 Codex 线程使用。你可以用 `@`
显式调用某个插件或 skill，也可以直接描述任务，让 Codex 根据描述自动选择。

常用 marketplace 管理命令：

```bash
codex plugin marketplace list
codex plugin marketplace upgrade academic-research-skills
codex plugin marketplace remove academic-research-skills
```

#### 手动安装 fallback

本仓库是 multi-skill collection，不要把仓库根目录当作单个 Codex skill
安装；应安装 `plugins/*/skills/*` 下的实际 skill 目录。

```bash
git clone https://github.com/YuanyuanMa03/academic-research-skills.git
mkdir -p ~/.codex/skills
cp -R academic-research-skills/plugins/*/skills/* ~/.codex/skills/
```

如果使用 Codex 的 GitHub skill installer，也要传入嵌套 skill 路径，而不是仓库根目录：

```bash
python3 /path/to/install-skill-from-github.py \
  --repo YuanyuanMa03/academic-research-skills \
  --path plugins/nature-academic-search/skills/nature-academic-search
```

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
