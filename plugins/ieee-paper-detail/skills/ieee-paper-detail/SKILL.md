---
name: ieee-paper-detail
description: Extracts full metadata from an IEEE Xplore article page (abstract, authors, keywords, DOI, references, PDF link). Use when the user wants details about a specific paper.
argument-hint: "[article number or URL]"
---

# IEEE Xplore Paper Detail Extraction

Extract complete metadata from an IEEE Xplore article page.

## Steps

### Step 1: Navigate to article

Determine the article URL from `$ARGUMENTS`:
- If an article number is given (e.g. `8876906`): URL is `{BASE_URL}/document/{ARNUMBER}/`
- If a full URL is given: use that URL directly
- If a DOI is given: URL is `https://doi.org/{DOI}` (will redirect to IEEE Xplore)

Use `navigate_page` with `initScript`:

```
navigate_page({
  url: "{article_url}",
  initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
})
```

If the article is already open in the current tab, skip navigation and go directly to Step 3.

### Step 2: Check access

After navigation, verify:
- If the page shows a captcha or bot challenge: tell the user "请在浏览器中完成验证后告知我。"
- If the page URL no longer points to IEEE Xplore, the user may need to log in. Tell the user: "页面被重定向，请在浏览器中完成登录或认证后告知我。"

### Step 3: Extract metadata

Use `evaluate_script` with built-in waiting. Do NOT use `wait_for`.

```javascript
async () => {
  // Wait for article content to load (up to 15s)
  for (let i = 0; i < 30; i++) {
    if (document.querySelector('.document-title') || document.querySelector('h1[class*="title"]')) break;
    await new Promise(r => setTimeout(r, 500));
  }

  const result = {};

  // Title
  result.title = document.querySelector('.document-title span')?.textContent?.trim() ||
                 document.querySelector('h1[class*="title"]')?.textContent?.trim() || '';

  // Authors
  result.authors = [...document.querySelectorAll('.authors-info a[href*="/author/"]')]
    .map(a => a.textContent.trim()).filter(Boolean);

  // Abstract
  result.abstract = document.querySelector('.abstract-text div[xplmathjax]')?.textContent?.trim() ||
                    document.querySelector('.abstract-text')?.textContent?.trim() || '';

  // DOI
  const doiLink = document.querySelector('a[href*="doi.org"]');
  result.doi = doiLink?.textContent?.trim() || '';

  // Publication info
  result.publication = document.querySelector('.stats-document-abstract-publishedIn a')?.textContent?.trim() || '';

  // Meta info (Published in, Date, DOI, Publisher, Conference Location, etc.)
  const metaItems = document.querySelectorAll('.abstract-desktop-div .u-pb-1');
  result.metaInfo = [...metaItems].map(el => el.textContent.trim().replace(/\s+/g, ' ')).filter(Boolean);

  // Keywords - multiple fallback strategies (keywords section may need scrolling to load)
  // Strategy 1: keywords module links
  let kwLinks = document.querySelectorAll('.stats-keywords-module a');
  result.keywords = [...kwLinks].map(a => a.textContent.trim()).filter(Boolean);

  // Strategy 2: keyword list items
  if (result.keywords.length === 0) {
    const kwItems = document.querySelectorAll('.doc-keywords-list-theme li a, .doc-keywords-list li a');
    result.keywords = [...kwItems].map(a => a.textContent.trim()).filter(Boolean);
  }

  // Strategy 3: extract from the plain text citation (keywords field inside citation text)
  if (result.keywords.length === 0) {
    const kwMatch = document.body.innerText.match(/keywords:\s*\{([^}]+)\}/i);
    if (kwMatch) {
      result.keywords = kwMatch[1].split(';').map(k => k.trim()).filter(Boolean);
    }
  }

  // Strategy 4: meta tag
  if (result.keywords.length === 0) {
    const kwMeta = document.querySelector('meta[name="keywords"]');
    if (kwMeta) {
      result.keywords = kwMeta.content.split(',').map(k => k.trim()).filter(Boolean);
    }
  }

  // PDF link
  const pdfLink = document.querySelector('a[href*="stamp/stamp.jsp"]');
  result.pdfUrl = pdfLink?.href || '';

  // Article number from URL
  result.arnumber = window.location.pathname.match(/\/document\/(\d+)/)?.[1] || '';

  // Cited by count — use multiple strategies
  const citeMetric = [...document.querySelectorAll('.document-banner-metric')].find(el => el.textContent.includes('Cites'));
  result.citedBy = citeMetric?.querySelector('.document-banner-metric-count')?.textContent?.trim() || '';
  // Fallback: regex from button text like "70Cites inPapers"
  if (!result.citedBy) {
    const citeBtn = [...document.querySelectorAll('button')].find(b => b.textContent.includes('Cites'));
    const citeMatch = citeBtn?.textContent?.match(/(\d+)\s*Cites/);
    result.citedBy = citeMatch ? citeMatch[1] : '';
  }

  // Full text views
  const viewMetric = [...document.querySelectorAll('.document-banner-metric')].find(el => el.textContent.includes('Views'));
  result.fullTextViews = viewMetric?.querySelector('.document-banner-metric-count')?.textContent?.trim() || '';
  if (!result.fullTextViews) {
    const viewBtn = [...document.querySelectorAll('button, .document-banner-metric')].find(b => b.textContent.includes('Views'));
    const viewMatch = viewBtn?.textContent?.match(/(\d[\d,]*)\s*Full/);
    result.fullTextViews = viewMatch ? viewMatch[1] : '';
  }

  // Section headings (article structure / TOC)
  result.sections = [...document.querySelectorAll('.document-toc a, h2')]
    .map(el => el.textContent.trim())
    .filter(t => t && !t.includes('Abstract') && t.length < 100)
    .slice(0, 20);

  // References count
  const refSection = document.querySelector('#references');
  const refItems = document.querySelectorAll('.reference-container, [class*="reference-item"]');
  result.referenceCount = refItems.length;

  return result;
}
```

### Step 4: Present metadata

Format the output clearly:

```
## {title}

**Authors**: {authors}
**Publication**: {publication}
**DOI**: {doi}
**Article #**: {arnumber}

### Meta Info
{metaInfo items, each on its own line}

### Abstract
{abstract}

### Keywords
{keywords}

### Article Structure
{sections}

**Cited by**: {citedBy} papers
**Full Text Views**: {fullTextViews}
**PDF**: {pdfUrl or "Not available"}
```

## Key CSS Selectors

| Element | Selector |
|---------|----------|
| Title | `.document-title span` |
| Authors | `.authors-info a[href*="/author/"]` |
| Abstract | `.abstract-text div[xplmathjax]` |
| DOI link | `a[href*="doi.org"]` |
| Publication | `.stats-document-abstract-publishedIn a` |
| Meta items | `.abstract-desktop-div .u-pb-1` |
| Keywords | `.stats-keywords-module a` |
| PDF link | `a[href*="stamp/stamp.jsp"]` |
| Cite button | `button` containing text "Cite This" |
| Cited by count | `.document-banner-metric-count` |
| Section headings | `.document-toc a`, `h2` |

## Notes

- PDF link format: `{BASE_URL}/stamp/stamp.jsp?tp=&arnumber={ARNUMBER}`
- The `arnumber` is the universal identifier across IEEE Xplore (like PII on ScienceDirect).
- Always include `initScript` on every `navigate_page` call.
- This skill uses 2 tool calls: `navigate_page` + `evaluate_script`.
