#!/usr/bin/env python3
"""Push CNKI paper data to Zotero via local Connector API (localhost:23119).

Session strategy: deterministic sessionID derived from content hash.
- 201 = saved successfully
- 409 = SESSION_EXISTS = already saved (idempotent, treat as success)
- Zotero's session gc/remove are buggy, sessions persist until restart.
  Deterministic IDs turn this bug into a feature: same content → same ID → 409 = already done.
"""

import json
import sys
import io
import hashlib
import urllib.request
import urllib.error
import re
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

ZOTERO_API = 'http://127.0.0.1:23119/connector'
HTTP_TIMEOUT = 15  # seconds, matching Zotero Connector extension


def zotero_request(endpoint, data=None, timeout=HTTP_TIMEOUT):
    """Send request to Zotero local API with timeout."""
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
        return -1, {'error': f'请求超时 ({timeout}s)'}


def make_session_id(items):
    """Generate deterministic sessionID from item content (titles hash).

    Same items always produce the same ID, so:
    - First call: creates session, saves items → 201
    - Repeat call: session exists → 409 → treat as already saved
    """
    key = '|'.join(sorted(item.get('title', '') for item in items))
    return hashlib.md5(key.encode('utf-8', errors='surrogateescape')).hexdigest()[:12]


def get_selected_collection():
    """Get currently selected Zotero collection."""
    status, data = zotero_request('getSelectedCollection')
    if status != 200 or not data:
        return None
    return data


def list_collections():
    """List all available Zotero collections."""
    data = get_selected_collection()
    if not data:
        print('Error: 无法连接 Zotero。请确保 Zotero 桌面端已启动。')
        return
    print(f'当前选中分类: {data.get("name", "?")} (ID: {data.get("id", "?")})')
    print(f'文库: {data.get("libraryName", "?")}')
    print()
    print('可用分类:')
    for t in data.get('targets', []):
        indent = '  ' * t.get('level', 0)
        recent = ' *' if t.get('recent') else ''
        print(f'  {indent}{t["name"]} (ID: {t["id"]}){recent}')


def parse_elearning(text):
    """Parse CNKI ELEARNING export format into structured fields."""
    text = text.replace('<br>', '\n').replace('\r', '')
    text = re.sub(r'<[^>]+>', '', text)  # strip HTML tags

    def get(key):
        m = re.search(rf'{re.escape(key)}:\s*(.+?)(?=\n|$)', text)
        return m.group(1).strip() if m else ''

    return {
        'title': get('Title-题名'),
        'authors': [a.strip() for a in get('Author-作者').split(';') if a.strip()],
        'journal': get('Source-刊名'),
        'year': get('Year-年'),
        'pubTime': get('PubTime-出版时间'),
        'keywords': [k.strip() for k in get('Keyword-关键词').split(';') if k.strip()],
        'abstract': get('Summary-摘要'),
        'volume': get('Roll-卷'),
        'issue': get('Period-期'),
        'pageCount': get('PageCount-页数'),
        'pages': get('Page-页码'),
        'organs': get('Organ-机构'),
        'link': get('Link-链接'),
        'srcDb': get('SrcDatabase-来源库'),
    }


