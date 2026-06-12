from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

import httpx

from scoutr.sources.base import JobSource, register
from scoutr.sources.models import RawPosting

log = logging.getLogger(__name__)


_API_URL = "https://remoteok.com/api"
_USER_AGENT = "scoutr/0.1 (+https://github.com/borarak/scoutr-mcp)"


@register
class RemoteOKSource(JobSource):
    """Abstracts RemoteOK API end-point"""

    name = "remoteok"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client  # inject in tests

    async def search(self, query: str) -> list[RawPosting]:
        raw = self._parse(await self._fetch())  # parse first, then filter parsed objects

        if query:
            needle = query.lower()
            raw = [
                p
                for p in raw
                if needle in (p.title or "").lower() or needle in (p.description or "").lower()
            ]
        return raw

    async def _fetch(self) -> list[dict[str, Any]]:
        headers = {"User-Agent": _USER_AGENT, "Accept": "application/json"}

        if self._client is not None:  # for tests
            response = await self._client.get(_API_URL, headers=headers)
        else:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(_API_URL, headers=headers)

        response.raise_for_status()
        data: Any = response.json()
        return data if isinstance(data, list) else []

    def _parse(self, payload: list[dict[str, Any]]) -> list[RawPosting]:
        """Pure: JSON list -> RawPostings. RemoteOK's first element is a legal
        header (no `id`); skip it. Fail-soft: skip malformed rows."""
        postings: list[RawPosting] = []

        for item in payload:
            if not isinstance(item, dict) or "id" not in item:
                continue
            try:
                postings.append(self._parse_one(item))
            except Exception:
                log.warning("remoteok: skipped malformed posting", exc_info=True)
        return postings

    @staticmethod
    def _parse_one(item: dict[str, Any]) -> RawPosting:
        tags = item.get("tags")
        return RawPosting(
            source="remoteok",
            external_id=str(item["id"]),
            title=item.get("position") or item.get("title"),
            organisation=item.get("company"),
            location=item.get("location") or None,
            remote=True,
            description=item.get("description"),
            url=item.get("url"),
            posted_at=_parse_date(item.get("date")),
            tags=[str(t) for t in tags] if isinstance(tags, list) else [],
            salary_min=_parse_salary(item.get("salary_min")),
            salary_max=_parse_salary(item.get("salary_max")),
            raw=item,
        )


def _parse_date(value: object) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


def _parse_salary(value: object) -> int | None:
    """RemoteOK sends 0 for 'unspecified'; treat 0/invalid as absent, not zero pay."""
    if not isinstance(value, (int, float, str)):
        return None
    try:
        n = int(value)
    except (TypeError, ValueError):
        return None
    return n if n > 0 else None
