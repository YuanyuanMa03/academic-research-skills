---
name: cnki-search
description: CNKI (中国知网) 全流程技能：关键词检索、高级检索（作者/期刊/日期/核心库过滤）、论文详情解析、结果页解析、翻页、期刊检索/目录/导航。Use when the user wants to search CNKI, browse CNKI journals, or open/parse CNKI paper pages.
argument-hint: "[search keywords]"
version: 2.0.0
---

# CNKI Search — 全流程技能

一个技能覆盖 CNKI 站内全部动作。基础检索在本文件；其余场景按路由表进入对应子流程文档。

## 场景路由

| 用户想做什么 | 进入哪个流程 |
|---|---|
| 关键词检索（本文件主流程） | 下文 Steps |
| 高级检索（作者/标题/期刊/日期/SCI-EI-CSSCI-北大核心过滤） | [references/advanced-search.md](references/advanced-search.md) |
| 打开/解析某篇论文详情页 | [references/paper-detail.md](references/paper-detail.md) |
| 解析当前结果页（独立于检索） | [references/parse-results.md](references/parse-results.md) |
| 结果翻页 | [references/navigate-pages.md](references/navigate-pages.md) |
| 检索特定期刊 | [references/journal-search.md](references/journal-search.md) |
| 浏览期刊目录（某期文章列表） | [references/journal-toc.md](references/journal-toc.md) |
| 期刊导航体系（核心期刊分类） | [references/journal-index.md](references/journal-index.md) |
| 下载/导出/推送 Zotero | 条目交给 `scansci-pdf` 技能（见文末） |

## Arguments

$ARGUMENTS contains the search keyword(s) in Chinese or English.

## Steps

### 1. Navigate

Use `mcp__chrome-devtools__navigate_page` → `https://kns.cnki.net/kns8s/search`

### 2. Search + extract results (single evaluate_script, NO wait_for)

Replace `YOUR_KEYWORDS` with actual search terms:

```javascript
async () => {
  const query = "YOUR_KEYWORDS";

  // Wait for search input (replaces wait_for)
  await new Promise((r, j) => {
    let n = 0;
    const c = () => { if (document.querySelector('input.search-input')) r(); else if (++n > 30) j('timeout'); else setTimeout(c, 500); };
    c();
  });

  // Check captcha (only if visible on screen, not hidden SDK at top:-1000000)
  const outer = document.querySelector('#tcaptcha_transform_dy');
  if (outer && outer.getBoundingClientRect().top >= 0) return { error: 'captcha' };

  // Fill and submit (verified selectors: input.search-input, input.search-btn)
  const input = document.querySelector('input.search-input');
  input.value = query;
  input.dispatchEvent(new Event('input', { bubbles: true }));
  document.querySelector('input.search-btn')?.click();

  // Wait for results
  await new Promise((r, j) => {
    let n = 0;
    const c = () => { if (document.body.innerText.includes('条结果')) r(); else if (++n > 30) j('timeout'); else setTimeout(c, 500); };
    c();
  });

  // Check captcha again
  const outer2 = document.querySelector('#tcaptcha_transform_dy');
  if (outer2 && outer2.getBoundingClientRect().top >= 0) return { error: 'captcha' };

  // Extract current page results (merged parse-results)
  const rows = document.querySelectorAll('.result-table-list tbody tr');
  const checkboxes = document.querySelectorAll('.result-table-list tbody input.cbItem');
  const results = Array.from(rows).map((row, i) => {
    const titleLink = row.querySelector('td.name a.fz14');
    const authors = Array.from(row.querySelectorAll('td.author a.KnowledgeNetLink') || []).map(a => a.innerText?.trim());
    const journal = row.querySelector('td.source a')?.innerText?.trim() || '';
    const date = row.querySelector('td.date')?.innerText?.trim() || '';
    const citations = row.querySelector('td.quote')?.innerText?.trim() || '';
    const downloads = row.querySelector('td.download')?.innerText?.trim() || '';
    return {
      n: i + 1,
      title: titleLink?.innerText?.trim() || '',
      href: titleLink?.href || '',
      exportId: checkboxes[i]?.value || '',
      authors: authors.join('; '),
      journal,
      date,
      citations,
      downloads
    };
  });

  return {
    query,
    total: document.querySelector('.pagerTitleCell')?.innerText?.match(/([\d,]+)/)?.[1] || '0',
    page: document.querySelector('.countPageMark')?.innerText || '1/1',
    results
  };
}
```

### 3. Report

Present results as a numbered list:

```
Searched CNKI for "$ARGUMENTS": found {total} results (page {page}).

1. {title}
   Authors: {authors} | Journal: {journal} | Date: {date}
   Citations: {citations} | Downloads: {downloads}

2. ...
```

### 4. Follow-up: navigate to a paper

When the user wants to open or download a specific paper, use `navigate_page` with the result's `href` URL directly — do NOT click the link (clicking opens a new tab and wastes 3 extra tool calls for tab management).

## Captcha detection

Check `#tcaptcha_transform_dy` element's `getBoundingClientRect().top >= 0`.
Tencent captcha SDK preloads DOM at `top: -1000000px` (off-screen, not active).
Only return `error: 'captcha'` when `top >= 0` (actually visible to user).

## Verified selectors

| Element | Selector | Notes |
|---------|----------|-------|
| Search input | `input.search-input` | id=`txt_search`, placeholder "中文文献、外文文献" |
| Search button | `input.search-btn` | type="button" |
| Result count | `.pagerTitleCell` | text "共找到 X 条结果" |
| Page indicator | `.countPageMark` | text "1/300" |
| Result rows | `.result-table-list tbody tr` | Each row = one paper |
| Title link | `td.name a.fz14` | Paper title with href |
| Authors | `td.author a.KnowledgeNetLink` | Author name links |
| Journal | `td.source a` | Journal/source link |
| Date | `td.date` | Publication date text |
| Citations | `td.quote` | Citation count |
| Downloads | `td.download` | Download count |

## Batch export to Zotero

When user wants to save results to Zotero, hand the collected entries (title, authors, source, date) to the `scansci-pdf` skill — `scansci_pdf_citation` for citation export, `scansci_pdf_zotero_push` for the Zotero push. The old `cnki-export` skill was removed; `docs/REFERENCE.md` has the migration table.

## Tool calls: 2 (navigate + evaluate_script)
