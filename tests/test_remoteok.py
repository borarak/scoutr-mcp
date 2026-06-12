from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from scoutr.sources.remoteok import RemoteOKSource

FIXTURE = Path(__file__).parent / "fixtures" / "remoteok.json"


def _client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def test_parse_skips_legal_header_and_reads_jobs():
    payload = json.loads(FIXTURE.read_text())
    postings = RemoteOKSource()._parse(payload)

    assert len(postings) == 2
    assert postings[0].source == "remoteok"
    assert postings[0].external_id == "1001"
    assert postings[0].title == "Senior Python Engineer"
    assert postings[0].organisation == "Acme"
    assert postings[0].remote is True


def test_parse_is_failsoft_on_bad_row():
    payload = [{"legal": "x"}, {"id": 1, "position": "ok", "company": "Z"}, {"oops": True}]
    assert len(RemoteOKSource()._parse(payload)) == 1


async def test_search_filters_by_query():
    body = [
        {"legal": "x"},
        {"id": 1, "position": "Python Dev", "company": "A", "description": ""},
        {"id": 2, "position": "Rust Dev", "company": "B", "description": ""},
    ]

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    out = await RemoteOKSource(client=_client(handler)).search("python")
    assert [p.external_id for p in out] == ["1"]  # Rust row filtered out


async def test_search_raises_on_http_error():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    with pytest.raises(httpx.HTTPStatusError):
        await RemoteOKSource(client=_client(handler)).search("x")
