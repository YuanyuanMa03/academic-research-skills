---
name: wos-navigate-pages
description: Navigate to a specific page of WoS search results, or load more results from the last search.
argument-hint: "[page number or 'next'/'prev']"
user-invocable: true
disable-model-invocation: false
---

# WoS Navigate Pages

Load a specific page of results from the current WoS search.

## Steps

### Step A: URL-based navigation (preferred, 2 tool calls)

The results URL follows the pattern:
```
/wos/{database}/summary/{session-uuid}/{sort}/{page-number}
```

Use `evaluate_script` to read the current URL and compute the target:

```javascript
() => {
  const url = new URL(window.location.href);
  const parts = url.pathname.split('/');
  // Pattern: /wos/{db}/summary/{uuid}/{sort}/{page}
  const currentPage = parseInt(parts[parts.length - 1]) || 1;
  const sort = parts[parts.length - 2] || 'relevance';
  const basePath = parts.slice(0, -1).join('/');
  return { currentPage, sort, basePath, currentUrl: url.href };
}
```

Based on `$ARGUMENTS`, compute the target page number:

| User intent | Target page |
|-------------|-------------|
| "next" / "下一页" | `currentPage + 1` |
| "prev" / "上一页" | `max(1, currentPage - 1)` |
| "page 3" / "第3页" | `3` |

Then use `navigate_page` to `{basePath}/{targetPage}` with `initScript`:
```
initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
```

After navigation, extract results via `evaluate_script` with DOM selectors (see `wos-parse-results` Mode B). Uses **2 tool calls** total.

### Step B: API-based navigation (1 tool call, requires prior search context)

Re-run the search API with an updated `retrieve.first` offset. This approach reuses the active session (SID) and requires the agent to substitute search parameters from the prior `wos-search` call.

**Template substitution**: Before executing, replace the placeholders below:
- `{TARGET_PAGE}` → the target page number (1-based)
- `{QUERY_ROWS}` → the exact `query` array from the prior `wos-search` (e.g. `{"rowField": "TS", "rowText": "deep learning"}`)
- `{EDITIONS}` → the editions list from the prior search (e.g. `"WOS.SCI"`, or omit for all)
- `{SORT}` → the sort value from the prior search (e.g. `"relevance"`, `"date-descending"`)

```javascript
async () => {
  const sid = performance.getEntriesByType('resource')
    .filter(r => r.name.includes('SID='))
    .map(r => r.name.match(/SID=([^&]+)/)?.[1])
    .filter(Boolean)[0] || '';

  if (!sid) return { status: 'no_session', message: 'SID lost. Use Step A (URL-based) instead.' };

  const page = {TARGET_PAGE};
  const perPage = 50;
  const first = (page - 1) * perPage + 1;

  const response = await fetch(`/api/wosnx/core/runQuerySearch?SID=${sid}`, {
    method: 'POST',
    headers: { 'Content-Type': 'text/plain;charset=UTF-8', 'Accept': 'application/x-ndjson' },
    body: JSON.stringify({
      "product": "WOSCC",
      "searchMode": "general",
      "viewType": "search",
      "serviceMode": "summary",
      "search": {
        "mode": "general",
        "database": "WOSCC",
        "query": [{QUERY_ROWS}],
        "editions": [{EDITIONS}]
      },
      "retrieve": {
        "first": first,
        "count": perPage,
        "history": false,
        "jcr": true,
        "sort": "{SORT}",
        "analyzes": [],
        "locale": "en"
      },
      "eventMode": null
    })
  });

  const text = await response.text();
  const lines = text.trim().split('\n').map(l => { try { return JSON.parse(l); } catch(e) { return null; } }).filter(Boolean);
  const searchInfo = lines.find(l => l.key === 'searchInfo')?.payload;
  const recordsData = lines.find(l => l.key === 'records')?.payload;

  let records = [];
  if (recordsData) {
    records = Object.entries(recordsData).map(([idx, rec]) => ({
      idx: first + parseInt(idx) - 1,
      wosId: rec.colluid,
      title: rec.titles?.item?.en?.[0]?.title || '',
      authors: rec.names?.author?.en?.filter(Boolean).map(a => a.wos_standard).join('; ') || '',
      source: rec.titles?.source?.en?.[0]?.title || '',
      year: rec.pub_info?.pubyear || '',
      doi: rec.doi || '',
      citations: rec.citation_related?.counts?.WOSCC || 0
    }));
  }

  return { status: 'ok', page, totalResults: searchInfo?.RecordsFound || 0, records };
}
```

**When to use Step B**: Only when the agent has the original search parameters available in the conversation context (from a prior `wos-search` call). Otherwise, use Step A.

## Notes

- **Step A** (URL-based) is the default — it always works regardless of search context and uses 2 tool calls.
- **Step B** (API-based) is faster (1 tool call) but requires the agent to remember and substitute the original query/editions/sort parameters.
- `retrieve.first` is 1-based record offset (1 = first record, 51 = page 2, etc.)
- 50 records per page, max 100,000 records accessible
- If SID is lost (browser navigated to external site), use Step A or navigate to any WoS page first to re-establish the session.
