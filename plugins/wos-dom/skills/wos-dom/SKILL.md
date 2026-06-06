# WoS (Web of Science) DOM & URL Reference

## Base URL

- Direct: `https://www.webofscience.com`
- Path pattern: `/wos/{db}/` where `{db}` is the database code

## Databases

| Database | URL Code | Description |
|----------|----------|-------------|
| Web of Science Core Collection | `woscc` | Default. SCI/SSCI/CPCI etc. |
| All Databases | `alldb` | All databases combined |
| Derwent Innovations Index | `diidw` | Patents |
| KCI-Korean Journal Database | `kci` | Korean journals |
| MEDLINE | `medline` | Biomedical literature |
| Preprint Citation Index | `pprn` | Preprints |
| ProQuest Dissertations & Theses | `pqdtglobal` | Dissertations |
| Research Commons | `rc` | Research Commons |
| SciELO Citation Index | `scielo` | Latin American journals |

### Editions (Core Collection only, path=`woscc`)

When database is `woscc`, the "Editions" dropdown allows filtering by index:

| Edition | Code | Coverage |
|---------|------|----------|
| Science Citation Index Expanded | SCI-EXPANDED | 1995-present |
| Social Sciences Citation Index | SSCI | 1995-present |
| Conference Proceedings - Science | CPCI-S | 1996-present |
| Conference Proceedings - SSH | CPCI-SSH | 1996-present |
| Current Chemical Reactions | CCR-EXPANDED | 1985-present |
| Index Chemicus | IC | 1993-present |

Default: All editions selected. Edition filtering requires form interaction (checkbox toggle), not URL-controllable.

## URL Patterns

### Search via URL (Recommended - no form interaction needed)

```
https://www.webofscience.com/wos/{db}/general-summary?queryJson={ENCODED_JSON}
```

Replace `{db}` with database code (default: `woscc`). Examples:
- Core Collection: `/wos/woscc/general-summary?queryJson=...`
- All Databases: `/wos/alldb/general-summary?queryJson=...`
- MEDLINE: `/wos/medline/general-summary?queryJson=...`

**queryJson format**:
```json
[{"rowBoolean":null,"rowField":"TS","rowText":"deep learning"}]
```

Multiple conditions:
```json
[
  {"rowBoolean":null,"rowField":"TS","rowText":"deep learning"},
  {"rowBoolean":"AND","rowField":"AU","rowText":"Hinton"},
  {"rowBoolean":"AND","rowField":"PY","rowText":"2020-2025"}
]
```

### Results Page (after search redirects)

```
/wos/woscc/summary/{session-uuid}/relevance/{page-number}
```

- `{page-number}` starts from 1
- Can change page by modifying the number in URL
- Sort: replace `relevance` with other sort options

### Full Record

```
/wos/woscc/full-record/WOS:{accession-number}
```

Example: `/wos/woscc/full-record/WOS:000779183600001`

### Citing Summary

```
/wos/woscc/citing-summary/WOS:{id}?from=woscc&type=colluid&eventMode=timeCitedOnSummary
```

### Cited References

```
/wos/woscc/cited-references-summary/WOS:{id}?type=colluid&from=woscc
```

### Related Records

```
/wos/woscc/related-records-summary/WOS:{id}?type=colluid&from=woscc
```

### Other Pages

- Smart Search: `/wos/woscc/smart-search`
- Fielded Search: `/wos/woscc/basic-search`
- Query Builder: `/wos/woscc/advanced-search`
- Cited References Search: `/wos/woscc/cited-reference-search`

## Global Identifier

**WoS Accession Number**: `WOS:000779183600001`
- Used in full-record URLs, citing/references URLs
- Extracted from title link href: `a[href*="full-record"]`

## Field Tags (for queryJson rowField)

