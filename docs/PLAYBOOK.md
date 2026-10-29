# PLAYBOOK — academic-research-skills 维护手册

> **修改任何浏览器自动化 / 反爬相关技能之前，先读完这一份。**
> 本文档面向接手本项目的 Agent 与开发者，目标是避免"会话失忆 + 不先 grep 家底"导致的重复造轮子和回归。

## 铁律（每条对应一次真实事故）

1. **造轮子前先 grep 家底。** 改技能前先搜本仓库是否已有同类实现。仓库曾有镜像/资产健康机制被重复造过；跨插件脚本先看 `scripts/check_shared_assets.py` 的模板清单。
2. **修复必须变成 CI 检查。** 没有检查守住的修复，在下个会话等于不存在。本仓库 5 个检查脚本全部由真实事故驱动：
   - `validate_skills.py` / `validate_plugin_json.py`：SKILL 与 manifest 基线（pre-commit + CI）。
   - `check_shared_assets.py`：commit 2a1a086 曾只给部分插件配了 mcpServers，事后回填——现在 .mcp.json 必须逐字节匹配三个 canonical 模板之一。
   - `check_marketplace_consistency.py`：Codex 市场曾静默落后 Claude 市场两个插件（nature-paper-to-patent、nature-reviewer），且 33 个插件版本双份漂移——现在目录/双市场/REFERENCE 三方一致才放行。
   - `lint.yml` 硬编码路径检查：曾因 `HARDcoded`/`HARDCODED` 变量名笔误导致失败标志从未生效（2026-10-28 修复），修复后确认存量内容零误报。
3. **双市场同步**：插件目录、`.claude-plugin/marketplace.json`、`.agents/plugins/marketplace.json`、`docs/REFERENCE.md` 覆盖，四处必须一致。一致性脚本会拦，但别让 CI 当你的第一道防线。
4. **独立安装约束**：每个插件目录必须自包含（用户可能只装一个）。**不要引入 `shared/` 公共目录**——1.1.0 版曾做过共享模块重构，因破坏独立安装被整体回退（commit c0b84e6）。重复资产靠清单守漂移，不靠共享目录。
5. **每个验证过的单元立即提交**，不要攒大提交。
6. **引入外部依赖先定融合方式**：scansci-pdf（MIT）采用"MCP 配置 + 技能包装"而非复制其源码——升级靠 PyPI，本仓库零 vendoring 负担。新外部依赖照此评估。

## 决策账本

### v2.0.0：一个平台一个技能（2026-10-29）

47 → 16 个插件。动机：端到端实测（见 `docs/test-evidence/2026-10-29-e2e-workflow/`）显示核心高频链路只占少数；步骤级技能（navigate-pages/parse-results 等）拆成独立安装单元没有用户单独安装；GS/IEEE 平台实测失效无人修。

- **删除 15 个**：GS×4、IEEE×7（平台失效，被 scansci-pdf 跨源检索覆盖）；pm-advanced-search / pm-navigate-pages（pm-search 脚本参数已覆盖）、pm-paper-detail（pm-search 单篇查询可替代）、pm-fulltext（scansci-pdf 的 PMC 渠道覆盖）。
- **合并 19 → 3**：CNKI 8 → `cnki-search`、SD 6 → `sd-search`、WoS 5 → `wos-search`。被合并技能的 SKILL.md 全文转为 `references/<action>.md` 子流程文档（仅剥 frontmatter 加归属头），主 SKILL.md 顶部加「场景路由」表。内容零丢失。
- **保留 nature 11 个独立**：场景级（审稿/回复信/配图/专利）而非平台步骤拆分；合并会让只装一个场景的用户背上全部资产。
- 浏览器技能豁免名单清空：wos-dom/wos-parse-results 并入 wos-search。
- 判断依据：每个留下的插件必须有不可替代理由（精度入口/站内导航/写作场景/获取中枢），每条删除线有实测依据。

