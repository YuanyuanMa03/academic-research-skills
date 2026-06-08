---
name: ieee-search
description: Searches for academic papers on IEEE Xplore. Use when the user wants to find papers by keyword on IEEE Xplore.
argument-hint: "[search keywords]"
---

# IEEE Xplore Basic Search

Search for academic papers on IEEE Xplore using Chrome DevTools MCP.

## Important: Determine the IEEE Xplore base URL

Before the first operation, check the current browser page URL to determine which IEEE Xplore domain the user is accessing. Store it as `BASE_URL`. Common patterns:
- Direct access: `https://ieeexplore.ieee.org`
- Institutional proxy: URL containing `ieeexplore` in the hostname (e.g. WebVPN or EZProxy)

Use whatever origin the user's browser is currently on. If no IEEE Xplore page is open, ask the user which URL to use.

## Steps

### Step 1: Navigate to search results

Use `navigate_page` to go to:

```
{BASE_URL}/search/searchresult.jsp?queryText={QUERY}&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true&rowsPerPage=25&pageNumber=1
```

Where `{QUERY}` is the URL-encoded search keywords from `$ARGUMENTS`.

**Important**: Always include `initScript` to prevent bot detection:
```
initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
```

### Step 2: Check access

After navigation, verify the page loaded correctly:
- If the page shows a captcha or bot detection challenge: tell the user "请在浏览器中完成验证后告知我。" Wait for confirmation.
- If the URL no longer contains `ieeexplore`, the user may have been redirected to a login page. Tell the user: "页面被重定向，请在浏览器中完成登录或认证后告知我。" Then wait.
- Otherwise, proceed.

### Step 3: Extract search results

Use `evaluate_script` with built-in waiting. Do NOT use `wait_for` — it returns the full page snapshot which can exceed token limits.

```javascript
async () => {
  // Wait for results to load (up to 15s)
  for (let i = 0; i < 30; i++) {
    if (document.querySelectorAll('.List-results-items .result-item').length > 0 ||
        document.querySelector('.Dashboard-header span')) break;
    await new Promise(r => setTimeout(r, 500));
  }

  const items = document.querySelectorAll('.List-results-items .result-item');
  const papers = [];

  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    const titleLink = item.querySelector('h3 a[href*="/document/"]');
    const authors = [...item.querySelectorAll('.author a[href*="/author/"]')].map(a => a.textContent.trim());
    const pubLink = item.querySelector('.description a[href*="/xpl/"]');
    const publisherInfo = item.querySelector('.publisher-info-container');
    const infoText = publisherInfo?.textContent?.trim() || '';
    const yearMatch = infoText.match(/Year:\s*(\d{4})/);
    const docNumber = titleLink?.href?.match(/\/document\/(\d+)/)?.[1] || '';
    const abstractSnippet = item.querySelector('.js-displayer-content span')?.textContent?.trim() || '';
    // Cited by: extract from full text content using regex (DOM selector varies across pages)
    const itemText = item.textContent || '';
    // Two formats: "Cited by: 70" (default sort) and "Cited by: Papers (190)" (citation sort)
    const citedByMatch = itemText.match(/Cited by:.*?(\d+)/);
    const citedBy = citedByMatch ? citedByMatch[1] : '';

    papers.push({
      rank: i + 1,
      title: titleLink?.textContent?.trim()?.replace(/<[^>]+>/g, '') || '',
      arnumber: docNumber,
      authors,
      publication: pubLink?.textContent?.trim() || '',
      year: yearMatch ? yearMatch[1] : '',
      info: infoText,
      citedBy,
      abstract: abstractSnippet.substring(0, 200),
    });
  }

  const resultCount = document.querySelector('.Dashboard-header span')?.textContent?.trim() || '';
  const noResults = resultCount.includes('No results') || items.length === 0;
  return { papers, resultCount, noResults };
}
```

### Step 4: Handle no results