def build_zotero_item(paper):
    """Build Zotero item JSON from paper data (matching Zotero Connector output)."""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    item = {
        'itemType': 'journalArticle',
        'title': paper.get('title', ''),
        'abstractNote': paper.get('abstract', ''),
        'date': paper.get('pubTime') or paper.get('year', ''),
        'language': 'zh-CN',
        'libraryCatalog': 'CNKI',
        'accessDate': now,
        'volume': paper.get('volume', ''),
        'pages': paper.get('pages', ''),
        'publicationTitle': paper.get('journal', ''),
        'issue': paper.get('issue', ''),
        'creators': [{'name': a, 'creatorType': 'author'} for a in paper.get('authors', [])],
        'tags': [{'tag': k, 'type': 1} for k in paper.get('keywords', [])],
        'attachments': [],
    }

    # URL: use Zotero Connector's format for compatibility
    dbcode = paper.get('dbcode', '')
    dbname = paper.get('dbname', '')
    filename = paper.get('filename', '')
    if dbcode and dbname and filename:
        item['url'] = f'https://kns.cnki.net/KCMS/detail/detail.aspx?dbcode={dbcode}&dbname={dbname}&filename={filename}'
    elif paper.get('link'):
        item['url'] = paper['link']

    # ISSN
    if paper.get('issn'):
        item['ISSN'] = paper['issn']

    # Build extra field (matching Zotero Connector's CNKI translator output)
    extra_parts = []
    if paper.get('journalEN'):
        extra_parts.append(f'original-container-title: {paper["journalEN"]}')
    if paper.get('foundation'):
        extra_parts.append(f'foundation: {paper["foundation"]}')
    if paper.get('downloadCount'):
        extra_parts.append(f'download: {paper["downloadCount"]}')
    if paper.get('album'):
        extra_parts.append(f'album: {paper["album"]}')
    if paper.get('clcCode'):
        extra_parts.append(f'CLC: {paper["clcCode"]}')
    if dbcode:
        extra_parts.append(f'dbcode: {dbcode}')
    if dbname:
        extra_parts.append(f'dbname: {dbname}')
    if filename:
        extra_parts.append(f'filename: {filename}')
    if paper.get('publicationTag'):
        extra_parts.append(f'publicationTag: {paper["publicationTag"]}')
    if paper.get('cif'):
        extra_parts.append(f'CIF: {paper["cif"]}')
    if paper.get('aif'):
        extra_parts.append(f'AIF: {paper["aif"]}')

    if extra_parts:
        item['extra'] = '\n'.join(extra_parts)

    return item


def download_pdf(pdf_url, cookies='', referer='https://kns.cnki.net'):
    """Download PDF from CNKI using provided cookies. Returns (bytes, content_type) or (None, error)."""
    req = urllib.request.Request(pdf_url, headers={
        'Cookie': cookies,
        'Referer': referer,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0',
    })
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        content_type = resp.headers.get('Content-Type', 'application/pdf')
        data = resp.read()
        if len(data) < 1024:
            return None, f'PDF 文件太小 ({len(data)} bytes)，可能需要登录'
        return data, content_type
    except Exception as e:
        return None, str(e)


def save_attachment(session_id, item_id, pdf_bytes, pdf_url, content_type='application/pdf', title='Full Text PDF'):
    """Upload PDF binary to Zotero via /connector/saveAttachment (Zotero 7.x workflow)."""
    metadata = json.dumps({
        'id': item_id + '_pdf',
        'parentItemID': item_id,
        'title': title,
        'url': pdf_url,
        'contentType': content_type,
    })
    url = f'{ZOTERO_API}/saveAttachment?sessionID={session_id}'
    req = urllib.request.Request(url, data=pdf_bytes, headers={
        'Content-Type': content_type,
        'X-Metadata': metadata,
        'Content-Length': str(len(pdf_bytes)),
        'X-Zotero-Connector-API-Version': '3',
    })
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        return resp.status, None
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='replace')
    except Exception as e:
        return 0, str(e)


