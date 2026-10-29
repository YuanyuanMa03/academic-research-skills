---
name: scansci-pdf
description: 学术论文获取全家桶，基于 scansci-pdf MCP server。多路由下载 PDF（开放获取 → 出版商 API → 机构通道并行竞速）、批量清单下载、引文导出（BibTeX/RIS/EndNote）、推送 Zotero、机构登录（WebVPN/CARSI/EZProxy）、环境诊断排障。当用户要下载论文（单篇或批量）、导出引文、推送 Zotero、配置机构访问，或下载遇到 Cloudflare/验证页/代理问题时使用。用户仅讨论 PDF 工具对比选型而无需获取文献时不要使用。
argument-hint: "<DOI | arXiv ID | 论文标题 | 清单文件路径>"
version: 1.0.0
---

# ScanSci PDF — 论文获取 / 引文 / Zotero

本技能桥接开源项目 [scansci-pdf](https://github.com/Rimagination/scansci-pdf)（MIT）的 MCP server：20+ 数据源并行竞速，任一成功立即返回；每篇结果都报告实际来源。它取代了本仓库早期的 `*-download` / `*-export` / `zotero-csl` 技能——平台站内检索仍用 `cnki-search`、`pm-search` 等技能，拿到条目后交给本技能完成下载、引文与推送。

## 前置条件 (Prerequisites)

MCP server 需要 Python ≥ 3.11 和 `scansci-pdf` 命令。安装本插件后若工具列表中没有 `scansci_pdf_*` 工具，按以下步骤引导（steps 按顺序执行，遇到问题转排障表）：

```bash
# 1. 检查 Python 版本（需要 >= 3.11）
python3 --version

# 2a. 推荐：独立 venv 安装（不污染用户环境）
python3 -m venv ~/.scansci-pdf/venv && ~/.scansci-pdf/venv/bin/pip install scansci-pdf

# 2b. 或一行式（需要 uv）
uvx --from scansci-pdf scansci-pdf check

# 3. 环境自检，按 readiness 分级处理
scansci-pdf check
```

- `ready`：全部就绪，直接走工作流。
- `partial`：核心可用、可选组件缺失（浏览器后端、Tor 等），按提示安装，不阻塞下载。
- `limited`：缺关键依赖，先完成安装再继续。

**可选浏览器后端强烈建议安装**：没有它，下载只覆盖"OA 仓库直链"型文章，出版商官网 OA 页面（Wiley/RSC 等）与机构登录都不可用。无机构通道时执行 `pip install "scansci-pdf[camoufox]"`（或 `scansci-pdf[patchright]`）可显著扩大可下载范围；机构登录/Cloudflare 场景必须有它。

安装后需重启宿主（或重载插件）让 MCP server 生效。CLI（`scansci-pdf get/search/batch/...`）与 MCP 工具能力等价，MCP 不可用时用 CLI 兜底。**注意**：CLI 模式没有引文格式化命令（`citation` 仅 MCP 提供）——CLI 兜底时由你（agent）用检索结果的 title/authors/year/doi 字段直接构造 BibTeX，或提示用户启用 MCP server。

## 工作流 (Workflow)

### 快速工作流（三条技能串起完整课题）

```
① 站内/平台检索（cnki-search、pm-search 等）拿条目（标题/作者/DOI）
② 本技能：get 下载 PDF（--md 转 Markdown 供精读）→ 引文/Zotero
③ nature-* 系列：精读笔记 → 综述 → 开题 → 文章撰写
```

### 场景 → 工具路由

| 用户想做什么 | 用什么 |
|---|---|
| 下载单篇（DOI / arXiv / 文章页 URL） | `scansci_pdf_download`（可带 `si=true` 拉补充材料、`md=true` 转 Markdown） |
| 批量下载一份清单（xlsx/csv/txt/bib/APA） | `scansci_pdf_parse_list` → `scansci_pdf_batch_download` |
| 验证 / 嗅探一批标识符 | `scansci_pdf_prepare_queue(action="verify")`；找 OA 副本用 `action="resolve_oa"` |
| 跨源检索文献（含作者、被引过滤） | `scansci_pdf_search`（可选 `scansci_pdf_sciverse` 语义检索） |
| 导出引文 | `scansci_pdf_citation`（bibtex / ris / endnote） |
| 推送到 Zotero | `scansci_pdf_zotero_push`（走 **Zotero Web API，需要 Zotero API key**——在 zotero.org 设置页创建；不是本地 Zotero 程序，也不是旧的 Connector 端口） |
| 机构登录 / 渠道状态 | `scansci_pdf_login`、`scansci_pdf_channel_status`、`scansci_pdf_schools` |
| 环境或下载排障 | `scansci_pdf_diagnostics(check=health|network|sources|setup)` |
| 模糊引用（"Wang 2023 CRISPR 那篇"） | 先 `scansci_pdf_search` 拿候选让用户确认，不要硬猜 DOI |

**检索源选择提示**：`scansci_pdf_search` 是宽泛发现引擎（13 源），长复合查询的相关性排序偏宽——主题精确检索优先用平台技能（生物医学 → `pm-search`，其走 PubMed 精确 API；站内 → `cnki-search` 等），本技能检索用于跨源发现与兜底，结果需做相关性过滤。

### 策略选择（必读）

用户指定了来源 = 只按用户的来，调度不得扩大授权范围：

| 用户说的是 | 策略 |
|---|---|
| "从 Sci-Hub 下载" | `scihub_only` |
| "优先 scihub" | `scihub_first`（OA 仍竞速，更快时最终来源可能是 OA） |
| "只要免费合法的" | `legal_only`（排除 Sci-Hub / LibGen） |
| 未指定 | `fastest`（默认，全源并行竞速） |

### 机构通道两条事实（失败大多源于此）

1. **登录必须用工具自己打开的浏览器**：`scansci_pdf_login` 打开的可见浏览器窗口才是 cookie 抓取上下文；用户自己浏览器里的登录态、无头模式，都拿不到。
2. **出口 IP 决定机构权限**：出版商按请求源 IP 判权益。系统级代理会把出口 IP 移出校园网段，静默作废 IP 认证。出版商报"无权限"时，先读错误页上它看到的 IP，再下"学校没订阅"的结论。工具只认 `network_proxy` / `SCANSCI_PDF_PROXY`，忽略 `HTTP_PROXY`。

批量（>300 篇）必须分批；连续 Cloudflare 拦截时停下来排障，不要硬冲。

## 输出 (Output)

- 每篇下载结果必含：文件路径、**实际来源**（OA / 出版商 API / 机构通道 / 灰色源）、耗时；失败结果带 `error_type`、`action`、`source_failures`（逐渠道明细）。
- 引文结果按请求格式输出；批量结果落盘 `batch_results.json`（含失败清单，可用 `batch --retry` 补齐）。
- 诊断结果为分级报告（`ready` / `partial` / `limited`），每项失败附下一步动作。

## 排障 (Error Handling)

| 症状 | 首个动作 |
|---|---|
| 工具列表没有 `scansci_pdf_*` | 命令未安装或插件未启用 → 走前置条件安装引导，或用 CLI 兜底 |
| Sci-Hub 返回 Cloudflare/Turnstile | `scansci_pdf_diagnostics(check="health")` 查浏览器后端；或改走机构路径 |
| 日志出现 "browser not available, skipping browser strategy" | 可选浏览器后端未装 → `pip install "scansci-pdf[camoufox]"` 后重试；该症状意味着出版商官网型 OA 文章会下载失败 |
| 所有源超时 | `scansci_pdf_diagnostics(check="network")` 查代理与 DNS |
| Elsevier 只回 1 页预览 | API key 无效或无权限 → 重新 setup 并 `--validate` |
| 结果带 `config_needed` / `ask_user_email` | 缺用户决策（如 Unpaywall 需真实邮箱）→ 问用户，不要替用户猜 |
| 机构登录页卡住 | session 过期 → 重新 `scansci_pdf_login` |
| `get` 返回的路径不在指定 `--output` 目录 | 缓存命中：返回的是此前下载的文件。换源重下或改输出位置先清缓存（`rm -f <out>/.doi_index.json && rm -rf ~/.scansci-pdf/cache/*`） |
| CLI 模式需要 BibTeX/引文 | `citation` 仅 MCP 提供 → agent 用检索结果字段（title/authors/year/doi）构造 BibTeX，或启用 MCP server |
| 403 / 超时 ≠ 无全文 | 多为反爬或网络受限，交给浏览器后端或代理，不要直接判死 |

## 合规边界 (Operating Boundaries)

- 灰色源（Sci-Hub / LibGen）与反爬路由**仅在用户明确选择时使用**，且限于用户有权且适用规则允许的场景；用户选择 `legal_only` 后调度不得回退。
- 保留用户指定的来源策略，并在每个结果中如实报告实际来源——不静默换渠道。
- API key、cookie、代理凭据、机构信息视为机密，不在回复中复述。
- 打开交互式登录、导入 cookie、更改访问配置前先征得用户同意。
