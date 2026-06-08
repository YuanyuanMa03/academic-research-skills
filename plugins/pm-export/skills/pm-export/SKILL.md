---
name: pm-export
description: Export PubMed paper(s) to Zotero or save as RIS file. Supports single paper by PMID or batch export from search results. Use when user wants to save papers to their reference manager.
argument-hint: "[PMID or space-separated PMIDs]"
---

# PubMed Export to Zotero

Export PubMed paper citation data and push to Zotero desktop via local Connector API, or generate MEDLINE/RIS format.

## Arguments

$ARGUMENTS contains one or more PMIDs (space-separated), e.g.:
- `35641793` — single paper
- `35641793 27741350 35362092` — batch export

## Steps

### Step 1: Fetch paper metadata (evaluate_script)

Use `mcp__chrome-devtools__evaluate_script` on any PubMed page. Replace PMID_LIST with the actual PMIDs:

```javascript
async () => {
  const pmids = "PMID_LIST".split(/[\s,]+/).filter(Boolean);

  // Batch esummary for basic metadata
  const sumResp = await fetch(
    `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=${pmids.join(',')}&retmode=json`
  );
  const sumData = await sumResp.json();

  // efetch XML for full records (abstracts, keywords)
  const fetchResp = await fetch(
    `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=${pmids.join(',')}&retmode=xml`
  );
  const xml = await fetchResp.text();
  const xmlDoc = new DOMParser().parseFromString(xml, 'text/xml');

  const papers = pmids.map(pmid => {
    const r = sumData.result?.[pmid] || {};
    const doi = (r.articleids || []).find(a => a.idtype === 'doi')?.value || '';

    // Find this paper's article in the XML
    const articles = xmlDoc.querySelectorAll('PubmedArticle');
    let abstract = '', keywords = [], meshTerms = [], pubTypes = [];
    let issn = '', pmcid = '';
    for (const art of articles) {
      if (art.querySelector('PMID')?.textContent === pmid) {
        abstract = Array.from(art.querySelectorAll('AbstractText'))
          .map(el => el.textContent).join(' ');
        keywords = Array.from(art.querySelectorAll('Keyword'))
          .map(k => k.textContent);
        meshTerms = Array.from(art.querySelectorAll('MeshHeading DescriptorName'))
          .map(d => d.textContent);
        pubTypes = Array.from(art.querySelectorAll('PublicationType'))
          .map(p => p.textContent);
        issn = art.querySelector('ISSN')?.textContent || '';
        pmcid = art.querySelector('ArticleId[IdType="pmc"]')?.textContent || '';
        break;
      }
    }

    return {
      pmid,
      title: r.title || '',
      authors: (r.authors || []).map(a => ({
        lastName: a.name?.split(' ')[0] || '',
        firstName: a.name?.split(' ').slice(1).join(' ') || '',
      })),
      journal: r.fulljournalname || '',
      journalAbbr: r.source || '',
      pubdate: r.pubdate || '',
      volume: r.volume || '',
      issue: r.issue || '',
      pages: r.pages || '',
      doi,
      issn,
      pmcid,
      abstract,
      keywords,
      pubtype: pubTypes,
      language: (r.lang || ['eng'])[0] === 'eng' ? 'en' : (r.lang || ['eng'])[0]
    };
  });

  return papers;
}
```

### Step 2: Push to Zotero

Save the returned JSON array to a temp file, then run the Python script:

```bash
python {SKILL_DIR}/scripts/push_to_zotero.py /tmp/pm_papers.json
```

The Python script runs a 3-step flow:
1. **saveItems** — saves metadata to Zotero (`POST /connector/saveItems`). Note: Zotero 7.x ignores the `attachments` field in saveItems.
2. **download_pdf** — downloads PDF binary via Python urllib (if `pdfUrl` or `pmcid` is available)
3. **saveAttachment** — uploads PDF binary to Zotero (`POST /connector/saveAttachment`), linked to the parent item via `parentItemID` in the `X-Metadata` header

Other details:
- Builds Zotero-compatible item JSON (`itemType: journalArticle`, `libraryCatalog: PubMed`)
- Parses PubMed author format into Zotero's `{firstName, lastName}` structure
- Sets DOI, PMID (in extra field), URL to PubMed page
- Uses deterministic session ID for idempotency (same papers → same session → no duplicates)
- PDF download may fail for some publishers (403, JS-redirect pages); these are reported as "PDF skip"

### Step 3: Report

Single paper:
```
Exported to Zotero:
  Title: {title}
  Authors: {authors}
  Journal: {journal} ({pubdate})
  DOI: {doi}
  PMID: {pmid}
```

Batch:
```
Exported {count} papers to Zotero:
  1. {title1} ({journal1}, {pubdate1})
  2. {title2} ({journal2}, {pubdate2})
  ...
```

## MEDLINE Export (alternative)

If the user wants a file instead of Zotero, use efetch to get MEDLINE format directly:

```javascript
async () => {
  const pmids = "PMID_LIST";
  const resp = await fetch(
    `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=${pmids}&rettype=medline&retmode=text`
  );
  return await resp.text();
}
```

Save the returned text as a `.nbib` file. This can be imported into Zotero, EndNote, or any reference manager.

## Zotero Troubleshooting

- **Zotero not running**: Script returns "Zotero is not running". User must start Zotero desktop.
- **Read-only library**: Script returns "Target library is read-only". User must select a writable collection.
- **Already saved**: Script returns 409, treated as success (idempotent).

## Notes

- This skill uses 2 tool calls: `evaluate_script` + `bash python`
- Batch export works for any number of PMIDs in a single call
- The Python script is at `{SKILL_DIR}/scripts/push_to_zotero.py`
- Zotero must be running with the Connector API on localhost:23119
