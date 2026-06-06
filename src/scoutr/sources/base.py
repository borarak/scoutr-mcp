from __future__ import annotations
from abc import ABC, abstractmethod
from scoutr.sources.models import RawPosting

import logging
log = logging.getLogger(__name__)


_REGISTRY: dict[str, type[JobSource]] = {}


def register(cls: type[JobSource]) -> type[JobSource]:
    """Class decorator; add a source to the registry"""
    if not cls.name:
        raise ValueError(f"{cls.__name__} must set a non-empty `name`.")
    if cls.name in _REGISTRY:
        raise ValueError(f"Duplicate source name: {cls.name!r}.")
    _REGISTRY[cls.name] = cls
    return cls


def available_sources() -> dict[str, type[JobSource]]:
    return dict(_REGISTRY)


class JobSource(ABC):
    """A base for each source job board"""

    name: str = ""

    @abstractmethod
    async def search(self, query: str) -> list[RawPosting]:
        """Return raw posting from a job baord"""
        ...
        