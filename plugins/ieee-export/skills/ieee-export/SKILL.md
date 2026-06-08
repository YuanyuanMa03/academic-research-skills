---
name: ieee-export
description: Exports citations from IEEE Xplore in RIS, BibTeX, or plain text format. Supports pushing to Zotero. Use when the user wants to export or save citation data for papers.
argument-hint: "[article number(s)] [format: ris|bibtex|text] [zotero]"
---

# IEEE Xplore Citation Export

Export article citations from IEEE Xplore. Supports Plain Text, BibTeX, RIS, RefWorks formats, and Zotero push.

## Single Article Export (from Document Page)

### Step 1: Navigate to article page (if needed)

If not already on the article page:

```
navigate_page({
  url: "{BASE_URL}/document/{ARNUMBER}/",
  initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
})
```

### Step 2: Open "Cite This" modal and extract citation

Click the "Cite This" button, select the desired format tab, and extract the citation text:

```javascript
async (format) => {
  // format: 'text', 'bibtex', 'ris', 'refworks'
  // Wait for page to load
  for (let i = 0; i < 20; i++) {
    if (document.querySelector('.document-title')) break;
    await new Promise(r => setTimeout(r, 500));
  }

  // Click "Cite This" button
  const citeBtn = [...document.querySelectorAll('button')].find(b => b.textContent.trim() === 'Cite This');
  if (!citeBtn) return { error: 'Cite This button not found.' };
  citeBtn.click();

  // Wait for modal to appear
  await new Promise(r => setTimeout(r, 1500));

  // Map format to tab name
  const tabMap = {
    'text': 'Plain Text',
    'bibtex': 'BibTeX',
    'ris': 'RIS',
    'refworks': 'Refworks'
  };
  const tabName = tabMap[format] || 'BibTeX';

  // Click the desired format tab
  const tab = [...document.querySelectorAll('.cite-this-container a')].find(a => a.textContent.trim() === tabName);
  if (tab) tab.click();

  // Wait for content to load
  await new Promise(r => setTimeout(r, 1000));

  // Extract citation text
  const citeContent = document.querySelector('.cite-this-container .ql-editor') ||
                      document.querySelector('.cite-this-container [xplmathjax]') ||
                      document.querySelector('.cite-this-container pre');
  const citationText = citeContent?.textContent?.trim() || '';

  // Get article info for metadata
  const title = document.querySelector('.document-title span')?.textContent?.trim() || '';
  const arnumber = window.location.pathname.match(/\/document\/(\d+)/)?.[1] || '';

  // Close modal
  const closeBtn = document.querySelector('.cite-this-container .fa-times') ||
                   document.querySelector('.modal .close');
  if (closeBtn) closeBtn.click();

  return { citationText, format: tabName, title, arnumber };
}
```

### Step 3: Save or push citation

**Save to file**: Write the citation text to a local file using the appropriate extension (`.bib`, `.ris`, `.txt`).

**Push to Zotero**: See Zotero section below.

## Batch Export (from Search Results)

### Step 1: On search results page, select articles and open Export modal

```javascript
async (arnumbers) => {
  // Select articles
  const items = document.querySelectorAll('.List-results-items .result-item');
  let selected = 0;
  items.forEach(item => {
    const titleLink = item.querySelector('h3 a[href*="/document/"]');
    const docNum = titleLink?.href?.match(/\/document\/(\d+)/)?.[1] || '';
    if (arnumbers.includes(docNum)) {
      const checkbox = item.querySelector('input[type="checkbox"]');
      if (checkbox && !checkbox.checked) {
        checkbox.click();
        selected++;
      }
    }
  });

  // Click Export button — it's a button with class xpl-btn-primary and text "Export"
  // Note: The button exists in the results-actions bar, NOT inside a dropdown
  const exportBtn = [...document.querySelectorAll('button.xpl-btn-primary, button')]
    .find(b => b.textContent.trim() === 'Export');
  if (!exportBtn) return { error: 'Export button not found. Make sure you are on a search results page.' };

  // Must select at least one article before Export works
  if (selected === 0) {
    return { error: 'No articles selected. Select articles first, then export.' };
  }

  exportBtn.click();

  await new Promise(r => setTimeout(r, 2000));

  return { selected, message: 'Export modal opened. Proceed with format selection.' };
}
```

