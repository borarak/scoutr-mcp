"""THE MCP server that allows LLMs to query for job listings"""

from __future__ import annotations

import uuid

from mcp.server.fastmcp import FastMCP

from scoutr.db.engine import get_session

from scoutr.catalog.repository import JobRepository

from scoutr.models import Job

mcp = FastMCP()

FAKE_JOBS: list[Job] = [
    Job(
        title="AI Engineer",
        mode="remote",
        location="Berlin",
        job_id=str(uuid.uuid4()),
        date_posted="01.06.2026",
        description="Company X wants a AI Engineer with LangChain and RAG skills",
        organisation="X GmbH",
    ),
    Job(
        title="ML Engineer",
        mode="on-site",
        location="Berlin",
        job_id=str(uuid.uuid4()),
        date_posted="02.06.2026",
        description="Company Y wants a ML Engineer with PEFT and KV-Cache optimisation skills",
        organisation="Y AG",
    ),
]


@mcp.tool()
async def search_jobs(query: str) -> list[Job]:
    async with get_session() as session:
        return await JobRepository(session).search(query)
