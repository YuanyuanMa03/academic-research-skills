# Workflow 5: Reference Management

**Purpose:** Manage and enrich reference collections.

**Uses:** [Dedup Engine](../dedup-engine.md) — for 5a (related papers overlap).

## 5a. Find Related Papers

1. Fetch source paper metadata via `get_paper_by_id(id="doi:..." or "pmid:...")`.
2. Search for related articles via `search_papers(query="<key terms from source paper>", sources=["pubmed", "crossref"])`.
3. Filter by relevance, date, or journal.
4. Deduplicate against source using [Dedup Engine](../dedup-engine.md).
5. Present with context notes.

## 5b. BibTeX Generation

1. DOI → `get_citation(doi="10.xxxx/...", style="bibtex")`.
2. PMID → `get_paper_by_id(id="pmid:...")` → format as BibTeX.
3. Batch: process multiple IDs via `scripts/format-converter.py`.
4. Clean: deduplicate by citation key, sort, validate required fields.
   See [BibTeX Format](../ris-bibtex-format.md#bibtex-format) for field requirements.

## 5c. ID Conversion

1. Accept DOI, PMID, or PMCID (up to 50).
2. Use `get_paper_by_id` to resolve each ID — the returned metadata includes all alternate IDs (DOI ↔ PMID ↔ PMCID).
3. Fetch metadata for newly resolved IDs via `get_paper_by_id`.

## 5d. Citation Formatting

1. Accept DOIs or PMIDs.
2. Use `get_citation(doi="...", style="apa"|"mla"|"bibtex"|"ris")` for formatted output.

## 5e. Full-Text Access

1. For articles with PMC copies, use `get_paper_by_id` to retrieve metadata, then access via PMC URL.
2. Fall back to `scripts/format-converter.py` for download assistance.
3. Report: structured text / PDF-as-text / metadata-only.
