from __future__ import annotations

import logging
import uuid

from scoutr.catalog.repository import JobRepository
from scoutr.db.engine import get_session
from scoutr.models import Job
from scoutr.sources.base import available_sources
from scoutr.sources.models import RawPosting

log = logging.getLogger(__name__)


# Fixed namespace: same (source, external_id) always yields the same catalog id.
_NAMESPACE = uuid.UUID("6f1d3c0a-2e7b-4a5c-9b1e-0c2d4e6f8a10")


def stable_job_id(source: str, external_id: str) -> str:
    """Deterministic catalog id from source identity → idempotent ingest."""
    return str(uuid.uuid5(_NAMESPACE, f"{source}:{external_id}"))


def normalize(raw: RawPosting) -> Job | None:
    """Map a loose `RawPosting` to a clean catalog `Job`.

    Fail-soft: returns None if the posting lacks fields a job needs to be
    useful. Mode/location inference stays minimal; richer extraction is Day 3.
    """
    if not raw.title or not raw.organisation:
        return None
    return Job(
        job_id=stable_job_id(raw.source, raw.external_id),
        title=raw.title,
        organisation=raw.organisation,
        location=raw.location or "Unknown",
        mode="remote" if raw.remote else "on-site",
        date_posted=raw.posted_at.strftime("%d.%m.%Y") if raw.posted_at else "",
        description=raw.description or "",
    )


async def ingest(query: str = "") -> int:
    """Pull from every registered source → normalize → upsert. Returns rows seen."""
    count = 0
    async with get_session() as session:
        repo = JobRepository(session)
        for name, source_cls in available_sources().items():
            try:
                raws = await source_cls().search(query)
            except Exception:
                log.warning("source %s failed; skipping", name, exc_info=True)
                continue
            for raw in raws:
                job = normalize(raw)
                if job is None:
                    continue
                await repo.upsert(job, source=raw.source, external_id=raw.external_id)
                count += 1

    log.info("Ingested %d job posts", count)
    return count
