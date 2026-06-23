---
name: ieee-parse-results
description: Re-parses the currently open IEEE Xplore search results page. Internal skill used by other skills to extract structured data without navigation.
argument-hint: "[current IEEE Xplore results page or exported result HTML]"
version: 0.1.0
user-invocable: false
---

# Parse Current IEEE Xplore Results Page

Extract structured data from an already-open IEEE Xplore search results page without navigating.

## When to use

- After the user has manually navigated to a search results page
- When re-parsing results after sorting or filtering changes
- Called internally by other skills

## Steps

### Step 1: Extract results from current page

Use `evaluate_script` (no navigation needed):

```javascript
async () => {
  // Verify we are on a search results page
  if (!window.location.pathname.includes('/search')) {
    return { error: 'Not on an IEEE Xplore search results page.' };
  }

  // Wait for results if still loading
  for (let i = 0; i < 20; i++) {
    if (document.querySelectorAll('.List-results-items .result-item').length > 0) break;
    await new Promise(r => setTimeout(r, 500));
  }

  const items = document.querySelectorAll('.List-results-items .result-item');
  if (items.length === 0) {
    return { error: 'No results found on the current page. The page may still be loading.' };
  }

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
    const itemText = item.textContent || '';
    const citedByMatch = itemText.match(/Cited by:.*?(\d+)/);
    const citedBy = citedByMatch ? citedByMatch[1] : '';
    const hasCheckbox = !!item.querySelector('input[type="checkbox"]');

    papers.push({
      rank: i + 1,
      title: titleLink?.textContent?.trim()?.replace(/<[^>]+>/g, '') || '',
      arnumber: docNumber,
      authors,
      publication: pubLink?.textContent?.trim() || '',
      year: yearMatch ? yearMatch[1] : '',
      info: infoText,
      citedBy,
      hasCheckbox,
    });
  }

  const resultCount = document.querySelector('.Dashboard-header span')?.textContent?.trim() || '';
  const currentUrl = window.location.href;
  const urlParams = Object.fromEntries(new URL(currentUrl).searchParams);

  return { papers, resultCount, currentUrl, urlParams };
}
```

### Step 2: Return structured data

Return the extracted data. The `arnumber` field is the primary key for all subsequent operations (detail, download, export).

## Notes

- This skill uses only 1 tool call (`evaluate_script`).
- It does NOT navigate — it reads the current page as-is.
- If results are empty, the page may still be loading; the built-in wait loop handles this.
