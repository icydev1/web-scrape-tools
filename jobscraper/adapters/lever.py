from __future__ import annotations

from typing import List

import httpx

from ..models import Job
from ..utils import parse_datetime


API_BASE = "https://api.lever.co/v0/postings/"


async def fetch_lever(client: httpx.AsyncClient, company: str) -> List[Job]:
    url = f"{API_BASE}{company}?mode=json"
    resp = await client.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    jobs: List[Job] = []
    if not isinstance(data, list):
        return jobs
    for row in data:
        if not isinstance(row, dict):
            continue
        # Lever marks remote via location or tags sometimes
        is_remote = False
        location = None
        if isinstance(row.get("workplaceTypes"), list) and any(x == "remote" for x in row["workplaceTypes"]):
            is_remote = True
        locs = row.get("categories", {})
        if isinstance(locs, dict):
            location = locs.get("location")
            if location and "remote" in location.lower():
                is_remote = True
        posted = parse_datetime(row.get("createdAt") or row.get("createdAtIso"))
        url = row.get("hostedUrl") or row.get("url")
        job_type = None
        if isinstance(row.get("workType"), str):
            job_type = row["workType"]
        elif isinstance(row.get("categories"), dict):
            job_type = row["categories"].get("commitment")
        jobs.append(
            Job(
                title=row.get("text") or row.get("title") or "",
                company=company,
                location=location,
                job_type=job_type,
                url=url,
                platform="Lever",
                posted_at=posted,
                remote=is_remote,
            )
        )
    return jobs