### 1.2.0：删除 12 个插件，文献获取切换 scansci-pdf（2026-10-28）

删除：`cnki-download`、`gs-fulltext`、`ieee-download`、`sd-download`、`wos-download`、`cnki-export`、`gs-export`、`ieee-export`、`pm-export`、`sd-export`、`wos-export`、`zotero-csl`。

理由：

1. **导出/Zotero 类（7 个）**：6 份 `push_to_zotero.py` 近重复（其中 gs/pm 两份逐字节相同、共 5 个变体 2385 行），走 Zotero Connector API（localhost:23119）的路线已过时；scansci-pdf 的 `scansci_pdf_citation` + `scansci_pdf_zotero_push` 开箱即用且持续维护。
2. **下载类（5 个）**：依赖浏览器 DOM 抓取 + 平台付费墙，2026-06-23 跨平台测试中 GS、IEEE 已超时失效；scansci-pdf 的多路由竞速（OA → 出版商 API → 机构通道）健壮得多。
3. 保留全部站内检索/导航技能与 `pm-fulltext`（PMC API，本身是好的 API-first 实现）。

替代路径：站内检索技能拿条目 → `scansci-pdf` 插件完成下载/引文/推送（见 REFERENCE 工作流）。git 历史可找回被删技能。

## 平台状态与失败签名表（2026-10-28 记录，会过期——改动前先复测）

基线：2026-06-23 跨平台抽取测试（证据在 `docs/test-evidence/2026-06-23-cross-platform-extraction/`）+ 2026-08-21 PubMed 抽查。

| 平台 | 状态（日期） | 失败签名 | 判定 | 处理 |
|---|---|---|---|---|
| PubMed | ✅ 双路径通过（2026-08-21） | 脚本 429/5xx | NCBI 限流 | 脚本自动重试一次；带 `--mailto` 进 polite pool |
| ScienceDirect | ✅ 通过（2026-06-23，用户 Chrome）；❌ 自动化 webview 即被拦（2026-10-29） | 页面要求登录；标题 `Just a moment...` + `Are you a robot?`（Cloudflare 指纹识别自动化上下文） | 会话失效 / 反爬墙 | 重新登录；自动化 webview 命中墙时不要重试——交用户可见浏览器过一次验证，或换 chrome-devtools 驱动用户日常 Chrome；持续失败转 scansci-pdf 机构通道 |
| CNKI | ✅ 通过（2026-06-23，用户 Chrome）；❌ 自动化 webview 加载即弹滑块（2026-10-29） | `请完成安全验证`+`向右滑动完成验证`（滑块）；`#tcaptcha_transform_dy` 可见（腾讯验证码） | 反爬墙 | 滑块：不要脚本硬拖，交用户可见浏览器滑一次或换 chrome-devtools；腾讯验证码按 cnki-search SKILL 判定；下载场景已移交 scansci-pdf |
| WoS | ✅ 通过（2026-06-23，仅 2 篇） | 内部 API 报 `no_session` | SID 过期 | wos-search 已内置回退：DOM 导航 / 结果解析子流程（references/parse-results.md）Mode B |
| Google Scholar | ❌ 超时（2026-06-23） | 长时间无响应 / CAPTCHA 页 | 反爬+配额 | 检索转 PubMed/CNKI 或 scansci-pdf `search`（13 源引擎）；修复前先复测 |
| IEEE Xplore | ❌ 超时（2026-06-23） | 长时间无响应 | 站点慢/反爬 | 同上；IEEE 官方 API 需 key，是双路径扩展候选 |

已知边界：测试结果快照在 `docs/test-evidence/`，GS/IEEE 恢复与否没有持续监测——见待办。

## pm-search 双路径范式（新增检索技能照此写）

`plugins/pm-search/skills/pm-search/SKILL.md` 是范式：

