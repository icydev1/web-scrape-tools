from __future__ import annotations

from typing import List

import httpx

from ..models import Job
from ..utils import parse_datetime


API_BASE = "https://boards-api.greenhouse.io/v1/boards/"


async def fetch_greenhouse(client: httpx.AsyncClient, board: str) -> List[Job]:
    url = f"{API_BASE}{board}/jobs?content=true"
    resp = await client.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    jobs: List[Job] = []
    for row in data.get("jobs", []) if isinstance(data, dict) else []:
        title = row.get("title") or ""
        comp = data.get("metadata", {}).get("company_name") if isinstance(data, dict) else None
        # Greenhouse often has multiple locations; treat remote by keyword
        loc = None
        if isinstance(row.get("location"), dict):
            loc = row["location"].get("name")
        is_remote = bool(loc and "remote" in loc.lower())
        posted = parse_datetime(row.get("updated_at") or row.get("created_at"))
        url = row.get("absolute_url") or row.get("hosted_url")
        jobs.append(
            Job(
                title=title,
                company=comp or board,
                location=loc,
                job_type=None,
                url=url,
                platform="Greenhouse",
                posted_at=posted,
                remote=is_remote,
            )
        )
    return jobs
