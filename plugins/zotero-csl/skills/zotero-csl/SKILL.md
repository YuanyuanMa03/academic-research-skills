---
name: csl
description: 根据用户描述的引用格式，生成 Zotero 可用的 CSL 样式文件
argument-hint: "[引用格式描述，如：GB/T 7714、APA、自定义格式说明]"
user-invocable: true
---

# CSL 样式生成器

所有模板、参数、规则均位于 `.` 目录下。

以下路径常量贯穿全流程：

| 常量 | 路径 |
|------|------|
| 预设目录 | `presets/` |
| 组件目录 | `components/` |
| 校验脚本 | `scripts/validate_csl.py` |
| 预览脚本 | `scripts/preview_csl.py` |
| 校验规则 | `validate/rules.md` |
| 输出目录 | `output/` |

## Step 0: 收集信息

分析用户输入 `$ARGUMENTS`，判断信息是否充足。如果不足，**必须先向用户确认以下内容再开始生成**：

1. **正文引用方式**（三选一，决定 CSL `class` 和 `citation` 配置）：
   - **上标角标**：正文中 `[1-3]` 以上标形式出现 → `class="in-text"`, `vertical-align="sup"`
   - **行内编号**：正文中 `[1-3]` 与正文同行同字号 → `class="in-text"`
   - **脚注/尾注**：正文中插入脚注标记，引用内容出现在页脚或文末 → `class="note"`

2. **参考文献列表示例**：至少需要用户提供 2-3 条不同类型（期刊、书籍、会议等）的参考文献原文，用于反推格式参数。

3. **正文引用示例**（可选）：包含引用标记的原文段落，用于确认引用样式。

如果用户已经提供了上述信息（如粘贴了参考文献和正文），直接进入 Step 1 分析。

## Step 1: 解析需求

从用户输入提取格式需求，匹配预设关键词：

| 关键词 | 预设文件 |
|--------|----------|
| GB/T 7714、国标、中文顺序编码 | `gbt7714-numeric.md` |
| GB/T 7714 著者-出版年、author-date | `gbt7714-author-date.md` |
| APA | `apa7.md` |
| Chicago Notes、芝加哥脚注 | `chicago-notes.md` |
| IEEE | `ieee.md` |
| MLA | `mla9.md` |
| 中文社科 note、脚注样式 | `chinese-note.md` |

- 匹配到 → 进入 Step 2a
- 未匹配 → 进入 Step 2b（从用户描述或参考文献示例反推参数）

## Step 2: 读取配方

**2a 预设路径：** 读取 `presets/{preset}.md`，获取全部参数。

**2b 自定义路径：** 按需读取 `components/` 下的组件模板：

| 组件 | 文件 | 职责 |
|------|------|------|
| 作者 | `name.md` | 姓名格式、et-al、排序 |
| 标题 | `title.md` | 斜体/引号/书名号 |
| 日期 | `date.md` | 年/月/日格式 |
| 期刊/书籍容器 | `container.md` | 期刊名、书名格式 |
| 卷期页 | `locators.md` | 卷/期/页码格式 |
| 出版信息 | `publisher.md` | 出版地、出版社 |
| DOI/URL | `access.md` | 电子资源访问信息 |
| 正文引用 | `citation.md` | citation 布局 |
| 参考文献列表 | `bibliography.md` | bibliography 布局 |
| 中文术语 | `locale-zh.md` | 中文本地化术语 |
| 英文术语 | `locale-en.md` | 英文本地化术语 |

根据用户需求选择性读取相关组件，无需全部加载。

## Step 3: 生成 CSL

按以下骨架组装完整 `.csl` 文件：

```
style (xmlns, class, version, default-locale)
  ├── info (title, id, category, updated)
  ├── locale × N (术语覆盖)
  ├── macro × N (按组件模板填充)
  ├── citation (正文引用 / 脚注)
  └── bibliography (参考文献列表)
```

- 各宏的 XML 实现从组件模板中获取，按预设参数调整属性值
- 输出到 `output/{style-name}.csl`

## Step 4: 校验

```bash
python scripts/validate_csl.py <file>
```

- 脚本输出 JSON 格式结果
- 如 `"status": "FAIL"`，根据 errors 修复后重新校验，直到 PASS
- 读取 `validate/rules.md` 做补充审核（常见陷阱检查）

## Step 5: 预览

```bash
python scripts/preview_csl.py <file>
```

- 展示真实渲染结果给用户
- 等待用户确认，或根据反馈返回 Step 3 修改

## Step 6: 修改已有样式（可选）

当用户提供现有 `.csl` 文件要求修改时：
1. 读取文件，定位需修改的部分
2. 参考对应组件模板进行修改
3. 重新执行 Step 4 + Step 5
