---
name: ieee-download
description: Downloads PDF from IEEE Xplore articles. Requires institutional or subscriber access. Use when the user wants to download a paper PDF by article number.
argument-hint: "[article number(s) or URL]"
disable-model-invocation: true
---

# IEEE Xplore PDF Download

Download PDF files from IEEE Xplore articles to the user's local disk.

## Prerequisites

- The user must have access to the article (institutional subscription, open access, or personal subscription).
- If the article is behind a paywall and the user has no access, the download will fail.

## PDF URL Patterns (Discovered via Testing)

IEEE Xplore has a two-layer PDF serving architecture:

| Layer | URL | Purpose |
|-------|-----|---------|
| Wrapper | `{BASE_URL}/stamp/stamp.jsp?tp=&arnumber={ARNUMBER}` | HTML page with iframe |
| **Actual PDF** | `{BASE_URL}/stampPDF/getPDF.jsp?tp=&arnumber={ARNUMBER}&ref=` | Direct PDF binary |

**Key discovery**: The `getPDF.jsp` URL pattern is **predictable** — you can skip `stamp.jsp` entirely and navigate directly to the PDF. This cuts tool calls from 6 to 2 per paper.

## Single Article Download (Optimized: 2 tool calls)

### Step 1: Pre-check access, then navigate directly to PDF

First, check if the user has access by visiting the document page:

```javascript
async () => {
  // Quick access check on the current document page
  const bodyText = document.body.innerText;
  const hasAccess = bodyText.includes('Access provided by');
  const accessLine = bodyText.match(/Access provided by[^\n]*/)?.[0] || '';
  return { hasAccess, accessLine };
}
```

If `hasAccess` is false, tell the user: "当前未登录或无权限访问此文章，请先在浏览器中完成机构登录。"

If access is confirmed, navigate **directly** to the getPDF URL (skip stamp.jsp):

```
navigate_page({
  url: "{BASE_URL}/stampPDF/getPDF.jsp?tp=&arnumber={ARNUMBER}&ref=",
  initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
})
```

### Step 2: Trigger download

```javascript
(arnumber, title) => {
  if (document.contentType === 'application/pdf') {
    // Construct a readable filename
    const safeName = (title || '').replace(/[^\w\s-]/g, '').replace(/\s+/g, '_').substring(0, 60);
    const filename = arnumber + (safeName ? '-' + safeName : '') + '.pdf';
    const a = document.createElement('a');
    a.href = window.location.href;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    return { downloaded: true, filename };
  }
  return { downloaded: false, contentType: document.contentType, error: 'Not a PDF. Access may be denied.' };
}
```

## Single Article Download (Fallback: 4 tool calls)

Use this only if the direct getPDF URL doesn't work (e.g., unusual access controls).

### Step 1: Navigate to stamp.jsp wrapper

```
navigate_page({
  url: "{BASE_URL}/stamp/stamp.jsp?tp=&arnumber={ARNUMBER}",
  initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
})
```

### Step 2: Extract actual PDF URL from iframe and redirect

```javascript
async () => {
  await new Promise(r => setTimeout(r, 4000));

  // Find the PDF iframe
  const iframe = document.querySelector('iframe[src*="getPDF"]');
  if (iframe) {
    // Redirect to the PDF URL directly (saves one navigate_page call)
    window.location.href = iframe.src;
    return { status: 'redirecting', pdfUrl: iframe.src };
  }

  // Check if PDF loaded directly
  if (document.contentType === 'application/pdf') {
    return { status: 'direct', pdfUrl: window.location.href };
  }

  // Access denied — page redirected back to document page
  if (window.location.href.includes('/document/')) {
    return { status: 'no-access', message: 'Redirected to document page. User likely has no access to this PDF.' };
  }

  return { status: 'unknown', url: window.location.href.substring(0, 100), contentType: document.contentType };
}
```

### Step 3: Wait for PDF to load and trigger download

```javascript
async (arnumber) => {
  await new Promise(r => setTimeout(r, 3000));
  if (document.contentType === 'application/pdf') {
    const a = document.createElement('a');
    a.href = window.location.href;
    a.download = arnumber + '.pdf';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    return { downloaded: true, filename: arnumber + '.pdf' };
  }
  return { downloaded: false, contentType: document.contentType };
}
```

## Batch Download (Sequential)

For downloading multiple papers efficiently, loop through a list of article numbers:

```
For each arnumber in list:
  1. navigate_page → {BASE_URL}/stampPDF/getPDF.jsp?tp=&arnumber={ARNUMBER}&ref=
  2. evaluate_script → check contentType, trigger download
  3. If contentType !== 'application/pdf' → log as failed, continue to next
```

**Rate limiting**: Wait at least 3 seconds between downloads to avoid triggering bot detection. The `await new Promise(r => setTimeout(r, 3000))` in the evaluate_script provides this naturally.

**Access pre-check**: Before starting a batch download, verify the user's institutional access is active by checking any document page for "Access provided by". This avoids wasting time on papers the user can't download.

## Batch Download from Search Results (UI-based)

On the search results page, there is a "Download PDFs" button. To use it:

1. Select articles using checkboxes
2. Click the "Download PDFs" button

```javascript
(arnumbers) => {
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

  const downloadBtn = [...document.querySelectorAll('button, .Menu-item')].find(b => b.textContent.trim().includes('Download PDF'));
  if (downloadBtn) {
    downloadBtn.click();
    return { success: true, selected, message: 'Download initiated for selected articles.' };
  }

  return { error: 'Download button not found.' };
}
```

## Access Denied Detection

When stamp.jsp or getPDF.jsp redirects back to the document page (URL contains `/document/` instead of `/stampPDF/`), it means the user has **no access** to the PDF. Common causes:

- Not logged in (check for "Institutional Sign In" on page)
- Institution doesn't subscribe to this content (e.g., older IEEE standards)
- Session expired

**Action**: Tell the user to check their login status and institutional access.

## Notes

- This skill is set to `disable-model-invocation: true` — it must be explicitly invoked with `/ieee-download`.
- **Optimized path** (direct getPDF.jsp): 2 tool calls per paper.
- **Fallback path** (stamp.jsp → iframe → getPDF): 3-4 tool calls per paper.
- The `window.location.href = iframe.src` redirect trick inside `evaluate_script` saves one `navigate_page` call.
- Open access articles can be downloaded without authentication.
- For subscription articles, the user must be authenticated (institutional access or personal subscription).
- After solving any captcha once, subsequent downloads in the same session work without interruption.
- If download fails, suggest the user check their access status or try logging in.
