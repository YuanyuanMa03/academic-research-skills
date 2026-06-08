---
name: ieee-navigate-pages
description: Navigates pages, changes sort order, or adjusts results per page on IEEE Xplore search results. Use when the user wants to go to the next page, sort by date or citations, or change results per page.
argument-hint: "[next|prev|page N|sort by date|show 50]"
---

# IEEE Xplore Pagination & Sorting

Navigate between result pages, change sorting, or adjust results per page.

## How pagination works

IEEE Xplore uses URL parameters for pagination:
- `pageNumber` — page number (1-based). Default is 1.
- `rowsPerPage` — results per page. Options: `25`, `50`, `75`, `100`.
- `sortType` — sort order. See table below.

## Sort Options

| Sort value | Description |
|------------|-------------|
| _(omit)_ | Relevance (default) |
| `newest` | Newest first |
| `oldest` | Oldest first |
| `paper-citations` | Most cited by papers |
| `patent-citations` | Most cited by patents |
| `most-popular` | Most popular |
| `pub-title-asc` | Publication title A-Z |
| `pub-title-desc` | Publication title Z-A |

## Steps

### Step 1: Determine current state

Use `evaluate_script` to read the current URL and pagination info:

```javascript
() => {
  const url = new URL(window.location.href);
  const params = Object.fromEntries(url.searchParams);
  const resultCount = document.querySelector('.Dashboard-header span')?.textContent?.trim() || '';
  const activePage = document.querySelector('.pagination-bar button.active, ul.my-3 button.active')?.textContent?.trim() || '';
  return { params, resultCount, activePage, currentUrl: window.location.href };
}
```

### Step 2: Build target URL

Based on `$ARGUMENTS`, modify the URL parameters:

| User intent | Action |
|-------------|--------|
| "next" / "下一页" | `pageNumber += 1` |
| "prev" / "上一页" | `pageNumber -= 1` (min 1) |
| "page 3" / "第3页" | `pageNumber = 3` |
| "sort by date" / "按日期排序" | add `sortType=newest` |
| "sort by citations" | add `sortType=paper-citations` |
| "sort by relevance" / "按相关性排序" | remove `sortType` |
| "show 100" / "每页100条" | set `rowsPerPage=100`, reset `pageNumber=1` |

### Step 3: Navigate and extract

Use `navigate_page` to the new URL. **Always include `initScript`**:
```
initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
```

Then extract results using `evaluate_script` with built-in waiting (same as `ieee-search`). Do NOT use `wait_for`.

## Notes

- Always preserve existing query parameters (`queryText`, `matchBoolean`, `ranges`, etc.) when modifying pagination/sort.
- When changing `rowsPerPage`, reset `pageNumber` to 1 to avoid out-of-range pages.
- Maximum 2-3 tool calls per operation.
