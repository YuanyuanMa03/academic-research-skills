---
name: ieee-journal-browse
description: Browses a journal or conference on IEEE Xplore — views info, impact factor, latest articles, and specific issues. Use when the user asks about a journal/conference or wants to browse its contents.
argument-hint: "[journal name or punumber]"
---

# IEEE Xplore Journal/Conference Browse

Browse journal or conference information, metrics, and articles on IEEE Xplore.

## URL Patterns

| Page | URL |
|------|-----|
| Journal home | `{BASE_URL}/xpl/RecentIssue.jsp?punumber={PUNUMBER}` |
| Popular articles | `{BASE_URL}/xpl/topAccessedArticles.jsp?punumber={PUNUMBER}` |
| Current issue | `{BASE_URL}/xpl/mostRecentIssue.jsp?punumber={PUNUMBER}` |
| All issues | `{BASE_URL}/xpl/issues?punumber={PUNUMBER}` |
| About journal | `{BASE_URL}/xpl/aboutJournal.jsp?punumber={PUNUMBER}` |
| Early access | `{BASE_URL}/xpl/tocresult.jsp?isnumber={ISNUMBER}` |
| Conference home | `{BASE_URL}/xpl/conhome/{PUNUMBER}/proceeding` |

The `punumber` (publication number) is the unique identifier for journals and conferences on IEEE Xplore.

### Common Journal PUNUMBERs

| Journal | punumber |
|---------|----------|
| IEEE Trans. Pattern Analysis and Machine Intelligence (TPAMI) | 34 |
| IEEE Trans. Neural Networks and Learning Systems (TNNLS) | 5962 |
| IEEE Trans. Image Processing (TIP) | 83 |
| IEEE Access | 6287639 |
| IEEE Trans. Information Forensics and Security (TIFS) | 10206 |
| IEEE Communications Surveys & Tutorials | 9739 |
| IEEE Internet of Things Journal | 6488907 |

If the user provides a journal name instead of a punumber, search for the journal first, or try constructing the URL from the name.

## Steps

### Step 1: Navigate to journal page

Use `navigate_page` with `initScript`:

```
navigate_page({
  url: "{BASE_URL}/xpl/RecentIssue.jsp?punumber={PUNUMBER}",
  initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
})
```

For conferences, use:
```
{BASE_URL}/xpl/conhome/{PUNUMBER}/proceeding
```

### Step 2: Extract journal info

Use `evaluate_script` with built-in waiting. Do NOT use `wait_for`.

```javascript
async () => {
  // Wait for journal content to load (up to 15s)
  for (let i = 0; i < 30; i++) {
    if (document.querySelector('h1') && document.querySelectorAll('a[href*="/document/"]').length > 0) break;
    await new Promise(r => setTimeout(r, 500));
  }

  const result = {};

  // Journal name
  result.name = document.querySelector('h1')?.textContent?.trim() || '';

  // Metrics
  const metricsContainer = document.querySelector('[class*="publication-info"]') || document.body;
  const allText = metricsContainer.innerText || '';

  const ifMatch = allText.match(/([\d.]+)\s*Impact Factor/);
  const efMatch = allText.match(/([\d.]+)\s*Eigenfactor/);
  const aiMatch = allText.match(/([\d.]+)\s*Article Influence/);
  const csMatch = allText.match(/([\d.]+)\s*CiteScore/);

  result.impactFactor = ifMatch ? ifMatch[1] : '';
  result.eigenfactor = efMatch ? efMatch[1] : '';
  result.articleInfluence = aiMatch ? aiMatch[1] : '';
  result.citeScore = csMatch ? csMatch[1] : '';

  // Tabs available
  const tabs = [...document.querySelectorAll('.tabs a, .nav-tabs a, [class*="tab-link"]')];
  result.tabs = tabs.map(a => ({
    text: a.textContent.trim(),
    href: a.href || ''
  })).filter(t => t.text).slice(0, 10);

  // Latest/popular articles on the page
  result.articles = [];
  const articleLinks = document.querySelectorAll('a[href*="/document/"]');
  const seen = new Set();
  articleLinks.forEach(link => {
    const title = link.textContent.trim();
    const arnumber = link.href.match(/\/document\/(\d+)/)?.[1] || '';
    if (title && arnumber && !seen.has(arnumber) && title.length > 10) {
      seen.add(arnumber);
      result.articles.push({ title: title.substring(0, 150), arnumber, url: link.href });
    }
  });
  result.articles = result.articles.slice(0, 15);

  // ISSN from page
  const pageText = document.body.innerText;
  const issnMatch = pageText.match(/ISSN[:\s]*([\d-X]+)/i);
  result.issn = issnMatch ? issnMatch[1] : '';

  // Publication number
  const urlMatch = window.location.href.match(/punumber=(\d+)/);
  result.punumber = urlMatch ? urlMatch[1] : '';

  return result;
}
```

### Step 3: Present journal info

```
## {name}

**Impact Factor**: {impactFactor}
**CiteScore**: {citeScore}
**Eigenfactor**: {eigenfactor}
**Article Influence Score**: {articleInfluence}
**ISSN**: {issn}
**PUNUMBER**: {punumber}

### Available Sections
{tabs}

### Articles
1. {title} (Article #: {arnumber})
2. ...
```

## Browsing a specific issue

If the user asks for a specific volume/issue, navigate to `{BASE_URL}/xpl/tocresult.jsp?punumber={PUNUMBER}&isnumber={ISNUMBER}` and extract the article list.

To find issue numbers, navigate to the "All Issues" page first:
```
{BASE_URL}/xpl/issues?punumber={PUNUMBER}
```

## Notes

- `punumber` is the primary identifier for journals and conferences on IEEE Xplore.
- Journal pages show latest published articles, early access, popular articles, etc.
- Conference pages show proceedings grouped by conference year.
- Always include `initScript` on every `navigate_page` call.
- Use 2 tool calls: `navigate_page` + `evaluate_script`.
