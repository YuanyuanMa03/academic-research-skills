---
name: ieee-advanced-search
description: Performs advanced search on IEEE Xplore with filters like author, title, publication, year, DOI. Use when the user wants filtered academic paper search.
argument-hint: "[search terms and filters]"
---

# IEEE Xplore Advanced Search

Perform a filtered search on IEEE Xplore using command search syntax via URL parameters.

## Command Search Syntax

IEEE Xplore supports boolean command search via the `queryText` parameter with `matchBoolean=true`. Field names are enclosed in double quotes.

### Available Fields

| Field | Syntax | Example |
|-------|--------|---------|
| All Metadata | `"All Metadata":term` | `"All Metadata":deep learning` |
| Document Title | `"Document Title":term` | `"Document Title":transformer` |
| Authors | `"Authors":name` | `"Authors":Hinton` |
| Author Affiliations | `"Author Affiliations":org` | `"Author Affiliations":MIT` |
| Publication Title | `"Publication Title":name` | `"Publication Title":IEEE Access` |
| Abstract | `"Abstract":term` | `"Abstract":neural network` |
| Index Terms | `"Index Terms":term` | `"Index Terms":convolutional` |
| Author Keywords | `"Author Keywords":term` | `"Author Keywords":federated learning` |
| IEEE Terms | `"IEEE Terms":term` | `"IEEE Terms":machine learning` |
| DOI | `"DOI":value` | `"DOI":10.1109/TPAMI.2024.1234567` |
| ISSN | `"ISSN":value` | `"ISSN":0162-8828` |
| ISBN | `"ISBN":value` | `"ISBN":978-1-7281-1234-5` |
| Article Number | `"Article Number":value` | `"Article Number":8876906` |
| Funding Agency | `"Funding Agency":name` | `"Funding Agency":NSF` |
| ORCID | `"ORCID":value` | `"ORCID":0000-0001-2345-6789` |

### Boolean Operators

Fields can be combined with `AND`, `OR`, `NOT`:
```
("Document Title":deep learning AND "Authors":LeCun)
("Abstract":transformer OR "Abstract":attention) AND "Authors":Vaswani
```

### Year Range

Use `ranges` parameter for year filtering:
```
ranges=2020_2025_Year
```

### Content Type Filter

Use `contentType` parameter:
```
contentType=conferences        # Conference papers only
contentType=periodicals        # Journal/magazine articles only
contentType=standards          # Standards only
contentType=books              # Books only
```

## Steps

### Step 1: Parse user intent

From `$ARGUMENTS`, identify which fields the user wants to filter on. Map natural language to command search syntax:
- "by author X" → `"Authors":X`
- "in journal Y" → `"Publication Title":Y`
- "titled ..." → `"Document Title":...`
- "about topic Z" → `"All Metadata":Z`
- "from 2020 to 2025" → `ranges=2020_2025_Year`
- "conference papers" → `contentType=conferences`
- "DOI 10.1109/..." → `"DOI":10.1109/...`

### Step 2: Build and navigate to URL

Construct URL:
```
{BASE_URL}/search/searchresult.jsp?action=search&matchBoolean=true&queryText={BOOLEAN_QUERY}&highlight=true&returnType=SEARCH&matchPubs=true&rowsPerPage=25&pageNumber=1&ranges={YEAR_RANGE}&contentType={TYPE}
```

Use `navigate_page` with `initScript`:
```
initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
```

### Step 3: Check access

- If the page shows a captcha or bot challenge: tell the user "请在浏览器中完成验证后告知我。"
- If redirected away from IEEE Xplore: tell the user "页面被重定向，请在浏览器中完成登录或认证后告知我。"

### Step 4: Extract results

Use `evaluate_script` with built-in waiting (same as `ieee-search`). Do NOT use `wait_for`.

