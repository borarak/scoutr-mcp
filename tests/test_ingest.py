from __future__ import annotations

from datetime import date

from scoutr.catalog.ingest import normalize, stable_job_id
from scoutr.sources.base import available_sources
from scoutr.sources.models import RawPosting


def _raw(**kwargs) -> RawPosting:
    defaults: dict[str, object] = {
        "source": "remoteok",
        "external_id": "1",
        "title": "Dev",
        "organisation": "Org",
        "location": None,
    }
    return RawPosting(**{**defaults, **kwargs})  # type: ignore[arg-type]


def test_stable_job_id_is_deterministic():
    assert stable_job_id("remoteok", "1001") == stable_job_id("remoteok", "1001")


def test_stable_job_id_differs_across_sources():
    assert stable_job_id("remoteok", "1001") != stable_job_id("jobsdb", "1001")


def test_stable_job_id_differs_across_external_ids():
    assert stable_job_id("remoteok", "1001") != stable_job_id("remoteok", "1002")


def test_available_sources_includes_remoteok():
    sources = available_sources()
    assert "remoteok" in sources


def test_normalize_valid_remote_posting():
    raw = _raw(remote=True, posted_at=date(2026, 5, 30), location="Worldwide")
    job = normalize(raw)
    assert job is not None
    assert job.title == "Dev"
    assert job.organisation == "Org"
    assert job.mode == "remote"
    assert job.location == "Worldwide"
    assert job.date_posted == "30.05.2026"
    assert job.job_id == stable_job_id("remoteok", "1")


def test_normalize_on_site_when_not_remote():
    job = normalize(_raw(remote=False))
    assert job is not None
    assert job.mode == "on-site"


def test_normalize_on_site_when_remote_is_none():
    job = normalize(_raw(remote=None))
    assert job is not None
    assert job.mode == "on-site"


def test_normalize_falls_back_location_to_unknown():
    job = normalize(_raw(location=None))
    assert job is not None
    assert job.location == "Unknown"


def test_normalize_empty_date_posted_when_none():
    job = normalize(_raw(posted_at=None))
    assert job is not None
    assert job.date_posted == ""


def test_normalize_empty_description_when_none():
    job = normalize(_raw(description=None))
    assert job is not None
    assert job.description == ""


def test_normalize_returns_none_without_title():
    assert normalize(_raw(title=None)) is None


def test_normalize_returns_none_without_organisation():
    assert normalize(_raw(organisation=None)) is None
