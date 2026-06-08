#!/usr/bin/env python3
"""Push WoS paper data to Zotero via local Connector API (localhost:23119).

Session strategy: deterministic sessionID derived from content hash.
- 201 = saved successfully
- 409 = SESSION_EXISTS = already saved (idempotent, treat as success)

Input: JSON from stdin or file argument. Accepts either:
1. Raw WoS API record format (from evaluate_script)
2. Pre-built Zotero item format (itemType present)
3. Wrapper with "items" array (direct saveItems format)
"""

import json
import sys
import io
import hashlib
import urllib.request
import urllib.error

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

ZOTERO_API = 'http://127.0.0.1:23119/connector'
HTTP_TIMEOUT = 15


def zotero_request(endpoint, data=None, timeout=HTTP_TIMEOUT):
    url = f'{ZOTERO_API}/{endpoint}'
    body = json.dumps(data or {}, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers={
        'Content-Type': 'application/json',
        'X-Zotero-Connector-API-Version': '3'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        text = resp.read().decode('utf-8')
        return resp.status, json.loads(text) if text else None
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode('utf-8', errors='replace')
        try:
            return e.code, json.loads(resp_body) if resp_body else None
        except json.JSONDecodeError:
            return e.code, {'error': resp_body}
    except urllib.error.URLError:
        return 0, None
    except TimeoutError:
        return -1, {'error': f'Timeout ({timeout}s)'}


def make_session_id(items):
    key = '|'.join(sorted(item.get('title', '') for item in items))
    return hashlib.md5(key.encode('utf-8', errors='surrogateescape')).hexdigest()[:12]


def build_zotero_item(paper):
    """Build Zotero journalArticle item from WoS paper data."""
    # Handle authors - accept both string ("A; B; C") and list formats
    authors_raw = paper.get('authors', [])
    if isinstance(authors_raw, str):
        authors_raw = [a.strip() for a in authors_raw.split(';') if a.strip()]

    creators = []
    for name in authors_raw:
        name = name.strip()
        if not name:
            continue
        # WoS standard format: "LastName, FirstInitials" e.g. "Gronroos, C"
        if ',' in name:
            parts = name.split(',', 1)
            creators.append({
                'lastName': parts[0].strip(),
                'firstName': parts[1].strip(),
                'creatorType': 'author'
            })
        else:
            creators.append({'name': name, 'creatorType': 'author'})

    # Build date from year + published
    date = paper.get('published', '') or str(paper.get('year', ''))

    item = {
        'itemType': 'journalArticle',
        'title': paper.get('title', ''),
        'abstractNote': paper.get('abstract', ''),
        'date': date,
        'language': paper.get('language', 'en'),
        'libraryCatalog': 'Web of Science',
        'publicationTitle': paper.get('source', ''),
        'volume': str(paper.get('volume', '') or ''),
        'issue': str(paper.get('issue', '') or ''),
        'pages': str(paper.get('pages', '') or ''),
        'DOI': paper.get('doi', ''),
        'ISSN': paper.get('issn', ''),
        'creators': creators,
        'tags': [],
        'attachments': [],
    }

    # URL
    wos_id = paper.get('accessionNumber', '') or paper.get('wosId', '')
    if wos_id:
        item['url'] = f'https://www.webofscience.com/wos/woscc/full-record/{wos_id}'

    # Keywords as tags
    for kw in paper.get('authorKeywords', []):
        item['tags'].append({'tag': kw, 'type': 1})
    for kw in paper.get('keywordsPlus', []):
        item['tags'].append({'tag': kw, 'type': 1})

    # Extra field - WoS-specific metadata
    extra_parts = []
    if wos_id:
        extra_parts.append(f'WoS ID: {wos_id}')
    cited = paper.get('citedCount', '') or paper.get('citations', '')
    if cited:
        alldb = paper.get('alldbCited', '') or paper.get('citationsAll', '')
        if alldb:
            extra_parts.append(f'Cited: {cited} (WOSCC) / {alldb} (All DB)')
        else:
            extra_parts.append(f'Cited: {cited}')
    if paper.get('jif'):
        jif_str = f'JIF: {paper["jif"]}'
        if paper.get('jifYear'):
            jif_str += f' ({paper["jifYear"]})'
        extra_parts.append(jif_str)
    if paper.get('jcrQuartile'):
        extra_parts.append(f'JCR: {paper["jcrQuartile"]}')
    if paper.get('researchAreas'):
        extra_parts.append(f'Research Areas: {paper["researchAreas"]}')
    if paper.get('wosCategories'):
        extra_parts.append(f'WoS Categories: {paper["wosCategories"]}')
    if paper.get('docType'):
        extra_parts.append(f'Document Type: {paper["docType"]}')
    if extra_parts:
        item['extra'] = '\n'.join(extra_parts)

    return item


def save_items(items, uri=''):
    session_id = make_session_id(items)
    for i, item in enumerate(items):
        if 'id' not in item:
            item['id'] = f'wos_{session_id}_{i}'

    data = {'sessionID': session_id, 'uri': uri, 'items': items}
    status, resp = zotero_request('saveItems', data)

    if status == 201:
        return 201, f'Saved (session: {session_id})'
    elif status == 409:
        return 201, f'Already saved (session: {session_id})'
    elif status == 500:
        if resp and 'libraryEditable' in str(resp):
            return 500, 'Library is read-only'
        return 500, f'Zotero error: {resp}'
    elif status == 0:
        return 0, 'Zotero not running'
    elif status == -1:
        return -1, f'Timeout ({HTTP_TIMEOUT}s)'
    else:
        return status, f'HTTP {status}'


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        status, data = zotero_request('getSelectedCollection')
        if status != 200 or not data:
            print('Error: Cannot connect to Zotero.')
            sys.exit(1)
        print(f'Current collection: {data.get("name", "?")}')
        for t in data.get('targets', []):
            indent = '  ' * t.get('level', 0)
            print(f'  {indent}{t["name"]} (ID: {t["id"]})')
        return

    # Check Zotero
    status, _ = zotero_request('ping')
    if status == 0:
        print('Error: Zotero not running.')
        sys.exit(1)

    col_status, col = zotero_request('getSelectedCollection')
    if col_status == 200 and col:
        print(f'Zotero collection: {col.get("name", "?")}')

    # Read input
    if len(sys.argv) > 1 and sys.argv[1] != '--list':
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            paper_data = json.load(f)
    else:
        paper_data = json.load(sys.stdin)

    # Handle wrapper format {"items": [...]}
    if isinstance(paper_data, dict) and 'items' in paper_data:
        items = paper_data['items']
        # If items already have itemType, use directly
        if items and 'itemType' in items[0]:
            status, msg = save_items(items, paper_data.get('uri', ''))
        else:
            built = [build_zotero_item(p) for p in items]
            status, msg = save_items(built, paper_data.get('uri', ''))
        if status == 201:
            print(f'OK: {msg} ({len(items)} papers)')
        else:
            print(f'Error: {msg}')
            sys.exit(1)
        return

    # Handle single or array
    papers = paper_data if isinstance(paper_data, list) else [paper_data]
    items = []
    for p in papers:
        if 'itemType' in p:
            items.append(p)
        else:
            items.append(build_zotero_item(p))

    if not items:
        print('Error: No valid paper data.')
        sys.exit(1)

    uri = papers[0].get('url', '')
    status, msg = save_items(items, uri)
    if status == 201:
        print(f'OK: {msg} ({len(items)} papers)')
        for item in items:
            print(f'  - {item.get("title", "?")}')
    else:
        print(f'Error: {msg}')
        sys.exit(1)


if __name__ == '__main__':
    main()
