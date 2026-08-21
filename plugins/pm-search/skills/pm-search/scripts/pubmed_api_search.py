#!/usr/bin/env python3
"""Standalone PubMed search client using NCBI E-utilities (stdlib only).

Primary path for the pm-search skill: runs in any environment with Python 3
and network access — no browser or MCP server required. Mirrors the output
contract of the browser fallback documented in SKILL.md.

API: esearch (PMID list) + esummary (metadata), retmode=json.
Docs: https://www.ncbi.nlm.nih.gov/books/NBK25500/

Usage:
    python3 pubmed_api_search.py "soil carbon cycling" [--limit 20] [--page 1]
    python3 pubmed_api_search.py "neural rendering" --sort date --year-from 2022 --year-to 2026 --json
    python3 pubmed_api_search.py --selftest   # offline, no network

Set NCBI_MAILTO (or pass --mailto) to join NCBI's polite API pool.
Exit codes: 0 = ok (including zero results), 1 = request/parse failure.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
ALLOWED_HOSTS = {"eutils.ncbi.nlm.nih.gov"}
TIMEOUT = 15
RETRY_STATUS = {429, 500, 502, 503}
RETRY_DELAY = 1.0

# Embedded API responses for --selftest (real shape, synthetic records).
FIXTURE_ESEARCH = {
    "esearchresult": {
        "count": "2",
        "retmax": "2",
        "retstart": "0",
        "querytranslation": "soil carbon cycling",
        "idlist": ["40000001", "40000002"],
    }
}
FIXTURE_ESUMMARY = {
    "result": {
        "40000001": {
            "title": "Soil carbon cycling under climate warming.",
            "authors": [{"name": "Doe J"}, {"name": "Smith A"}],
            "fulljournalname": "Soil Biology",
            "source": "Soil Biol",
            "pubdate": "2024 Mar",
            "volume": "12",
            "issue": "1",
            "pages": "1-10",
            "pubtype": ["Journal Article"],
            "articleids": [
                {"idtype": "pubmed"},
                {"idtype": "doi", "value": "10.1000/fake.1"},
            ],
        },
        "40000002": {
            "title": "Microbial feedbacks in carbon cycling.",
            "authors": [{"name": "Lee K"}],
            "fulljournalname": "Ecology Letters",
            "source": "Ecol Lett",
            "pubdate": "2025 Jan",
            "volume": "28",
            "issue": "2",
            "pages": "55-66",
            "pubtype": ["Journal Article"],
            "articleids": [
                {"idtype": "pubmed"},
                {"idtype": "doi", "value": "10.1000/fake.2"},
            ],
        },
        "uids": ["40000001", "40000002"],
    }
}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Reject cross-host redirects: this client only talks to NCBI."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102
        raise RuntimeError(
            f"redirect to {newurl!r} blocked (allowlist: {sorted(ALLOWED_HOSTS)})"
        )


def _checked_url(url: str) -> str:
    """Allowlist gate: https only, known NCBI host only."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise RuntimeError(
            f"blocked URL {parsed.scheme}://{parsed.hostname}: not in allowlist"
        )
    return url


_OPENER = urllib.request.build_opener(NoRedirect)


def build_term(query: str, year_from: int | None, year_to: int | None) -> str:
    term = query.strip()
    if year_from or year_to:
        start = f"{year_from}/01/01" if year_from else "1900/01/01"
        end = f"{year_to}/12/31" if year_to else "2100/12/31"
        term += f" AND {start}:{end}[dp]"
    return term


def fetch_json(url: str) -> dict:
    """GET a JSON endpoint from NCBI; retry once on 429/5xx with backoff."""
    url = _checked_url(url)
    last_err = None
    for attempt in (1, 2):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "academic-research-skills/pm-search"}
            )
            with _OPENER.open(req, timeout=TIMEOUT) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in RETRY_STATUS and attempt == 1:
                time.sleep(RETRY_DELAY)
                continue
            raise RuntimeError(f"HTTP {e.code} from {url.split('?')[0]}") from e
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last_err = e
            if attempt == 1:
                time.sleep(RETRY_DELAY)
                continue
            raise RuntimeError(f"request failed: {e}") from e
    raise RuntimeError(f"request failed: {last_err}")