| Tag | Field |
|-----|-------|
| TS | Topic (title + abstract + keywords) |
| TI | Title |
| AB | Abstract |
| AU | Author |
| AI | Author Identifiers |
| AK | Author Keywords |
| GP | Group Author |
| ED | Editor |
| KP | Keyword Plus |
| SO | Publication Titles |
| DO | DOI |
| PY | Year Published |
| CF | Conference |
| AD | Address |
| OG | Affiliation |
| OO | Organization |
| SG | Suborganization |
| CU | Country/Region |
| FO | Funding Agency |
| FG | Grant Number |
| SU | Research Area |
| WC | Web of Science Categories |
| IS | ISSN/ISBN |
| UT | Accession Number |
| PMID | PubMed ID |
| DOP | Publication Date |
| ALL | All Fields |

## CSS Selectors - Search Results Page

| Element | Selector |
|---------|----------|
| Record container | `app-record` |
| Title link | `a[data-ta="summary-record-title-link"]` |
| Author links | `a[data-ta^="SumAuthTa"]` (display names only: `a[data-ta*="DisplayName"]`) |
| Source/Journal | `a[data-ta="jcr-link-menu"]` or `.summary-source-title-link` |
| Conference | `a[data-ta="Summary-conferenceName"]` |
| Citation count | `a[data-ta="stat-number-citation-related-count"]` |
| Reference count | `a[data-ta="stat-number-references-count"]` |
| Related records | `a[data-ta="related-records-link"]` |
| Abstract snippet | `.abstract-size` or `span.abstract-size` |
| Record checkbox | `mat-checkbox` (within `app-record`) |
| Open Access badge | `img[alt="Open Access"]` |
| Full text link | `a[data-ta^="FRLinkTa"]` |
| Page number input | `spinbutton[aria-label*="Page Number"]` |
| Next page button | `button[data-ta="next-page-button"]` |
| Page count | StaticText after "of " (e.g., "2,000") |
| Sort selector | `button[data-ta="selectSortOption"]` |
| Page size selector | `button` containing "Page size" |
| Export button | `button` containing "Export" with `haspopup="menu"` |
| Select all checkbox | region `summaryRecordsTop` > `checkbox` |

### Record Data Extraction Pattern

Within each `app-record`:
- WoS ID: extracted from title link href (`/full-record/WOS:XXXXX`)
- Year: from date StaticText (e.g., "2014", "Nov 2022")
- Volume/Issue/Pages: from StaticText after source (e.g., "59", "(11)", ", pp.2251-2266")

## CSS Selectors - Full Record Page

**IMPORTANT**: Full record page uses different citation selectors than search results page.

| Element | Selector | Notes |
|---------|----------|-------|
| Title | `[data-ta="FullRTa-fullRecordtitle-0"]` | |
| Authors | `[data-ta^="SumAuthTa-DisplayName-author-en"]` | |
| Abstract | `div.abstract--instance` | |
| Source/Journal | h3 `[data-ta="FullRTa-sourceLabel"]` → parent span | Split on "arrow_back" to exclude JCR popup |
| DOI | `a[href*="doi.org"]` | |
| Metadata fields | h3 label → `parentElement` → non-h3 children | Volume, Issue, Page, Published, etc. |
| Author Keywords | h3 "Author Keywords" → `parentElement.querySelectorAll('a')` | NOT `nextElementSibling` |
| Keywords Plus | h3 "Keywords Plus" → `parentElement.querySelectorAll('a')` | Same pattern |
| **Citation (WOSCC)** | `a[data-ta*="times-cited-count-link-WOSCC"]` | Different from search results! |
| **Citation (All DB)** | `a[data-ta*="times-cited-count-link-ALLDB"]` | |
| **Reference count** | `a[data-ta*="refCountLink"]` | |
| JIF | Inside `app-jcr-sidenav` text | Regex: `/Impact Factor\s*™?\s*(\d{4})\s*([\d.]+)/` |
| JCR Quartile | Same text block | Regex: `/Category Quartile\s*(Q[1-4])/` |
| Full text links | `a[data-ta^="FRLinkTa"]` | |
| Export button | `button` containing "Export" with `haspopup="menu"` | |

