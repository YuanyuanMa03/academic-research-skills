# 学术研究技能市场

Claude Code 插件市场，提供学术研究工作流相关技能。

[English](./README.md)

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
/plugin marketplace add YuanyuanMa03/academic-research-skills-marketplace

# 安装技能
/plugin install cnki-search@academic-research-skills-marketplace
/plugin install gs-search@academic-research-skills-marketplace
/plugin install nature-writing@academic-research-skills-marketplace
```

### Copilot CLI

```bash
# 克隆仓库
git clone https://github.com/YuanyuanMa03/academic-research-skills-marketplace.git

# 复制技能到 Copilot CLI 技能目录
mkdir -p ~/.copilot/skills
cp -R academic-research-skills-marketplace/plugins/*/skills/* ~/.copilot/skills/

# 或安装特定技能
cp -R academic-research-skills-marketplace/plugins/cnki-search/skills/cnki-search ~/.copilot/skills/
cp -R academic-research-skills-marketplace/plugins/gs-search/skills/gs-search ~/.copilot/skills/
```

技能通过 `/skill` 命令激活，或在你询问研究任务时自动激活。

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
# 克隆仓库
git clone https://github.com/YuanyuanMa03/academic-research-skills-marketplace.git

# 复制技能到 Codex 技能目录
mkdir -p ~/.codex/skills
cp -R academic-research-skills-marketplace/plugins/*/skills/* ~/.codex/skills/

# 或安装特定技能
cp -R academic-research-skills-marketplace/plugins/cnki-search/skills/cnki-search ~/.codex/skills/
cp -R academic-research-skills-marketplace/plugins/gs-search/skills/gs-search ~/.codex/skills/
```

技能在 Codex 中原生加载 — 只需按照 SKILL.md 中的说明操作。

| 技能工具 | Codex 等价工具 |
|----------|---------------|
| `Read`, `Write`, `Edit` | 原生文件工具 |
| `Bash` | 原生 Shell 工具 |
| `Skill` 工具 | 技能原生加载 |

### Gemini CLI

```bash
# 克隆仓库
git clone https://github.com/YuanyuanMa03/academic-research-skills-marketplace.git

# 复制技能到 Gemini CLI 技能目录
mkdir -p ~/.gemini/skills
cp -R academic-research-skills-marketplace/plugins/*/skills/* ~/.gemini/skills/

# 或安装特定技能
cp -R academic-research-skills-marketplace/plugins/cnki-search/skills/cnki-search ~/.gemini/skills/
cp -R academic-research-skills-marketplace/plugins/gs-search/skills/gs-search ~/.gemini/skills/
```

通过 `activate_skill` 工具激活技能，或在提示词中引用它们。

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
# 克隆仓库
git clone https://github.com/YuanyuanMa03/academic-research-skills-marketplace.git

# 复制技能到 OpenClaw 技能目录
mkdir -p ~/.openclaw/skills
cp -R academic-research-skills-marketplace/plugins/*/skills/* ~/.openclaw/skills/

# 或安装特定技能
cp -R academic-research-skills-marketplace/plugins/cnki-search/skills/cnki-search ~/.openclaw/skills/
cp -R academic-research-skills-marketplace/plugins/gs-search/skills/gs-search ~/.openclaw/skills/
```

技能作为上下文文件加载。在你的 agent 配置中引用它们，或直接包含在提示词中。

### 其他 Agent（通用）

对于任何支持技能/上下文文件的 AI 编程 agent：

```bash
# 克隆仓库
git clone https://github.com/YuanyuanMa03/academic-research-skills-marketplace.git

# 技能是纯 Markdown 文件 — 可以复制到任何位置
# 每个技能都是自包含的目录
cp -R academic-research-skills-marketplace/plugins/cnki-search/skills/cnki-search /path/to/your/agent/skills/
```

**技能结构（通用）：**
```
<技能名>/
├── SKILL.md              # 主要说明（始终存在）
├── references/           # 辅助指南（可选）
├── examples/             # 标注示例（可选）
└── scripts/              # 辅助脚本（可选）
```

**在任何 agent 中使用：**
1. 将技能目录复制到你的 agent 的技能/上下文位置
2. 在你的 agent 系统提示词或上下文中引用 `SKILL.md`
3. 当触发相关主题时，agent 会按照 SKILL.md 中的说明操作

### 不知道怎么用？直接粘贴给 Agent

如果你不确定你的 agent 如何处理技能，最简单的方法：**直接把 SKILL.md 内容粘贴到聊天中。**

```bash
# 1. 克隆仓库
git clone https://github.com/YuanyuanMa03/academic-research-skills-marketplace.git

# 2. 读取你想要的技能
cat academic-research-skills-marketplace/plugins/cnki-search/skills/cnki-search/SKILL.md

# 3. 复制全部内容，粘贴到你的 agent 聊天中
# 4. 然后提问 — agent 会按照说明操作
```

**给你的 agent 的示例提示词：**
```
我要粘贴一个技能文档。当我在2026年6月6日询问学术搜索相关问题时，请按照它的说明操作。

[在这里粘贴 SKILL.md 的内容]

现在帮我在知网上搜索关于 neural rendering 的论文。
```

这种方法适用于**任何**基于 LLM 的 agent — ChatGPT、Gemini、Claude、通义千问、DeepSeek 等。SKILL.md 就是一个 Markdown 说明文件，任何模型都能理解并遵循。

## 使用方式

安装后，技能会自动激活：

- "帮我在知网上搜索关于 neural rendering 的论文"
- "在谷歌学术上找引用这篇论文的文献"
- "下载这篇 ScienceDirect 的论文"
- "帮我用 Nature 风格写一个 Introduction"

## 添加插件

贡献新技能：

1. 创建 `plugins/your-skill-name/skills/your-skill-name/SKILL.md`
2. 添加 `plugins/your-skill-name/.claude-plugin/plugin.json`
3. 在 `.claude-plugin/marketplace.json` 中添加条目
4. 提交 Pull Request

## 许可证

MIT
