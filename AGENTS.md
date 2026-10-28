# AGENTS.md

本文件是所有 Agent（Claude Code、Codex、ZCode 等）在本仓库工作时的入口指南。修改任何浏览器自动化 / 反爬相关技能之前，先读 [`docs/PLAYBOOK.md`](docs/PLAYBOOK.md)。

## 这个仓库是什么

academic-research-skills 是一个面向 AI 助手的学术研究技能市场（plugin marketplace），当前 47 个插件覆盖三类能力：

1. **平台站内检索与导航**（46 个）：CNKI、Google Scholar、ScienceDirect、Web of Science、PubMed、IEEE Xplore 的搜索、详情、翻页、期刊浏览，以及 Nature 写作辅助。
2. **文献获取**（1 个）：`scansci-pdf` 桥接插件——接入开源 [scansci-pdf](https://github.com/Rimagination/scansci-pdf) MCP server，负责 PDF 下载（多路由竞速）、批量队列、引文导出、Zotero 推送、机构通道、环境诊断。它取代了已删除的 `*-download` / `*-export` / `zotero-csl` 技能（决策记录见 PLAYBOOK）。
3. **典型工作流**：平台站内检索（如 `cnki-search`）拿条目 → `scansci-pdf` 完成下载 / 引文 / Zotero 推送 → `nature-*` 辅助写作。

## 目录结构

```
academic-research-skills/
├── plugins/<name>/               # 每插件一个目录，独立安装
│   ├── .claude-plugin/plugin.json   # Claude manifest（必需）
│   ├── .codex-plugin/plugin.json    # Codex manifest（必需）
│   ├── .mcp.json                    # MCP 配置（浏览器技能 / scansci-pdf 必需）
│   └── skills/<name>/SKILL.md       # 技能定义
├── .claude-plugin/marketplace.json  # Claude 市场清单（47 条）
├── .agents/plugins/marketplace.json # Codex 市场清单（47 条）
├── scripts/                      # 校验工具（见下）
└── docs/
    ├── PLAYBOOK.md               # 维护手册（铁律 / 失败签名 / 决策账本）
    └── REFERENCE.md              # 意图路由手册（想做什么 → 用哪个技能）
```

## 开发命令

```bash
python scripts/validate_skills.py               # SKILL.md 校验
python scripts/validate_plugin_json.py          # plugin.json 校验
python scripts/check_shared_assets.py           # .mcp.json 模板漂移检查
python scripts/check_marketplace_consistency.py # 双市场 + 目录 + REFERENCE 一致性
ruff check plugins/ scripts/ && ruff format --check plugins/ scripts/
```

提交前全部通过；CI（lint.yml / test.yml）会重复这些检查。`pyproject.toml` 只含 ruff 配置。

## 宿主适配

| 宿主 | 安装方式 | 清单 |
|---|---|---|
| Claude Code | `/plugin marketplace add YuanyuanMa03/academic-research-skills` 后逐个安装 | `.claude-plugin/marketplace.json` |
| Codex | `codex plugin marketplace add YuanyuanMa03/academic-research-skills` | `.agents/plugins/marketplace.json` |
| 其他 Agent | 手动复制 `plugins/<name>/skills/<name>/` 到技能目录 | — |

## Guardrails（改动前必读）

1. **双市场同步**：新增/删除/改名插件必须同时更新 `.claude-plugin/marketplace.json` 与 `.agents/plugins/marketplace.json`，并补齐两个 `plugin.json`。历史上 Codex 市场曾静默落后两个插件——`scripts/check_marketplace_consistency.py` 就是为此而设，不要绕过它。
2. **独立安装约束**：每个插件目录必须自包含（用户可能只装一个）。不要引入 `shared/` 公共目录——试过一次已被回退（commit c0b84e6）。跨插件重复资产用 `scripts/check_shared_assets.py` 的 SHA 清单守模板，不允许静默漂移。
3. **浏览器/反爬技能改动前先读 [`docs/PLAYBOOK.md`](docs/PLAYBOOK.md)**：里面有平台失败签名表（什么响应算墙、算死链）、当前平台状态和铁律。
4. **新检索技能遵循 pm-search 双路径范式**：Path 1 独立 Python 脚本（API 优先，工具调用预算 1）+ Path 2 浏览器兜底，详见 PLAYBOOK。
5. **scansci-pdf 是外部 PyPI 包**：本仓库只做 MCP 配置 + 技能包装，不 vendoring 其代码。灰色源（Sci-Hub/LibGen）必须在用户明确选择后才可用，`legal_only` 策略不可被调度扩大；API key、cookie、代理凭据视为机密。
6. **REFERENCE.md 覆盖检查**：每个插件名必须出现在 `docs/REFERENCE.md` 中（一致性脚本强制），新增技能时同步补路由表。
7. **禁止硬编码绝对路径**（`/Users/`、`/home/`、盘符路径），CI 会拒绝。
