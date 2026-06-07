# Workflow 2: Citation Verification

**Purpose:** Verify references in a document (.docx / .tex / .txt) against databases.

**Uses:**
- [Citation Parser](../citation-parser.md) — extraction strategies per source format.
- [Dedup Engine](../dedup-engine.md) — collapse duplicate candidate matches before classification.

## Procedure

1. **Extract citations** from document using [Citation Parser](../citation-parser.md).
   Prefer T1 sources for primary verification (CrossRef DOI lookup → PubMed PMID confirmation). Use T2 (Semantic Scholar) for cross-checking ambiguous or missing results. See [Source Tiers](../source-tiers.md) for full routing.
2. **Resolve each citation:**
   - DOI → `get_paper_by_id(id="doi:10.xxxx/...")`
   - PMID → `get_paper_by_id(id="pmid:12345")`
   - arXiv ID → `get_paper_by_id(id="arxiv:2301.12345")`
   - Title + first author → `search_papers(query="title first_author", sources=["crossref", "pubmed"])`
3. **Compare** retrieved metadata vs. document metadata (title, journal, year).
4. **Classify** into: `verified` | `mismatch` | `not_found` | `suspicious` | `manual_needed`.
   See [Citation Parser: Classification Labels](../citation-parser.md#classification-labels) for criteria.
5. **Generate report:**
   - Summary: total / verified / mismatched / not_found / suspicious / manual_needed counts.
   - Detail table: each reference with status, DOI/PMID, resolution notes.

## Error Modes

- **Unsupported document format:** report and request .docx, .tex, or .txt.
- **All references manual_needed:** document may lack identifiers; suggest adding DOIs or PMIDs to the manuscript.
- **MCP tools partially unavailable:** flag affected references as `manual_needed`.