```javascript
async () => {
  for (let i = 0; i < 30; i++) {
    if (document.querySelectorAll('.List-results-items .result-item').length > 0 ||
        document.querySelector('.Dashboard-header span')) break;
    await new Promise(r => setTimeout(r, 500));
  }

  const items = document.querySelectorAll('.List-results-items .result-item');
  const papers = [];

  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    const titleLink = item.querySelector('h3 a[href*="/document/"]');
    const authors = [...item.querySelectorAll('.author a[href*="/author/"]')].map(a => a.textContent.trim());
    const pubLink = item.querySelector('.description a[href*="/xpl/"]');
    const publisherInfo = item.querySelector('.publisher-info-container');
    const infoText = publisherInfo?.textContent?.trim() || '';
    const yearMatch = infoText.match(/Year:\s*(\d{4})/);
    const docNumber = titleLink?.href?.match(/\/document\/(\d+)/)?.[1] || '';
    const itemText = item.textContent || '';
    const citedByMatch = itemText.match(/Cited by:.*?(\d+)/);
    const citedBy = citedByMatch ? citedByMatch[1] : '';

    papers.push({
      rank: i + 1,
      title: titleLink?.textContent?.trim()?.replace(/<[^>]+>/g, '') || '',
      arnumber: docNumber,
      authors,
      publication: pubLink?.textContent?.trim() || '',
      year: yearMatch ? yearMatch[1] : '',
      info: infoText,
      citedBy,
    });
  }

  const resultCount = document.querySelector('.Dashboard-header span')?.textContent?.trim() || '';
  return { papers, resultCount };
}
```

### Step 5: Present results

Show applied filters at the top, then same format as ieee-search:

```
Search filters: {applied filters}
{resultCount}

1. {title} ...
```

## Examples

```
# Author + keyword
/ieee-advanced-search author: LeCun deep learning

# Journal + year range
/ieee-advanced-search in IEEE TPAMI from 2020 to 2025 attention mechanism

# Conference papers about transformers
/ieee-advanced-search conference papers about vision transformer 2023-2025
```

## Tested Boolean Query Examples (Proven Effective)

These queries were tested in production and returned precise, relevant results:

| Query | Results | Topic |
|-------|---------|-------|
| `("dc bias" AND "transformer" AND "HVDC")` | 159 | HVDC DC bias on transformers |
| `("temporary overvoltage" AND "HVDC")` | 26 | HVDC TOV |
| `("coupling capacitor" AND "capacitor voltage")` | 89 | CCVT / coupling capacitor papers |
| `("drain coil" OR "line trap") AND ("power line carrier" OR "PLC" OR "coupling")` | 32 | PLC line traps |
| `("thermal aging" OR "thermal ageing") AND ("electrical insulation") AND ("IEC 60085" OR "thermal class")` | 27 | Insulation thermal classification |

### Common Pitfalls to Avoid

| Pitfall | Bad Query | Problem | Fix |
|---------|-----------|---------|-----|
| **OR between different concepts** | `"coupling capacitor" OR "power line carrier"` | 12,835 results — each phrase matches independently | Use AND: `"coupling capacitor" AND "power line carrier"` |
| **Unquoted multi-word phrases** | `coupling capacitor power line carrier` | Each word is a separate OR token | Quote: `"coupling capacitor" "power line carrier"` |
| **Too generic abbreviations** | `"CVT" AND "insulation"` | CVT = Continuously Variable Transmission in automotive | Add domain: `"capacitor voltage transformer" AND "insulation"` |
| **IEC standard numbers** | `"IEC 60358-2"` | 0 results — IEEE Xplore doesn't index IEC numbers | Search by topic instead |

## Notes

- URL parameter approach avoids form filling, keeping operations to 2 tool calls.
- All parameters are optional and combinable.
- If the user provides a DOI or article number, consider using `ieee-paper-detail` instead.
- **Standards-specific search tip**: Use `contentType=standards` to filter for IEEE/ANSI standards only. IEEE Xplore does NOT host IEC/ISO standards — use `ieee-standards-search` for IEEE SA website, or direct users to IEC Webstore for IEC originals.
- When searching for IEC-related content, search by **technical topic** rather than IEC standard number (e.g. `"coupling capacitor" "power line carrier"` instead of `"IEC 60358"`).