If `noResults` is true:
1. Tell the user no results were found on IEEE Xplore.
2. Suggest broadening the search (use fewer keywords, remove quotes, try synonyms).
3. **Important**: IEEE Xplore does NOT host IEC, ISO, or CENELEC standard documents directly. If the user searched for an IEC/ISO standard number (e.g. "IEC 60358-2"), explain:
   - IEC standards must be obtained from the IEC Webstore (webstore.iec.ch) or national standardization bodies.
   - Suggest searching IEEE Xplore for the **technical topic** instead (e.g. "coupling capacitor power line carrier" instead of "IEC 60358").
   - Suggest searching IEEE SA (standards.ieee.org) for the corresponding IEEE/ANSI standard using `ieee-standards-search`.
   - Offer to search for papers that **reference** the IEC standard.

### Step 5: Present results

Format results as a numbered list:

```
{resultCount}

1. {title}
   Authors: {authors}
   Publication: {publication} | {year}
   Info: {info}
   Cited by: {citedBy} | Article #: {arnumber}

2. ...
```

## Key CSS Selectors

| Element | Selector |
|---------|----------|
| Result items | `.List-results-items .result-item` |
| Title link | `h3 a[href*="/document/"]` |
| Authors | `.author a[href*="/author/"]` |
| Publication link | `.description a[href*="/xpl/"]` |
| Publisher info | `.publisher-info-container` |
| Abstract snippet | `.js-displayer-content span` |
| Cited by | Regex `Cited by:\s*(\d+)` on item text (DOM selector unreliable) |
| Result count | `.Dashboard-header span` |
| Checkbox | `input[type="checkbox"][aria-label="Select search result"]` |

## URL Parameters

| Param | Description | Example |
|-------|-------------|---------|
| `queryText` | Query string | `deep learning` |
| `rowsPerPage` | Results per page | `25`, `50`, `75`, `100` |
| `pageNumber` | Page number (1-based) | `1`, `2`, `3` |
| `sortType` | Sort order | `newest`, `oldest`, `paper-citations`, `patent-citations`, `most-popular` |
| `highlight` | Highlight matches | `true` |
| `returnFacets` | Return facets | `ALL` |
| `returnType` | Return type | `SEARCH` |
| `matchPubs` | Match publications | `true` |

## Search Strategy (Learned from Testing)

**Quoting matters**: IEEE Xplore treats unquoted words as individual tokens joined by OR. Always quote multi-word phrases.

| Query | Results | Quality |
|-------|---------|---------|
| `coupling capacitor power line carrier` | ~12,000+ | Terrible — each word matches independently |
| `"coupling capacitor" "power line carrier"` | 4 | Excellent — exact phrases, both required |
| `"coupling capacitor" OR "capacitor divider"` | Moderate | OK — OR between synonyms of same concept |
| `"coupling capacitor" OR "power line carrier"` | ~12,000+ | Bad — OR between different concepts |

**Rules**:
1. **Always quote multi-word phrases** with double quotes
2. **Use AND (implicit) between different concepts** — just put quoted phrases next to each other
3. **Use OR only between synonyms** of the same concept (e.g. `"drain coil" OR "line trap"`)
4. **Add a domain anchor** like `"HVDC"` or `"high voltage"` to prevent cross-domain noise
5. If results > 500, the query is too broad — add more AND terms
6. If results = 0, the query is too narrow — remove one quoted phrase or try synonyms
7. For multi-topic searches, use `ieee-advanced-search` with `matchBoolean=true` for full boolean control

## Notes

- Results include article numbers (`arnumber`) needed for detail extraction, PDF download, and citation export.
- This skill performs at most 2 tool calls: `navigate_page` + `evaluate_script`.
- IEEE Xplore uses Angular and loads content dynamically; the wait loop in `evaluate_script` handles this.
- **IEEE Xplore does NOT host IEC/ISO/CENELEC standards**. For IEC standards, direct users to IEC Webstore. For corresponding IEEE/ANSI standards, use `ieee-standards-search`.
- The `citedBy` field is extracted via regex from the item's text content, not a specific DOM element, because IEEE Xplore's cited-by markup varies.
