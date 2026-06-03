from __future__ import annotations
from pydantic import BaseModel, Field

from datetime import date
from typing import Any


class RawPosting(BaseModel):
    """A raw job posting retreieved from one of the job boards"""
    source: str = Field(description="the job board from which this job was fetched")
    external_id: str = Field(description="The source's own id for this posting.")
    title: str | None = Field(description="String describing job title")
    location: str | None = Field(description="Location describing the city or town of the user")
    organisation: str | None = Field(description="The name of the organisation which posted the job")
    remote: bool | None = Field(default=None, description="True if the source marks the role remote.")
    description: str | None = None
    url: str | None = None
    posted_at: date | None = None
    tags: list[str] = Field(default_factory=list, description="Source-provided skill/category tags.")
    salary_min: int | None = Field(default=None, description="Lower salary bound, source currency.")
    salary_max: int | None = Field(default=None, description="Upper salary bound, source currency.")
    raw: dict[str, Any] = Field(
        default_factory=dict, description="Verbatim source payload, kept for re-normalization."
    )


