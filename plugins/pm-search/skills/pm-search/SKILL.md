---
name: pm-search
description: Search PubMed for biomedical literature by keywords. Returns structured results with PMID, title, authors, journal, date, DOI. Use when the user wants to find papers on a topic.
argument-hint: "[search keywords]"
---

# PubMed Basic Search

Search PubMed for papers using keyword(s). Returns result count and structured result list via NCBI E-utilities API.

## Arguments

$ARGUMENTS contains the search keyword(s) in English or Chinese.

## Steps

### 1. Navigate

Use `mcp__chrome-devtools__navigate_page`:
- url: `https://pubmed.ncbi.nlm.nih.gov/?term={URL_ENCODED_KEYWORDS}&size=20`
- This shows the search results page to the user in the browser.

### 2. Search + extract results (single evaluate_script)

Replace `YOUR_KEYWORDS` with the actual search terms from $ARGUMENTS:

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

### 3. Report

Present results as a numbered list:

```
Searched PubMed for "$ARGUMENTS": found {total} results (page {page}, showing {size} per page).

1. {title}
   PMID: {pmid} | DOI: {doi}
   Authors: {authors}
   Journal: {journal} ({pubdate}) | Vol {volume}({issue}):{pages}

2. ...
```

### 4. Follow-up

When the user wants to:
- **Open a paper**: use `pm-paper-detail` with the PMID
- **See more results**: use `pm-navigate-pages` to go to next page
- **Get full text**: use `pm-fulltext` with the PMID
- **Export to Zotero**: use `pm-export` with the PMID(s)

## Sort options

The `sort` parameter in esearch accepts:
- `relevance` (default, best match)
- `date` (most recent first)
- `pub_date` (publication date)
- `first_author` (alphabetical by first author)
- `journal` (alphabetical by journal)

To change sort, modify the `sort=` parameter in the esearch URL.

## Pagination

- `retstart`: 0-indexed offset (page 1 = 0, page 2 = 20, page 3 = 40, ...)
- `retmax`: results per page (default 20, max 10000)
- Total pages: ceil(total / size)

## Notes

- This skill uses 2 tool calls: `navigate_page` + `evaluate_script`
- E-utilities API is public, no authentication needed
- Results are fetched via API, not DOM scraping, for reliability
