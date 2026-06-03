from __future__ import annotations

import uuid

from scoutr.models import Job
from scoutr.sources.models import RawPosting

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