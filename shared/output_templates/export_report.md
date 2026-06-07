# Export Results Report Template

## Standard Output Contract

All export skills should produce output in the following format:

### Single Export (Zotero)

```
Exported to Zotero:
  Title: {title}
  Authors: {authors}
  Journal: {journal} ({year})
  Collection: {collection_name}
```

### Batch Export (Zotero)

```
Exported {count} papers to Zotero:
  1. {title1} ({journal1}, {year1})
  2. {title2} ({journal2}, {year2})
  ...
PDFs: {pdf_ok} attached, {pdf_fail} failed
```

### File Export (RIS/BibTeX)

```
Exported {count} records as {format}:
  File: {filepath}
  Format: {format} ({extension})
```

## Status Messages

| Status | Message Template |
|--------|-----------------|
| Success (new) | `OK: Saved (session: {session_id})` |
| Success (duplicate) | `OK: Already saved (session: {session_id})` |
| Zotero not running | `Error: Zotero is not running. Please start Zotero desktop.` |
| Library read-only | `Error: Target library is read-only.` |
| PDF skip | `PDF skip: {reason} ({url_truncated})` |
