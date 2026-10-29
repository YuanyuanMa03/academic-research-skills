# REFERENCE — 意图路由手册

"我想做 X，用哪个技能？"——本页回答这个问题。覆盖全部 47 个插件。维护者请读 [`PLAYBOOK.md`](PLAYBOOK.md)；改技能清单后本页必须同步（CI 强制每个插件名出现在本页）。

## 三步工作流

```
① 站内检索           ② 文献获取                ③ 写作辅助
cnki-search 等   →   scansci-pdf 插件      →   nature-* 系列
拿条目(题录/DOI)      下载 PDF / 引文 / Zotero     润色 / 审稿 / 配图 / 专利
```

**检索源选择**（按课题主题）：
- 生物医学主题 → `pm-search`（PubMed 精确 API）
- 材料 / 物理 / 工程主题 → `nature-academic-search`（CrossRef/PubMed/arXiv 并发）或 `scansci-pdf` 跨源检索（宽泛发现，需相关性过滤；PubMed 对此类主题覆盖有限）
- 中文文献 / 特定平台站内 → 对应 `cnki-*` / `sd-*` 等平台技能

## 想做什么 → 用哪个技能

### ① 平台站内检索与导航

| 想做什么 | 技能 | 前置 |
|---|---|---|
| CNKI 关键词检索 | `cnki-search` | 浏览器 MCP |
| CNKI 字段过滤高级检索（作者/期刊/日期/核心库） | `cnki-advanced-search` | 浏览器 MCP |
| CNKI 论文详情页解析 | `cnki-paper-detail` | 浏览器 MCP |
| CNKI 结果页结构化解析 | `cnki-parse-results` | 浏览器 MCP |
| CNKI 翻页 | `cnki-navigate-pages` | 浏览器 MCP |
| CNKI 期刊检索 | `cnki-journal-search` | 浏览器 MCP |
| CNKI 期刊目录页浏览 | `cnki-journal-toc` | 浏览器 MCP |
| CNKI 期刊导航体系 | `cnki-journal-index` | 浏览器 MCP |
| Google Scholar 关键词检索 | `gs-search` | 浏览器 MCP（状态见 PLAYBOOK） |
| GS 高级检索 | `gs-advanced-search` | 浏览器 MCP |
| GS 找引用某文的文章 | `gs-cited-by` | 浏览器 MCP |
| GS 翻页 | `gs-navigate-pages` | 浏览器 MCP |
| ScienceDirect 检索 / 高级检索 | `sd-search` / `sd-advanced-search` | 浏览器 MCP |
| SD 结果解析 / 详情 / 翻页 | `sd-parse-results` / `sd-paper-detail` / `sd-navigate-pages` | 浏览器 MCP |
| SD 期刊浏览 | `sd-journal-browse` | 浏览器 MCP |
| Web of Science 检索（内部 API，带 SID 回退） | `wos-search` | 浏览器 MCP |
| WoS DOM 结构参考 | `wos-dom` | 无 |
| WoS 结果解析（含离线快照模式） | `wos-parse-results` | 无（在线模式需浏览器） |
| WoS 论文详情 / 翻页 | `wos-paper-detail` / `wos-navigate-pages` | 浏览器 MCP |
| IEEE 检索 / 高级检索 | `ieee-search` / `ieee-advanced-search` | 浏览器 MCP（状态见 PLAYBOOK） |
| IEEE 标准检索 | `ieee-standards-search` | 浏览器 MCP |
| IEEE 结果解析 / 详情 / 翻页 | `ieee-parse-results` / `ieee-paper-detail` / `ieee-navigate-pages` | 浏览器 MCP |
| IEEE 期刊浏览 | `ieee-journal-browse` | 浏览器 MCP |
| PubMed 关键词检索（API 优先双路径） | `pm-search` | Python 脚本（默认）或浏览器 |
| PubMed 高级检索 | `pm-advanced-search` | 浏览器 MCP |
| PubMed 详情 / 翻页 | `pm-paper-detail` / `pm-navigate-pages` | 浏览器 MCP |
| PubMed 全文获取（PMC API） | `pm-fulltext` | 网络 |
| 跨源学术检索（MCP server：CrossRef/PubMed/arXiv…） | `nature-academic-search` | 自带 MCP（自动引导安装） |

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

前置：Python ≥ 3.11 + `scansci-pdf` 命令（SKILL.md 有安装引导，装完插件即引导）。灰色源仅在用户明确选择时启用。

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

## 老用户迁移表（已删除技能 → 替代）

| 已删除（2026-10-28） | 替代 |
|---|---|
| `cnki-download` / `gs-fulltext` / `ieee-download` / `sd-download` / `wos-download` | `scansci-pdf` → `scansci_pdf_download` |
| `cnki-export` / `gs-export` / `ieee-export` / `pm-export` / `sd-export` / `wos-export` | `scansci-pdf` → `scansci_pdf_citation` + `scansci_pdf_zotero_push` |
| `zotero-csl` | `scansci-pdf` → `scansci_pdf_citation`（多格式） |

## 症状 → 首个动作

| 症状 | 首个动作 |
|---|---|
| 浏览器技能全部不动 | 检查 chrome-devtools MCP 是否启动（插件自带 .mcp.json 配置） |
| GS / IEEE 检索超时 | 见 PLAYBOOK 平台状态表——用 PubMed/CNKI 替代检索，或 `scansci-pdf` 跨源检索 |
| WoS 报 `no_session` | wos-search 自动回退 DOM 导航；仍失败重新进站拿 SID |
| PubMed 429 | 脚本自动重试；加 `--mailto` 进 polite pool |
| 工具列表没有 `scansci_pdf_*` | scansci-pdf SKILL.md 安装引导（Python ≥ 3.11 + pip install）；或 CLI 兜底 |
| 下载日志 "browser not available" | 装 `pip install "scansci-pdf[camoufox]"`——不装则只覆盖 OA 仓库直链型文章 |
| 下载报 `config_needed` / 要邮箱 | 问用户真实邮箱（Unpaywall 必须），配置后重试 |
| 下载的文件不在指定目录 | scansci-pdf 缓存命中返回旧文件；清缓存重下（见其 SKILL.md 排障表） |
| 机构登录后仍无权限 | 读出版商错误页上的出口 IP，核对是否在校园网段（详见 scansci-pdf SKILL 两条事实） |
| Zotero 推送失败 | 本地 Zotero 需在运行；重试用 `scansci_pdf_zotero_push` |