### Step 2: Select Citations tab and download

```javascript
async (format) => {
  // Click Citations tab in export modal
  const citationsTab = [...document.querySelectorAll('.nav-link')].find(a => a.textContent.trim() === 'Citations');
  if (citationsTab) citationsTab.click();

  await new Promise(r => setTimeout(r, 1000));

  // Select format radio button
  // IMPORTANT: Radio buttons are DISABLED until articles are selected in the Results tab first.
  // If radios are disabled, switch to Results tab, select articles, then come back to Citations tab.
  const formatMap = {
    'text': 'download-ascii',
    'bibtex': 'download-bibtex',
    'ris': 'download-ris',
    'refworks': 'download-refworks'
  };
  const labelFor = formatMap[format] || 'download-bibtex';

  // Find the radio by label text as fallback since for= attribute may not match id
  const allLabels = document.querySelectorAll('.export-form label, .tab-pane.active label');
  const targetLabel = [...allLabels].find(l => l.getAttribute('for') === labelFor ||
    l.textContent.trim().toLowerCase().includes(format));
  const radio = targetLabel?.querySelector('input[type="radio"]');

  if (radio) {
    if (radio.disabled) {
      return { error: 'Format radio buttons are disabled. Articles must be selected first. Use Step 1 to select articles before exporting citations.' };
    }
    radio.click();
  }

  // Select "Citation and Abstract" option
  const citAbsLabel = [...allLabels].find(l => l.getAttribute('for') === 'citation-abstract' ||
    l.textContent.trim().includes('Citation and Abstract'));
  const citAbsRadio = citAbsLabel?.querySelector('input[type="radio"]');
  if (citAbsRadio && !citAbsRadio.disabled) citAbsRadio.click();

  await new Promise(r => setTimeout(r, 500));

  // Click Download button
  const downloadBtn = [...document.querySelectorAll('.tab-pane.active button, .modal button')].find(b =>
    b.textContent.trim().includes('Download') && !b.textContent.trim().includes('Cancel')
  );
  if (downloadBtn) {
    downloadBtn.click();
    return { success: true, format };
  }

  return { error: 'Download button not found in export panel.' };
}
```

## Zotero Push

To push citations to a locally running Zotero instance. Two modes are supported:

**Prerequisites**: Zotero desktop must be running with the Connector API enabled (default on port 23119).

### Mode 1: RIS import (simple, no PDF)

After extracting RIS citation text from the Cite This modal:

```bash
python scripts/push_to_zotero.py --ris-data "{RIS_CONTENT}"
```

Or save to a file first and import:

```bash
python scripts/push_to_zotero.py --ris-file "{RIS_FILE_PATH}"
```

### Mode 2: JSON import (structured data with optional PDF attachment)

Save paper data as a JSON file, then run:

```bash
python scripts/push_to_zotero.py --json "{JSON_FILE_PATH}"
```

**JSON format** (single paper or array):

```json
{
  "title": "Paper Title",
  "authors": ["Author One", "Author Two"],
  "journal": "IEEE Transactions on ...",
  "date": "2026",
  "doi": "10.1109/...",
  "volume": "46",
  "issue": "3",
  "pages": "1234-1245",
  "abstract": "...",
  "keywords": ["keyword1", "keyword2"],
  "url": "https://ieeexplore.ieee.org/document/{ARNUMBER}",
  "pdfUrl": "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={ARNUMBER}",
  "cookies": "..."
}
```

### Listing Zotero collections

```bash
python scripts/push_to_zotero.py --list
```

## Export Format Reference

| Format | File Extension | Use Case |
|--------|---------------|----------|
| Plain Text | `.txt` | Human-readable citation |
| BibTeX | `.bib` | LaTeX documents |
| RIS | `.ris` | Reference managers (Zotero, Mendeley, EndNote) |
| RefWorks | `.txt` | RefWorks import |

## Notes

- The "Cite This" modal on document pages provides citation data for individual articles.
- The "Export" button on search results pages handles batch citation export.
- For batch export, articles must first be selected via checkboxes.
- Citation formats include: Plain Text, BibTeX, RIS, RefWorks.
- Include options: "Citation Only" or "Citation and Abstract".
- For Zotero push, ensure Zotero desktop is running before invoking.