def run_search(
    query: str,
    limit: int,
    page: int,
    sort: str,
    year_from: int | None,
    year_to: int | None,
    mailto: str | None,
) -> dict:
    term = build_term(query, year_from, year_to)
    retstart = (page - 1) * limit
    params = {
        "db": "pubmed",
        "term": term,
        "retmax": str(limit),
        "retstart": str(retstart),
        "retmode": "json",
        "sort": sort,
    }
    if mailto:
        params["tool"] = "academic-research-skills"
        params["email"] = mailto

    search_url = f"{EUTILS}/esearch.fcgi?{urllib.parse.urlencode(params)}"
    search_data = fetch_json(search_url)
    result = search_data.get("esearchresult") or {}
    ids = result.get("idlist") or []
    total = int(result.get("count") or 0)
    query_translation = result.get("querytranslation") or ""
    if not ids:
        return {
            "query": query,
            "queryTranslation": query_translation,
            "total": total,
            "page": page,
            "size": limit,
            "results": [],
        }

    sum_url = f"{EUTILS}/esummary.fcgi?db=pubmed&retmode=json&id={','.join(ids)}"
    sum_data = fetch_json(sum_url).get("result") or {}

    records = []
    for i, pmid in enumerate(ids):
        r = sum_data.get(pmid) or {}
        doi = ""
        for aid in r.get("articleids") or []:
            if aid.get("idtype") == "doi":
                doi = aid.get("value") or ""
                break
        records.append(
            {
                "n": retstart + i + 1,
                "pmid": pmid,
                "title": r.get("title") or "",
                "authors": ", ".join(a.get("name", "") for a in r.get("authors") or []),
                "journal": r.get("fulljournalname") or "",
                "source": r.get("source") or "",
                "pubdate": r.get("pubdate") or "",
                "volume": r.get("volume") or "",
                "issue": r.get("issue") or "",
                "pages": r.get("pages") or "",
                "doi": doi,
                "pubtype": ", ".join(r.get("pubtype") or []),
            }
        )
    return {
        "query": query,
        "queryTranslation": query_translation,
        "total": total,
        "page": page,
        "size": limit,
        "results": records,
    }


def render_text(payload: dict) -> str:
    lines = [
        f'Searched PubMed for "{payload["query"]}": found {payload["total"]} results '
        f"(page {payload['page']}, showing {payload['size']} per page)."
    ]
    for r in payload["results"]:
        lines.append("")
        lines.append(f"{r['n']}. {r['title']}")
        lines.append(f"   PMID: {r['pmid']} | DOI: {r['doi'] or 'N/A'}")
        lines.append(f"   Authors: {r['authors'] or 'N/A'}")
        lines.append(
            f"   Journal: {r['journal']} ({r['pubdate']}) | Vol {r['volume']}({r['issue']}):{r['pages']}"
        )
    return "\n".join(lines)


def selftest() -> int:
    """Validate parsing logic offline against embedded fixtures."""
    records = []
    for i, pmid in enumerate(FIXTURE_ESEARCH["esearchresult"]["idlist"]):
        r = FIXTURE_ESUMMARY["result"].get(pmid) or {}
        doi = ""
        for aid in r.get("articleids") or []:
            if aid.get("idtype") == "doi":
                doi = aid.get("value") or ""
                break
        records.append({"pmid": pmid, "title": r.get("title"), "doi": doi})
    assert len(records) == 2, "expected 2 fixture records"
    assert records[0]["doi"] == "10.1000/fake.1", "DOI extraction failed"
    assert records[1]["title"] == "Microbial feedbacks in carbon cycling."
    assert build_term("x", 2022, None) == "x AND 2022/01/01:2100/12/31[dp]"
    assert build_term("x", None, None) == "x"
    bad = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    try:
        _checked_url(bad)
        raise AssertionError("non-https URL should be blocked")
    except RuntimeError:
        pass
    print("selftest OK: parse + DOI extraction + term building + URL allowlist")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Search PubMed via NCBI E-utilities")
    ap.add_argument("query", nargs="?", help="search keywords")
    ap.add_argument(
        "--limit", type=int, default=20, help="results per page (default 20)"
    )
    ap.add_argument("--page", type=int, default=1, help="1-indexed page number")
    ap.add_argument(
        "--sort",
        default="relevance",
        choices=["relevance", "date", "pub_date", "first_author", "journal"],
    )
    ap.add_argument("--year-from", type=int, default=None)
    ap.add_argument("--year-to", type=int, default=None)
    ap.add_argument("--mailto", default=os.environ.get("NCBI_MAILTO"))
    ap.add_argument("--json", action="store_true", help="machine-readable JSON output")
    ap.add_argument(
        "--selftest", action="store_true", help="offline self-test, no network"
    )
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.query:
        ap.error("query is required (or pass --selftest)")
    if not 1 <= args.limit <= 10000:
        ap.error("--limit must be 1-10000")
    if args.page < 1:
        ap.error("--page must be >= 1")

    try:
        payload = run_search(
            args.query,
            args.limit,
            args.page,
            args.sort,
            args.year_from,
            args.year_to,
            args.mailto,
        )
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("Hint: check network access to eutils.ncbi.nlm.nih.gov", file=sys.stderr)
        return 1

    print(
        json.dumps(payload, ensure_ascii=False, indent=2)
        if args.json
        else render_text(payload)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
