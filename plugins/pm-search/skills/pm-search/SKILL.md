---
name: pm-search
description: Search PubMed for biomedical literature by keywords. Returns structured results with PMID, title, authors, journal, date, DOI. Use when the user wants to find papers on a topic.
argument-hint: "[search keywords]"
version: 0.2.0
---

# PubMed Basic Search

Search PubMed for papers using keyword(s). Returns result count and structured result list via the NCBI E-utilities API — no login, no CAPTCHA, no DOM scraping.

## Requirements

- **Path 1 (default)**: `python3` + network access to `eutils.ncbi.nlm.nih.gov`. No browser needed.
- **Path 2 (fallback)**: a browser automation tool that can (a) navigate to a URL and (b) evaluate JavaScript in the page. Any such tool works (Chrome DevTools MCP, Playwright MCP, etc.) — do not assume a specific tool name.

## Arguments

$ARGUMENTS contains the search keyword(s) in English or Chinese.

## Steps

### Path 1 — Standalone script (default)

Run from this skill's directory (single tool call):

```bash
python3 scripts/pubmed_api_search.py "YOUR_KEYWORDS" --limit 20
```

Useful flags: `--page N`, `--sort date|relevance|pub_date|first_author|journal`, `--year-from 2022 --year-to 2026`, `--json` (machine-readable), `--mailto you@example.com` (or env `NCBI_MAILTO`, joins NCBI's polite pool).

The script retries once on 429/5xx and reports failures to stderr with exit code 1. Exit code 0 with `total: 0` means the query genuinely matched nothing.

### Path 2 — Browser evaluate (only when no shell is available)

Use your browser tool to navigate to `https://pubmed.ncbi.nlm.nih.gov/?term={URL_ENCODED_KEYWORDS}&size=20` (this shows the results page to the user), then evaluate the following script in the page. It calls the E-utilities API from page context — it never scrapes DOM.

Replace `YOUR_KEYWORDS` with the actual search terms:

```javascript
async () => {
  const query = "YOUR_KEYWORDS";
  const page = 1, size = 20;
  const retstart = (page - 1) * size;

  // E-utilities esearch: get PMID list
  const searchResp = await fetch(
    `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=${encodeURIComponent(query)}&retmax=${size}&retstart=${retstart}&retmode=json&sort=relevance`
  );
  const searchData = await searchResp.json();
  const ids = searchData.esearchresult?.idlist || [];
  const total = parseInt(searchData.esearchresult?.count || '0');
  const queryTranslation = searchData.esearchresult?.querytranslation || '';

  if (ids.length === 0) return { query, total: 0, results: [] };

  // E-utilities esummary: batch get metadata
  const sumResp = await fetch(
    `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=${ids.join(',')}&retmode=json`
  );
  const sumData = await sumResp.json();

  const results = ids.map((id, i) => {
    const r = sumData.result?.[id] || {};
    const doi = (r.articleids || []).find(a => a.idtype === 'doi')?.value || '';
    return {
      n: retstart + i + 1,
      pmid: id,
      title: r.title || '',
      authors: (r.authors || []).map(a => a.name).join(', '),
      journal: r.fulljournalname || '',
      source: r.source || '',
      pubdate: r.pubdate || '',
      volume: r.volume || '',
      issue: r.issue || '',
      pages: r.pages || '',
      doi,
      pubtype: (r.pubtype || []).join(', ')
    };
  });

  return { query, queryTranslation, total, page, size, results };
}
```

### Report

Present results as a numbered list (both paths produce the same shape):

```
Searched PubMed for "$ARGUMENTS": found {total} results (page {page}, showing {size} per page).

1. {title}
   PMID: {pmid} | DOI: {doi}
   Authors: {authors}
   Journal: {journal} ({pubdate}) | Vol {volume}({issue}):{pages}

2. ...
```

### Follow-up

When the user wants to:
- **Open a paper**: use `pm-paper-detail` with the PMID
- **See more results**: use `pm-navigate-pages` to go to next page (or `--page N` in Path 1)
- **Get full text**: use `pm-fulltext` with the PMID
- **Export to Zotero**: use `pm-export` with the PMID(s)

## Pagination

- Path 1: `--page` (1-indexed), `--limit` (default 20, max 10000)
- Path 2: `retstart`: 0-indexed offset (page 1 = 0, page 2 = 20, ...), `retmax` per page
- Total pages: ceil(total / size)

## Notes

- Tool call budget: Path 1 = 1 (single Bash call); Path 2 = 2 (navigate + evaluate)
- E-utilities API is public, no authentication needed
- Results come from the API, not DOM scraping, so site redesigns do not break this skill
