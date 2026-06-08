---
name: pm-navigate-pages
description: Navigate PubMed search result pages or change sort order. Use when user wants to see more results or change ordering.
argument-hint: "[next|previous|page N|sort by date|relevance]"
user-invokable: false
---

# PubMed Navigate Pages & Sort

Navigate search result pages or change sort order. Requires a previous pm-search call to know the current query, page, and size.

## Arguments

$ARGUMENTS can be:
- `next` — go to next page
- `previous` — go to previous page
- `page N` — go to page N
- `sort by date` — sort by most recent
- `sort by relevance` — sort by best match (default)

## Prerequisites

This skill requires context from a previous `pm-search` call:
- `query`: the search term
- `page`: current page number
- `size`: results per page
- `total`: total results count

## Steps

### 1. Calculate new parameters

Based on $ARGUMENTS:
- `next`: newPage = currentPage + 1
- `previous`: newPage = max(1, currentPage - 1)
- `page N`: newPage = N
- `sort by date`: sort = "date", newPage = 1
- `sort by relevance`: sort = "relevance", newPage = 1

Compute: `retstart = (newPage - 1) * size`

### 2. Navigate to updated URL

Use `mcp__chrome-devtools__navigate_page`:
- url: `https://pubmed.ncbi.nlm.nih.gov/?term={URL_ENCODED_QUERY}&size={size}&page={newPage}`

### 3. Fetch results (evaluate_script)

Same pattern as pm-search step 2, with updated `retstart` and `sort`:

```javascript
async () => {
  const query = "PREVIOUS_QUERY";
  const page = NEW_PAGE;
  const size = CURRENT_SIZE;
  const sort = "SORT_VALUE";
  const retstart = (page - 1) * size;

  const searchResp = await fetch(
    `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=${encodeURIComponent(query)}&retmax=${size}&retstart=${retstart}&retmode=json&sort=${sort}`
  );
  const searchData = await searchResp.json();
  const ids = searchData.esearchresult?.idlist || [];
  const total = parseInt(searchData.esearchresult?.count || '0');

  if (ids.length === 0) return { query, total, page, results: [] };

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
      doi,
      pubtype: (r.pubtype || []).join(', ')
    };
  });

  const totalPages = Math.ceil(total / size);
  return { query, total, page, totalPages, size, sort, results };
}
```

### 4. Report

```
Page {page} of {totalPages} for "{query}" ({total} total results, sorted by {sort}):

1. {title}
   PMID: {pmid} | DOI: {doi}
   Authors: {authors}
   Journal: {journal} ({pubdate})

2. ...
```

## Notes

- This skill uses 2 tool calls: `navigate_page` + `evaluate_script`
- If already on PubMed page, can skip navigate_page and use only evaluate_script (1 tool call)
