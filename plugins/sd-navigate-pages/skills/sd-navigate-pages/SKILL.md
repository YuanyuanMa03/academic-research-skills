---
name: sd-navigate-pages
description: Navigate pages, change sort order, or adjust results per page on ScienceDirect search results.
argument-hint: "[next|prev|page N|sort by date|show 50]"
---

# ScienceDirect Pagination & Sorting

Navigate between result pages, change sorting, or adjust results per page.

## How pagination works

ScienceDirect uses URL parameters for pagination:
- `offset` — starting result index (0-based). Default is 0 (page 1).
- `show` — results per page. Options: `25`, `50`, `100`.
- `sortBy` — sort order. `date` for newest first; omit for relevance.

Page calculation: `page N` → `offset = (N - 1) * show`

## Steps

### Step 1: Determine current state

Use `evaluate_script` to read the current URL and pagination info:

```javascript
() => {
  const url = new URL(window.location.href);
  const params = Object.fromEntries(url.searchParams);
  const pageInfo = document.querySelector('.Pagination li:first-child')?.textContent?.trim() || '';
  const totalText = document.querySelector('.search-body-results-text')?.textContent?.trim() || '';
  return { params, pageInfo, totalText, currentUrl: window.location.href };
}
```

### Step 2: Build target URL

Based on `$ARGUMENTS`, modify the URL parameters:

| User intent | Action |
|-------------|--------|
| "next" / "下一页" | `offset += show` |
| "prev" / "上一页" | `offset -= show` (min 0) |
| "page 3" / "第3页" | `offset = (3-1) * show` |
| "sort by date" / "按日期排序" | add `sortBy=date` |
| "sort by relevance" / "按相关性排序" | remove `sortBy` |
| "show 100" / "每页100条" | set `show=100`, reset `offset=0` |

### Step 3: Navigate and extract

Use `navigate_page` to the new URL. **Always include `initScript`** to prevent bot detection:
```
initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
```

Then extract results using `evaluate_script` with built-in waiting. Do NOT use `wait_for` — it returns oversized snapshots.

```javascript
async () => {
  // Wait for results to load (up to 10s)
  for (let i = 0; i < 20; i++) {
    if (document.querySelector('li.ResultItem') || document.querySelector('.search-body-results-text')) break;
    await new Promise(r => setTimeout(r, 500));
  }

  const items = document.querySelectorAll('li.ResultItem');
  const papers = [];

  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    const titleLink = item.querySelector('a.result-list-title-link');
    const journal = item.querySelector('a.subtype-srctitle-link');
    const dateSpans = item.querySelectorAll('.srctitle-date-fields > span');
    const date = dateSpans.length > 1 ? dateSpans[dateSpans.length - 1].textContent.trim() : '';
    const authors = [...item.querySelectorAll('.Authors .author')].map(a => a.textContent.trim());
    const doi = item.getAttribute('data-doi');
    const pii = titleLink?.href?.match(/pii\/(\w+)/)?.[1] || '';
    const articleType = item.querySelector('.article-type')?.textContent?.trim() || '';
    const isOpenAccess = !!item.querySelector('.access-label');

    papers.push({
      rank: i + 1,
      title: titleLink?.textContent?.trim() || '',
      pii,
      doi: doi || '',
      journal: journal?.textContent?.trim() || '',
      date,
      authors,
      articleType,
      openAccess: isOpenAccess,
    });
  }

  const totalText = document.querySelector('.search-body-results-text')?.textContent?.trim() || '';
  const pageInfo = document.querySelector('.Pagination li:first-child')?.textContent?.trim() || '';

  return { papers, totalResults: totalText, pageInfo };
}
```

## Notes

- Always preserve existing query parameters (`qs`, `tak`, `authors`, etc.) when modifying pagination/sort.
- When changing `show`, reset `offset` to 0 to avoid out-of-range pages.
- Maximum 2-3 tool calls per operation.