### Citation Selector Differences (Search vs Full Record)

| Context | Citation Selector | Reference Selector |
|---------|-------------------|-------------------|
| Search results | `a[data-ta="stat-number-citation-related-count"]` | `a[data-ta="stat-number-references-count"]` |
| Full record | `a[data-ta*="times-cited-count-link-WOSCC"]` | `a[data-ta*="refCountLink"]` |

## Export Menu Items (from Export dropdown)

| menuitem | Format |
|----------|--------|
| "EndNote online" | EndNote online |
| "EndNote desktop" | .ciw file |
| "Plain text file" | .txt |
| "RefWorks" | RefWorks |
| "RIS (other reference software)" | .ris |
| "BibTeX" | .bib |
| "Excel" | .xlsx |
| "Tab delimited file" | .txt (tab) |
| "Printable HTML file" | .html |
| "InCites" | InCites |
| "Email" | Send via email |
| "Fast 5000" | Quick export up to 5000 records |

## Pagination

- 50 records per page (default, configurable)
- Max 2,000 pages viewable (100,000 records)
- Page navigation: change page number in URL or use next/prev buttons

## Internal API (Preferred over DOM scraping)

### Search API

**Endpoint**: `POST /api/wosnx/core/runQuerySearch?SID={SID}`

**SID** can be extracted from browser performance entries:
```javascript
performance.getEntriesByType('resource')
  .filter(r => r.name.includes('SID='))
  .map(r => r.name.match(/SID=([^&]+)/)?.[1])[0]
```

**Request body**:
```json
{
  "product": "WOSCC",
  "searchMode": "general",
  "viewType": "search",
  "serviceMode": "summary",
  "search": {
    "mode": "general",
    "database": "WOSCC",
    "query": [{"rowField": "TS", "rowText": "value co-creation"}],
    "editions": ["WOS.SSCI"]
  },
  "retrieve": {
    "count": 10,
    "history": true,
    "jcr": true,
    "sort": "times-cited-descending",
    "analyzes": [],
    "locale": "en"
  },
  "eventMode": null
}
```

**Edition codes**: `WOS.SCI`, `WOS.SSCI`, `WOS.CPCI-S`, `WOS.CPCI-SSH`, `WOS.CCR-EXPANDED`, `WOS.IC`

**Sort values**: `relevance`, `times-cited-descending`, `times-cited-ascending`, `date-descending`, `date-ascending`, `usage-count-last-180-days-descending`

**Response format**: NDJSON (newline-delimited JSON). Key lines:
- `{"key":"searchInfo","payload":{"RecordsFound":5462,...}}`
- `{"key":"records","payload":{"1":{record1},"2":{record2},...}}`

**Record structure** (from API response):
```
rec.colluid                              → WoS ID (e.g., "WOS:000298554300001")
rec.titles.item.en[0].title              → Paper title
rec.titles.source.en[0].title            → Journal name
rec.names.author.en[].wos_standard       → Author names
rec.pub_info.pubyear                     → Publication year
rec.pub_info.vol / issue / page_no       → Volume, issue, pages
rec.doi                                  → DOI
rec.citation_related.counts.WOSCC        → Citation count (Core Collection)
rec.citation_related.counts.ALLDB        → Citation count (All Databases)
rec.ref_count                            → Reference count
rec.abstract.basic.en.abstract           → Abstract (HTML, strip tags)
rec.doctypes[0]                          → Document type
rec.oa                                   → Open Access flag
```

### Other API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/api/wosnx/indic/records/getIndicators` | Citation indicators |
| `/api/wosnx/core/getHistory` | Search history |
| `/api/wosnx/core/markedList` | Marked list |
| `/api/esti/Personalization/preferences` | User preferences |
| `/api/esti/SearchEngine/search` | Alternative search endpoint |
