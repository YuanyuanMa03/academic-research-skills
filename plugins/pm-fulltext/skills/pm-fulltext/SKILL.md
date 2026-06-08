---
name: pm-fulltext
description: Find full-text download links for a PubMed paper by PMID - DOI, PMC open access, Sci-Hub, and publisher links. Use when user wants to read or download a paper's full text.
argument-hint: "[PMID]"
---

# PubMed Full Text Links

Resolve and present all full-text access options for a given PMID.

## Arguments

$ARGUMENTS is a PMID (PubMed ID, an integer like `35641793`).

## Steps

### 1. Navigate to the paper page

Use `mcp__chrome-devtools__navigate_page`:
- url: `https://pubmed.ncbi.nlm.nih.gov/{PMID}/`

### 2. Resolve full-text links (evaluate_script)

Replace `PMID_HERE` with the actual PMID from $ARGUMENTS:

```javascript
async () => {
  const pmid = "PMID_HERE";

  // Wait for page to load
  for (let i = 0; i < 20; i++) {
    if (document.querySelector('h1.heading-title')) break;
    await new Promise(r => setTimeout(r, 500));
  }

  // 1. Get DOI from esummary
  const sumResp = await fetch(
    `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=${pmid}&retmode=json`
  );
  const sumData = await sumResp.json();
  const record = sumData.result?.[pmid] || {};
  const doi = (record.articleids || []).find(a => a.idtype === 'doi')?.value || '';
  const title = record.title || '';

  // 2. Check PMC via elink
  const linkResp = await fetch(
    `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=pmc&id=${pmid}&retmode=json`
  );
  const linkData = await linkResp.json();
  const pmcLinks = linkData.linksets?.[0]?.linksetdbs?.find(l => l.linkname === 'pubmed_pmc')?.links || [];
  const pmcid = pmcLinks.length > 0 ? `PMC${pmcLinks[0]}` : '';

  // 3. Get publisher links from DOM
  const ftLinkEls = document.querySelectorAll('.full-text-links-list a');
  const publisherLinks = Array.from(ftLinkEls).map(a => ({
    text: a.textContent?.trim() || '',
    href: a.href || '',
    icon: a.querySelector('img')?.getAttribute('alt') || ''
  }));

  // 4. Check free full text availability from DOM
  const hasFreeFullText = !!document.querySelector('.free-full-text');

  // 5. Build access links
  const links = {};

  if (doi) {
    links.doi = `https://doi.org/${doi}`;
    links.scihub = `https://sci-hub.ru/${doi}`;
  }

  if (pmcid) {
    links.pmc = `https://www.ncbi.nlm.nih.gov/pmc/articles/${pmcid}/`;
    links.pmcPdf = `https://www.ncbi.nlm.nih.gov/pmc/articles/${pmcid}/pdf/`;
  }

  return {
    pmid,
    title,
    doi,
    pmcid,
    hasFreeFullText,
    publisherLinks,
    links
  };
}
```

### 3. Report

```
## Full Text Links — PMID: {pmid}

**{title}**

**DOI:**
{links.doi ? "- " + links.doi : "N/A"}

**Open Access (PMC):**
{links.pmc ? "- Full text: " + links.pmc : "No PMC full text available"}
{links.pmcPdf ? "- PDF: " + links.pmcPdf : ""}

**Sci-Hub:**
{links.scihub ? "- " + links.scihub : "Cannot build Sci-Hub link (no DOI)"}

**Publisher Links:**
{For each publisherLink: "- {text}: {href}"}
```

### 4. Open full text (optional)

If the user wants to read the paper immediately, use `mcp__chrome-devtools__new_page` to open the preferred link:
- PMC link (if available, free open access)
- Sci-Hub link (if DOI available)
- Publisher link (may require subscription)

## Notes

- This skill uses 2 tool calls: `navigate_page` + `evaluate_script`
- PMC (PubMed Central) articles are fully open access
- Sci-Hub link is constructed from DOI, not all papers have DOI
- Opening a full text page in a new tab adds 1 more tool call
