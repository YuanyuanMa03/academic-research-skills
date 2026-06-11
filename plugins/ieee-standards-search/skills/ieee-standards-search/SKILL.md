---
name: ieee-standards-search
description: Searches IEEE SA (standards.ieee.org) for IEEE/ANSI standards. Use when the user wants to find IEEE standards, or when searching for IEC/ISO standard counterparts in the IEEE ecosystem.
argument-hint: "[standard number or keywords]"
version: 0.1.0
---

# IEEE SA Standards Search

Search the IEEE Standards Association website (standards.ieee.org) for IEEE and ANSI standards.

## When to use

- User asks for an IEEE or ANSI standard by number (e.g. "C93.1", "IEEE 4")
- User searches for an IEC standard and needs the IEEE counterpart (e.g. IEC 60358 → IEEE C93.1)
- User wants to find standards on a specific topic (e.g. "power line carrier coupling")
- `ieee-search` on IEEE Xplore returned no results for a standards query

**Important**: This skill searches **standards.ieee.org**, NOT ieeexplore.ieee.org. These are different websites with different structures.

## IEC ↔ IEEE Standard Cross-Reference

Common cross-references for the PLC / coupling capacitor / HV test domain:

| IEC Standard | IEEE Counterpart | Topic |
|-------------|-----------------|-------|
| IEC 60358-1/-2/-3/-4 | IEEE/ANSI C93.1-1999 + PC57.13.9 (Draft) | PLC coupling capacitors / CCVT |
| IEC 60481 | IEEE C93.4-2012 | PLC line-tuning equipment (30–500 kHz) |
| _(line trap)_ | IEEE C93.3-2017 | PLC line traps (30–500 kHz) |
| _(PLC application)_ | IEEE 643-1980 | PLC application guide |
| IEC 60060-1/-2 | IEEE 4-2013 | High-voltage testing techniques |
| IEC 60085 | IEEE P1 (Draft) + IEEE C57.12.60-2020 | Insulation thermal evaluation / thermal class |
| IEC 61869-5 | _(no direct IEEE counterpart)_ | CVT additional requirements |

## Steps

### Step 1: Navigate to IEEE SA search

Use `navigate_page` to:

```
https://standards.ieee.org/search/?q={QUERY}
```

Where `{QUERY}` is the URL-encoded search terms from `$ARGUMENTS`.

**Always include `initScript`**:
```
initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
```

### Step 2: Extract results

Use `evaluate_script` with built-in waiting:

```javascript
async () => {
  // Wait for search results to load (up to 10s)
  for (let i = 0; i < 20; i++) {
    if (document.body.innerText.includes('result') || document.body.innerText.includes('Sorry')) break;
    await new Promise(r => setTimeout(r, 500));
  }

  const pageText = document.body.innerText;

  // Check for no results
  if (pageText.includes('no results were found')) {
    return { results: [], noResults: true, query: new URL(window.location.href).searchParams.get('q') || '' };
  }

  // Extract results by parsing the page structure
  // IEEE SA search results are rendered as cards/sections with standard number + description
  const results = [];
  const resultBlocks = document.querySelectorAll('.search-results .result, article, .card');

  if (resultBlocks.length > 0) {
    resultBlocks.forEach((block, i) => {
      const link = block.querySelector('a');
      const title = link?.textContent?.trim() || '';
      const href = link?.href || '';
      const desc = block.textContent.trim().substring(title.length).trim().substring(0, 300);
      if (title) {
        results.push({ rank: i + 1, title, href, description: desc });
      }
    });
  }

  // Fallback: parse from page text if DOM selectors don't match
  if (results.length === 0) {
    // IEEE SA search results appear as standard number + title + description in page text
    const lines = pageText.split('\n').map(l => l.trim()).filter(Boolean);
    let current = null;
    for (const line of lines) {
      // Match patterns like "IEEE C93.1™-1999" or "IEEE 4™-2013" or "PC93.4™"
      const stdMatch = line.match(/^(IEEE[\/\s].*?™.*?\d{4}|P[A-Z\d]+.*?™|IEEE\s+\d+.*?™.*?\d{4})/);
      if (stdMatch) {
        if (current) results.push(current);
        current = { rank: results.length + 1, standardNumber: line, title: '', description: '' };
      } else if (current && !current.title && line.length > 20 && !line.startsWith('Last modified')) {
        current.title = line.substring(0, 200);
      } else if (current && line.startsWith('Last modified')) {
        current.lastModified = line;
      } else if (current && current.title && !current.description && line.length > 30) {
        current.description = line.substring(0, 300);
        results.push(current);
        current = null;
      }
    }
    if (current) results.push(current);
  }

  // Extract result count
  const countMatch = pageText.match(/(\d+)\s+results?\s+found/);
  const resultCount = countMatch ? countMatch[1] + ' results found' : '';

  return { results: results.slice(0, 20), resultCount, url: window.location.href };
}
```

### Step 3: Present results

```
IEEE SA Standards Search: "{query}"
{resultCount}

1. **{standardNumber}**
   {title}
   {description}
   Last modified: {lastModified}

2. ...
```

### Step 4: Handle no results

If no results found:
- Suggest alternative search terms (broader keywords, different standard number format).
- If searching for an IEC standard, check the cross-reference table above and suggest the IEEE counterpart.
- Suggest searching IEEE Xplore (`ieee-search`) for related papers and IEEE standards that are also published there.

## Notes

- IEEE SA website (standards.ieee.org) is the official home for IEEE standard project pages, NOT IEEE Xplore.
- IEEE Xplore hosts the **full text** of published IEEE standards for download (with subscription).
- IEEE SA hosts the **catalog entries** with descriptions, status, and project information.
- For downloading the actual standard document, users need to go to the IEEE Xplore link or the IEEE SA shop.
- The search on standards.ieee.org returns standards, drafts, projects, and governance documents.
- This skill uses 2 tool calls: `navigate_page` + `evaluate_script`.
- IEC/ISO standards are NOT on standards.ieee.org either — they must be obtained from IEC Webstore (webstore.iec.ch).
