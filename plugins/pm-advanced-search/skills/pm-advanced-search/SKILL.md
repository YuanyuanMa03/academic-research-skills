---
name: pm-advanced-search
description: Perform advanced PubMed search with field qualifiers - author, title, journal, MeSH, date range, article type. Constructs proper PubMed query syntax from natural language. Use for precise filtered searches.
argument-hint: "[describe search criteria in natural language]"
---

# PubMed Advanced Search

Construct and execute a PubMed query using field qualifiers, boolean operators, and filters based on the user's natural language description.

## Arguments

$ARGUMENTS is a natural language description of the search criteria, e.g.:
- "搜索 Zhang Wei 在 Nature 上发表的关于 CRISPR 的综述"
- "Find reviews about CAR-T therapy published after 2020 with IF>10"
- "Search for clinical trials on COVID-19 vaccines in 2023-2024"

## Step 1: Parse search criteria into PubMed query syntax

Map the user's intent to PubMed field tags:

| Field | Tag | Example |
|-------|-----|---------|
| Author | `[AU]` | `Zhang W[AU]` |
| First Author | `[1AU]` | `Smith J[1AU]` |
| Title words | `[TI]` | `CRISPR[TI]` |
| Title/Abstract | `[TIAB]` | `machine learning[TIAB]` |
| Journal | `[TA]` | `Nature[TA]` |
| MeSH term | `[MESH]` | `Neoplasms[MESH]` |
| Date range | `[DP]` | `2020/01:2025/12[DP]` |
| Publication type | `[PT]` | `Review[PT]`, `Clinical Trial[PT]`, `Meta-Analysis[PT]`, `Systematic Review[PT]`, `Randomized Controlled Trial[PT]` |
| Affiliation | `[AD]` | `Harvard[AD]` |
| Language | `[LA]` | `English[LA]` |
| All fields | `[ALL]` | `cancer[ALL]` |

Boolean operators: `AND`, `OR`, `NOT` (must be uppercase).

**Examples:**
- "Zhang Wei 在 Nature 上的 CRISPR 综述" → `Zhang W[AU] AND CRISPR[TI] AND Nature[TA] AND Review[PT]`
- "2020年以后关于 COVID-19 疫苗的临床试验" → `COVID-19 vaccine[TIAB] AND Clinical Trial[PT] AND 2020:2026[DP]`
- "IF>10 的癌症免疫治疗系统综述" → `cancer immunotherapy[TIAB] AND Systematic Review[PT]`

**Note:** PubMed does not have a built-in impact factor filter. For IF filtering, search first and then the user can check journal IF manually.

## Step 2: Navigate

Use `mcp__chrome-devtools__navigate_page`:
- url: `https://pubmed.ncbi.nlm.nih.gov/?term={URL_ENCODED_QUERY}&size=20`

Replace `{URL_ENCODED_QUERY}` with the constructed query string, URL-encoded.

## Step 3: Search + extract (evaluate_script)

Same pattern as pm-search, using the constructed query:

```javascript
async () => {
  const query = "CONSTRUCTED_QUERY";
  const page = 1, size = 20;
  const retstart = (page - 1) * size;

  const searchResp = await fetch(
    `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=${encodeURIComponent(query)}&retmax=${size}&retstart=${retstart}&retmode=json&sort=relevance`
  );
  const searchData = await searchResp.json();
  const ids = searchData.esearchresult?.idlist || [];
  const total = parseInt(searchData.esearchresult?.count || '0');
  const queryTranslation = searchData.esearchresult?.querytranslation || '';

  if (ids.length === 0) return { query, queryTranslation, total: 0, results: [] };

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

  return { query, queryTranslation, total, page, size, results };
}
```

## Step 4: Report

```
Advanced search: {query}
PubMed translated query: {queryTranslation}
Found {total} results (page {page}):

1. {title}
   PMID: {pmid} | DOI: {doi}
   Authors: {authors}
   Journal: {journal} ({pubdate}) | Type: {pubtype}

2. ...
```

Always show the `queryTranslation` so the user can see how PubMed interpreted the query.

## Common Publication Types

| Chinese | English | PubMed tag |
|---------|---------|------------|
| 综述 | Review | `Review[PT]` |
| 系统综述 | Systematic Review | `Systematic Review[PT]` |
| Meta分析 | Meta-Analysis | `Meta-Analysis[PT]` |
| 临床试验 | Clinical Trial | `Clinical Trial[PT]` |
| 随机对照试验 | RCT | `Randomized Controlled Trial[PT]` |
| 病例报告 | Case Report | `Case Reports[PT]` |

## Notes

- This skill uses 2 tool calls: `navigate_page` + `evaluate_script`
- The key difference from pm-search is query construction — this skill translates natural language to PubMed syntax
- `queryTranslation` in the response shows how PubMed actually interprets the query (MeSH expansion, etc.)
