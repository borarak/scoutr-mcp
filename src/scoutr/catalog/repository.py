from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from scoutr.db.models import JobRow
from scoutr.models import Job


class JobRepository:
    """All `jobs` persistence. Keeps SQL/dialect details out of the orchestrator."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert(self, job: Job, *, source: str, external_id: str) -> None:
        """Insert or update on (source, external_id) — idempotent re-ingest."""
        values = {
            "job_id": job.job_id,
            "source": source,
            "external_id": external_id,
            "title": job.title,
            "organisation": job.organisation,
            "location": job.location,
            "mode": job.mode,
            "description": job.description,
        }
        stmt = pg_insert(JobRow).values(**values)  # type: ignore[no-untyped-call]
        stmt = stmt.on_conflict_do_update(
            constraint="uq_jobs_source_external_id",
            set_={
                k: stmt.excluded[k]
                for k in ("title", "organisation", "location", "mode", "description")
            },
        )
        await self._session.execute(stmt)

    async def search(self, query: str, limit: int = 20) -> list[Job]:
        """Substring match over title/description. (Becomes vector search later.)"""
        stmt = select(JobRow)
        if query:
            like = f"%{query}%"
            stmt = stmt.where(JobRow.title.ilike(like) | JobRow.description.ilike(like))
        rows = (await self._session.execute(stmt.limit(limit))).scalars().all()
        return [self._to_job(r) for r in rows]

    @staticmethod
    def _to_job(row: JobRow) -> Job:
        return Job(
            job_id=row.job_id,
            title=row.title,
            organisation=row.organisation,
            location=row.location,
            mode=row.mode,  # type: ignore[arg-type]
            date_posted=row.posted_at.strftime("%d.%m.%Y") if row.posted_at else "",
            description=row.description,
        )
