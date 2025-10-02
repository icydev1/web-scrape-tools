from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

import httpx

from ..models import Job
from ..utils import parse_datetime


API_URL = "https://remoteok.com/api"


async def fetch_remoteok(client: httpx.AsyncClient) -> List[Job]:
    resp = await client.get(API_URL, headers={"Accept": "application/json", "User-Agent": "jobscraper/1.0"}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    jobs: List[Job] = []
    for row in data:
        if not isinstance(row, dict):
            continue
        if row.get("position") is None and row.get("title") is None:
            continue
        # RemoteOK includes a metadata header row sometimes
        title = row.get("position") or row.get("title")
        posted = parse_datetime(row.get("epoch") or row.get("date"))
        jobs.append(
            Job(
                title=title or "",
                company=row.get("company"),
                location=row.get("location"),
                job_type=",".join(row.get("tags", [])[:3]) if isinstance(row.get("tags"), list) else None,
                url=row.get("url") or row.get("apply_url"),
                platform="RemoteOK",
                posted_at=posted,
                remote=True,
            )
        )
    return jobs
