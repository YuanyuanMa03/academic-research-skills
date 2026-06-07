# Search Results Report Template

## Standard Output Contract

All search skills should produce output in the following format:

```
Found {count} results for "{query}" on {platform}:

1. **{title}**
   Authors: {authors}
   Journal: {journal} ({year})
   Citations: {citation_count}
   DOI: {doi}
   {platform_url}

2. ...

---
Search completed in {tool_calls} tool calls.
```

## Required Fields

| Field | Description | Fallback |
|-------|-------------|----------|
| `title` | Paper title | "(Untitled)" |
| `authors` | Comma-separated author list | "(Unknown)" |
| `journal` | Publication venue | "(Unknown)" |
| `year` | Publication year | "(n.d.)" |
| `citation_count` | Number of citations | "N/A" |
| `doi` | Digital Object Identifier | "N/A" |
| `platform_url` | Link to paper on source platform | "(no link)" |

## Optional Fields (platform-specific)

| Field | Platforms | Description |
|-------|-----------|-------------|
| `downloads` | CNKI | Download count |
| `jif` | WoS | Journal Impact Factor |
| `jcr_quartile` | WoS | JCR quartile ranking |
| `pmid` | GS/PubMed | PubMed ID |
| `data_cid` | GS | Google Scholar internal ID |
| `accession_number` | WoS | WoS unique identifier |
| `dbcode` | CNKI | CNKI database code |
| `fulltext_url` | All | Direct PDF link |

## Batch Summary Format

When searching across multiple pages or combining results:

```
Aggregated {total} results across {pages} pages:
  Page 1: {count_1} results
  Page 2: {count_2} results
  ...
Duplicates removed: {dupes}
Final count: {final}
```
