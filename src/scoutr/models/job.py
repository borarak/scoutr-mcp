from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Job(BaseModel):
    """Store the entire details of a job"""

    job_id: str = Field("A UUID string unique to each job")
    title: str = Field("String describing job title in slug-case")
    location: str = Field("Location describing the city or town of the user")
    organisation: str = Field("The name of the organisation which posted the job")
    mode: Literal["on-site", "hybrid", "remote"]
    date_posted: str = Field("the date of the job posted in dd-mm-yyyy format")
    description: str = Field("the description of the job deatailing the requirements")