def save_items(items, uri='', attachments=None, cookies=''):
    """Push items to Zotero via saveItems API, optionally with PDF attachments.

    Uses deterministic sessionID (content hash) for idempotency:
    - 201 = saved successfully
    - 409 = same items already saved in this Zotero session (success)

    If attachments are provided, downloads and uploads PDFs after saving metadata.
    attachments format: [{"itemIndex": 0, "pdfUrl": "https://...", "title": "Full Text PDF"}, ...]
    """
    session_id = make_session_id(items)

    # Assign IDs to items (needed for attachment parentItemID mapping)
    for i, item in enumerate(items):
        if 'id' not in item:
            item['id'] = f'cnki_{session_id}_{i}'

    data = {
        'sessionID': session_id,
        'uri': uri,
        'items': items
    }
    status, resp = zotero_request('saveItems', data)

    already_saved = False
    if status == 201:
        msg = f'保存成功 (session: {session_id})'
    elif status == 409:
        already_saved = True
        msg = f'这批论文已保存过，无需重复添加 (session: {session_id})'
    elif status == 500:
        detail = resp.get('error', '') if resp else ''
        if 'libraryEditable' in str(resp):
            return 500, '目标文库为只读，请在 Zotero 中切换到可写的分类'
        return 500, f'Zotero 内部错误: {detail}'
    elif status == 0:
        return 0, 'Zotero 未运行或连接被拒绝'
    elif status == -1:
        return -1, f'请求超时 ({HTTP_TIMEOUT}s)，Zotero 可能正在处理大量数据'
    else:
        return status, f'未知错误，HTTP {status}'

    # Handle PDF attachments (only for new saves, skip if already saved)
    if attachments and not already_saved:
        # Check if target collection supports files
        col = get_selected_collection()
        files_editable = col.get('filesEditable', True) if col else True

        if files_editable:
            pdf_results = []
            for att in attachments:
                idx = att.get('itemIndex', 0)
                pdf_url = att.get('pdfUrl', '')
                title = att.get('title', 'Full Text PDF')
                if not pdf_url:
                    continue

                item_id = items[idx]['id'] if idx < len(items) else items[0]['id']
                print(f'  下载 PDF: {pdf_url[:80]}...', file=sys.stderr)
                pdf_bytes, ct = download_pdf(pdf_url, cookies=cookies)

                if pdf_bytes is None:
                    pdf_results.append(f'  PDF 下载失败: {ct}')
                    continue

                print(f'  上传 PDF 到 Zotero ({len(pdf_bytes)} bytes)...', file=sys.stderr)
                att_status, att_err = save_attachment(session_id, item_id, pdf_bytes, pdf_url, title=title)
                if att_status == 201:
                    pdf_results.append(f'  PDF 已附加: {title} ({len(pdf_bytes) // 1024}KB)')
                else:
                    pdf_results.append(f'  PDF 上传失败: HTTP {att_status} {att_err or ""}')

            if pdf_results:
                msg += '\n' + '\n'.join(pdf_results)
        else:
            msg += '\n  (目标分类不支持文件附件，跳过 PDF)'

    return 201, msg


def main():
    """Main entry point. Accepts JSON paper data from stdin or file argument."""
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        list_collections()
        return

    # Check Zotero is running
    status, _ = zotero_request('ping')
    if status == 0:
        print('Error: Zotero 未运行。请启动 Zotero 桌面端。')
        sys.exit(1)

    # Show current collection
    col = get_selected_collection()
    if col:
        print(f'Zotero 当前分类: {col.get("name", "?")}')

    # Read paper data from stdin or file
    if len(sys.argv) > 1 and sys.argv[1] != '--list':
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            paper_data = json.load(f)
    else:
        paper_data = json.load(sys.stdin)

    # Handle both single paper and array
    if isinstance(paper_data, list):
        papers = paper_data
    elif 'items' in paper_data:
        # Already in Zotero format
        status, msg = save_items(paper_data['items'], paper_data.get('uri', ''))
        if status == 201:
            print(f'成功: {msg} ({len(paper_data["items"])} 篇)')
        else:
            print(f'失败: {msg}')
            sys.exit(1)
        return
    else:
        papers = [paper_data]

    # Build Zotero items
    items = []
    for p in papers:
        if 'itemType' in p:
            items.append(p)
        elif 'title' in p and 'authors' in p:
            items.append(build_zotero_item(p))
        elif 'ELEARNING' in p:
            parsed = parse_elearning(p['ELEARNING'])
            # Merge page-level fields into parsed data
            for k in ['issn', 'dbcode', 'dbname', 'filename', 'clcCode',
                       'journalEN', 'foundation', 'downloadCount', 'album',
                       'publicationTag', 'cif', 'aif', 'pageUrl']:
                if k in p and p[k]:
                    parsed[k] = p[k]
            items.append(build_zotero_item(parsed))

    if not items:
        print('Error: 无有效论文数据。')
        sys.exit(1)

    # Collect attachment info and cookies from input
    attachments = []
    cookies = ''
    for i, p in enumerate(papers):
        if p.get('pdfUrl'):
            attachments.append({
                'itemIndex': i,
                'pdfUrl': p['pdfUrl'],
                'title': p.get('pdfTitle', 'Full Text PDF'),
            })
        if p.get('cookies') and not cookies:
            cookies = p['cookies']

    uri = papers[0].get('pageUrl', papers[0].get('link', ''))
    status, msg = save_items(items, uri, attachments=attachments, cookies=cookies)
    if status == 201:
        print(f'成功: {msg} ({len(items)} 篇)')
        for item in items:
            print(f'  - {item.get("title", "?")}')
    else:
        print(f'失败: {msg}')
        sys.exit(1)


if __name__ == '__main__':
    main()