- **Path 1（默认）**：独立 Python 脚本直连官方 API（`scripts/pubmed_api_search.py`，E-utilities），单次工具调用，带 `--selftest` 离线自测（CI 跑的就是它）、429/5xx 重试、`--mailto` polite pool。
- **Path 2（兜底）**：无 shell 时用浏览器 navigate + 页面上下文 `fetch` 调 API——**永远不解析 DOM**。
- 下载/引文/推送不在这层做：拿到条目交给 scansci-pdf。

## MCP 模板与豁免

`.mcp.json` 必须逐字节匹配 `scripts/check_shared_assets.py` 里注册的三个模板之一：

| 模板 | 用途 | 样例 |
|---|---|---|
| `chrome-devtools` | 浏览器自动化技能 | `plugins/cnki-search/.mcp.json` |
| `academic-search` | nature-academic-search 自带 MCP | `plugins/nature-academic-search/.mcp.json` |
| `scansci-pdf` | 文献获取桥接 | `plugins/scansci-pdf/.mcp.json` |

豁免（无 .mcp.json 且有理由）：`wos-dom`（纯 DOM 结构参考文档，无运行时工具）、`wos-parse-results`（离线解析已保存快照）。

## 已知坑位（日期化，agent 必读）

- **2026-06-23**：GS、IEEE 跨平台测试超时（快照在 test-evidence）；GS 还会随机出 CAPTCHA（gs-search SKILL 有处理流程）。
- **2026-10-28**：`lint.yml` 的 `HARDcoded`/`HARDCODED` 笔误修复——此前硬编码路径检查失败永不生效；同日 33 个插件版本对齐（claude 侧 1.0.0 → codex 侧 1.0.1，取高者）。
- **2026-10-29 端到端实测**（课题"半导体材料在电池中的创新应用"，证据：`docs/test-evidence/2026-10-29-e2e-workflow/测试报告.md`）：
  - scansci-pdf `get` 缓存命中时忽略 `--output`，直接返回旧文件路径（`.doi_index.json` 索引）；换源/换目录先清缓存。
  - CLI 无引文命令（`citation` 仅 MCP）；CLI 兜底时 agent 需自行从检索字段构造 BibTeX——已写进桥接 SKILL.md 排障表。
  - 无浏览器后端（未装 `[camoufox]` extras）时，可下载范围收窄为"OA 仓库直链"型（实测 Wiley/RSC 官网 OA 页失败）；安装引导已补提示。
  - `scansci_pdf_search` 长复合查询相关性偏宽（被匹配到主题外结果），精确检索走平台技能——已写进 SKILL.md 与 REFERENCE.md。
  - PubMed 对材料/物理主题覆盖有限（光充电方向仅 6 条），印证双检索入口设计。
- CHANGELOG 曾长期只记录一条已失效的 shared/ 重构——现已刷新，新条目及时记。
- scansci-pdf MCP server 要求 Python ≥ 3.11；插件装好后工具列表没有 `scansci_pdf_*` 时先走 SKILL.md 的安装引导。

- **2026-10-29 浏览器墙实测**：CNKI 与 ScienceDirect 在自动化/内嵌 webview（ZCode IAB，Electron UA）下加载即被反爬识别（CNKI 滑块、SD Cloudflare "Are you a robot?"）。结论：浏览器平台技能的正确宿主是 chrome-devtools 驱动的**用户日常 Chrome**（各插件 .mcp.json 已带反检测参数）；签名与处置已写入 cnki-search / sd-search SKILL 与本表。

## 待办

- [ ] GS / IEEE 检索技能的 API-first 双路径扩展（IEEE 官方 API 需 key；GS 无免费 API，考虑降级建议）。
- [ ] 平台状态定期复测机制（借鉴 scansci-pdf 的 canary 思路：固定已知论文探测各平台，区分硬失败/软告警）。
- [ ] wos-search 内部 API 调用脚本化（当前是页面上下文 fetch）。
