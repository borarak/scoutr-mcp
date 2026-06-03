from __future__ import annotations

from datetime import date, datetime
from pgvector.sqlalchemy import Vector

from sqlalchemy import DateTime, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


EMBEDDING_DIM = 1536 # openai/text-embedding-small -> latge: 3072


class Base(DeclarativeBase):
    pass


class JobRow(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_jobs_source_external_id"),)

    job_id: Mapped[str] = mapped_column(String, primary_key=True)  # deterministic uuid5
    source: Mapped[str] = mapped_column(String, index=True)
    external_id: Mapped[str] = mapped_column(String)

    title: Mapped[str] = mapped_column(String)
    organisation: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String)
    mode: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    posted_at: Mapped[date | None] = mapped_column(nullable=True)

    # Provisioned for RAG, unused by core ranking. Nullable so ingest skips it.
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )