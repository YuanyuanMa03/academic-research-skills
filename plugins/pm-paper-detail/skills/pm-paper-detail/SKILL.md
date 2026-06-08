---
name: pm-paper-detail
description: Get full paper details for a PubMed article by PMID - title, authors with affiliations, abstract, MeSH terms, keywords, publication types, DOI, and citation info. Use when user needs detailed information about a specific paper.
argument-hint: "[PMID]"
---

# PubMed Paper Detail

Extract complete metadata from a PubMed paper using NCBI E-utilities efetch API (XML format).

## Arguments

$ARGUMENTS is a PMID (PubMed ID, an integer like `35641793`).

## Steps

### 1. Navigate to the paper page

Use `mcp__chrome-devtools__navigate_page`:
- url: `https://pubmed.ncbi.nlm.nih.gov/{PMID}/`

This shows the paper detail page to the user in the browser.

### 2. Extract full metadata via E-utilities (evaluate_script)

Replace `PMID_HERE` with the actual PMID from $ARGUMENTS:

```javascript
async () => {
  const pmid = "PMID_HERE";

  // efetch XML for full record (abstract, MeSH, authors with affiliations)
  const fetchResp = await fetch(
    `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=${pmid}&retmode=xml`
  );
  const xml = await fetchResp.text();
  const doc = new DOMParser().parseFromString(xml, 'text/xml');

  // Title
  const title = doc.querySelector('ArticleTitle')?.textContent || '';

  // Abstract (may have labeled sections like BACKGROUND, METHODS, etc.)
  const abstractParts = Array.from(doc.querySelectorAll('AbstractText')).map(el => {
    const label = el.getAttribute('Label');
    return label ? `**${label}**: ${el.textContent}` : el.textContent;
  });
  const abstract = abstractParts.join('\n\n') || '';

  // Authors with affiliations
  const authors = Array.from(doc.querySelectorAll('Author')).map(a => {
    const lastName = a.querySelector('LastName')?.textContent || '';
    const foreName = a.querySelector('ForeName')?.textContent || '';
    const initials = a.querySelector('Initials')?.textContent || '';
    const affiliations = Array.from(a.querySelectorAll('AffiliationInfo Affiliation'))
      .map(af => af.textContent);
    return {
      name: foreName ? `${lastName} ${foreName}` : `${lastName} ${initials}`,
      nameAbbr: `${lastName} ${initials}`,
      affiliations
    };
  });

  // MeSH terms
  const meshTerms = Array.from(doc.querySelectorAll('MeshHeading')).map(mh => {
    const descriptor = mh.querySelector('DescriptorName')?.textContent || '';
    const majorTopic = mh.querySelector('DescriptorName')?.getAttribute('MajorTopicYN') === 'Y';
    const qualifiers = Array.from(mh.querySelectorAll('QualifierName')).map(q => ({
      name: q.textContent,
      major: q.getAttribute('MajorTopicYN') === 'Y'
    }));
    return { descriptor, majorTopic, qualifiers };
  });

  // Keywords
  const keywords = Array.from(doc.querySelectorAll('Keyword')).map(k => k.textContent);

  // Publication types
  const pubTypes = Array.from(doc.querySelectorAll('PublicationType')).map(p => p.textContent);

  // Grant/funding
  const grants = Array.from(doc.querySelectorAll('Grant')).map(g => ({
    id: g.querySelector('GrantID')?.textContent || '',
    agency: g.querySelector('Agency')?.textContent || '',
    country: g.querySelector('Country')?.textContent || ''
  }));

  // IDs
  const doi = doc.querySelector('ArticleId[IdType="doi"]')?.textContent || '';
  const pmcid = doc.querySelector('ArticleId[IdType="pmc"]')?.textContent || '';

  // Journal info
  const journal = doc.querySelector('Journal Title')?.textContent
    || doc.querySelector('Title')?.textContent || '';
  const journalAbbr = doc.querySelector('ISOAbbreviation')?.textContent || '';
  const issn = doc.querySelector('ISSN')?.textContent || '';
  const volume = doc.querySelector('Volume')?.textContent || '';
  const issue = doc.querySelector('Issue')?.textContent || '';
  const pages = doc.querySelector('MedlinePgn')?.textContent || '';

  // Publication date
  const pubDateEl = doc.querySelector('PubDate');
  const year = pubDateEl?.querySelector('Year')?.textContent || '';
  const month = pubDateEl?.querySelector('Month')?.textContent || '';
  const day = pubDateEl?.querySelector('Day')?.textContent || '';
  const medlineDate = pubDateEl?.querySelector('MedlineDate')?.textContent || '';
  const pubDate = medlineDate || [year, month, day].filter(Boolean).join(' ');

  // Language
  const language = doc.querySelector('Language')?.textContent || '';

  return {
    pmid, title, abstract, authors,
    meshTerms, keywords, pubTypes, grants,
    doi, pmcid, journal, journalAbbr, issn,
    volume, issue, pages, pubDate, language
  };
}
```

### 3. Format and present

```
## {title}

**PMID:** {pmid} | **DOI:** {doi} | **PMCID:** {pmcid || "N/A"}
**Journal:** {journal} ({journalAbbr}) | ISSN: {issn}
**Citation:** {pubDate}; {volume}({issue}):{pages}
**Language:** {language}
**Type:** {pubTypes joined by ", "}

**Authors:**
{For each author: "- {name} — {affiliations joined by '; '}"}

**Abstract:**
{abstract}

**MeSH Terms:**
{For each mesh: "- {descriptor}{majorTopic ? ' *' : ''}{qualifiers ? ' / ' + qualifiers.map(q => q.name).join(', ') : ''}"}

**Keywords:** {keywords joined by ", "}

**Funding:**
{For each grant: "- {agency} ({id})"}
```

### 4. Follow-up

- **Full text**: use `pm-fulltext` with the PMID
- **Export to Zotero**: use `pm-export` with the PMID

## Notes

- This skill uses 2 tool calls: `navigate_page` + `evaluate_script`
- E-utilities efetch XML provides the most complete metadata including structured abstracts, MeSH with major topic flags, and author affiliations
- The navigate_page step lets the user see the paper in the browser while the API fetches structured data
