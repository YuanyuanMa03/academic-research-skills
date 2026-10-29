# REFERENCE — 意图路由手册

"我想做 X，用哪个技能？"——本页回答这个问题。覆盖全部 16 个插件（v2.0.0 起：**一个平台一个技能**，平台技能内含全流程子文档）。维护者请读 [`PLAYBOOK.md`](PLAYBOOK.md)；改技能清单后本页必须同步（CI 强制每个插件名出现在本页）。

## 三步工作流

```
① 平台检索           ② 文献获取                ③ 写作辅助
cnki-search 等    →   scansci-pdf 插件      →   nature-* 系列
拿条目(题录/DOI)      下载 PDF / 引文 / Zotero     润色 / 审稿 / 配图 / 专利
```

**检索源选择**（按课题主题）：
- 生物医学主题 → `pm-search`（PubMed 精确 API）
- 材料 / 物理 / 工程主题 → `nature-academic-search`（CrossRef/PubMed/arXiv 并发）或 `scansci-pdf` 跨源检索（宽泛发现，需相关性过滤）
- 中文文献 → `cnki-search`；特定平台站内 → `sd-search` / `wos-search`

## 想做什么 → 用哪个技能

### ① 平台检索与导航（每平台一个技能，内含全流程）

| 想做什么 | 技能 | 内含子流程 | 前置 |
|---|---|---|---|
| CNKI：检索/高级检索/详情/解析/翻页/期刊检索/期刊目录/核心期刊导航 | `cnki-search` | 7 个 references 子文档 | 浏览器 MCP |
| ScienceDirect：检索/高级检索/详情/解析/翻页/期刊浏览 | `sd-search` | 5 个 references 子文档 | 浏览器 MCP |
| Web of Science：检索（内部 API+SID 回退）/详情/解析（含离线快照）/翻页/DOM 参考 | `wos-search` | 4 个 references 子文档 | 浏览器 MCP |
| PubMed：检索（API 优先双路径，`--year-from/--sort/--page` 覆盖高级检索与翻页） | `pm-search` | 单文件（独立脚本） | Python 脚本（默认）或浏览器 |
| 跨源学术检索（CrossRef/PubMed/arXiv，MCP server） | `nature-academic-search` | 自带 references | 自带 MCP（自动引导安装） |

进入平台技能后，SKILL.md 顶部的「场景路由」表会把具体动作路由到对应子流程文档。

### ② 文献获取（下载 / 引文 / Zotero）— 全部走 `scansci-pdf`

| 想做什么 | 用什么 |
|---|---|
| 下载单篇 PDF（DOI / arXiv / URL，多路由竞速） | `scansci-pdf` → `scansci_pdf_download` |
| 批量下载一份清单 | `scansci-pdf` → `scansci_pdf_parse_list` + `scansci_pdf_batch_download` |
| 跨源检索 + 找 OA 副本 | `scansci-pdf` → `scansci_pdf_search` / `prepare_queue(action="resolve_oa")` |
| 导出引文（BibTeX/RIS/EndNote） | `scansci-pdf` → `scansci_pdf_citation` |
| 推送 Zotero | `scansci-pdf` → `scansci_pdf_zotero_push` |
| 机构访问（WebVPN/CARSI/EZProxy/出版商 key） | `scansci-pdf` → `scansci_pdf_login` / `scansci_pdf_schools` |
| 环境自检 / 下载排障 | `scansci-pdf` → `scansci_pdf_diagnostics` |

前置：Python ≥ 3.11 + `scansci-pdf` 命令（SKILL.md 有安装引导）。强烈建议装浏览器后端 `pip install "scansci-pdf[camoufox]"`。灰色源仅在用户明确选择时启用。

### ③ Nature 写作辅助（纯提示词，任意 LLM 可用）

| 想做什么 | 技能 |
|---|---|
| 写引言 / 手稿 | `nature-writing` |
| 语言润色 | `nature-polishing` |
| 审稿人视角评审 | `nature-reviewer` |
| 审稿意见回复信 | `nature-response` |
| 论文精读 | `nature-reader` |
| 图表制作 | `nature-figure` |
| 数据呈现 | `nature-data` |
| 论文转 PPT | `nature-paper2ppt` |
| 论文转中文发明专利草案 | `nature-paper-to-patent` |
| 引文检查 | `nature-citation` |

## 老用户迁移表

**v1.2.0（2026-10-28）**：`*-download`/`*-export`/`zotero-csl` → `scansci-pdf`。

**v2.0.0（2026-10-29）**：一个平台一个技能——

| 已移除 | 替代 |
|---|---|
| `gs-*` 4 个（平台失效） | `scansci-pdf` 跨源检索 / `pm-search` |
| `ieee-*` 7 个（平台失效） | `scansci-pdf` 跨源检索（IEEE 官方 API 路线见 PLAYBOOK 待办） |
| `pm-advanced-search` / `pm-navigate-pages` | `pm-search` 的 `--year-from --year-to --sort --page` 参数 |
| `pm-paper-detail` / `pm-fulltext` | `pm-search` 单篇查询 / `scansci-pdf` 下载（PMC 渠道） |
| `cnki-advanced-search` 等 CNKI 7 个 | `cnki-search` 的 references 子流程 |
| `sd-advanced-search` 等 SD 5 个 | `sd-search` 的 references 子流程 |
| `wos-paper-detail` / `wos-parse-results` / `wos-navigate-pages` / `wos-dom` | `wos-search` 的 references 子流程 |

## 症状 → 首个动作

| 症状 | 首个动作 |
|---|---|
| 浏览器技能全部不动 | 检查 chrome-devtools MCP 是否启动（插件自带 .mcp.json 配置） |
| CNKI 出验证码 | cnki-search SKILL.md 的 Captcha detection 段（只认可见验证码） |
| WoS 报 `no_session` | wos-search 自动回退 DOM 导航；仍失败重新进站拿 SID |
| PubMed 429 | 脚本自动重试；加 `--mailto` 进 polite pool |
| 工具列表没有 `scansci_pdf_*` | scansci-pdf SKILL.md 安装引导（Python ≥ 3.11 + pip install）；或 CLI 兜底 |
| 下载日志 "browser not available" | 装 `pip install "scansci-pdf[camoufox]"`——不装则只覆盖 OA 仓库直链型文章 |
| 下载报 `config_needed` / 要邮箱 | 问用户真实邮箱（Unpaywall 必须），配置后重试 |
| 下载的文件不在指定目录 | scansci-pdf 缓存命中返回旧文件；清缓存重下（见其 SKILL.md 排障表） |
| 机构登录后仍无权限 | 读出版商错误页上的出口 IP，核对是否在校园网段（详见 scansci-pdf SKILL 两条事实） |
| Zotero 推送失败 | `scansci_pdf_zotero_push` 走 Zotero Web API——需要 zotero.org 的 API key（非本地 Zotero 程序）；报 "API key not configured" 即此原因 |
