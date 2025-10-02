from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Iterable, Sequence

from .models import Job


def filter_since(jobs: Iterable[Job], since_hours: int) -> list[Job]:
    if since_hours <= 0:
        return list(jobs)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    kept: list[Job] = []
    for job in jobs:
        if job.posted_at is None:
            continue
        ts = job.posted_at
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if ts >= cutoff:
            kept.append(job)
    return kept


def filter_remote(jobs: Iterable[Job], remote_only: bool = True) -> list[Job]:
    if not remote_only:
        return list(jobs)
    kept: list[Job] = []
    for job in jobs:
        if job.remote:
            kept.append(job)
            continue
        # Heuristic based on location text
        heuristics_text = " ".join(filter(None, [job.location or "", job.title]))
        if any(k in heuristics_text.lower() for k in ["remote", "anywhere", "work from home", "distributed", "global"]):
            job.remote = True
            kept.append(job)
    return kept


def filter_query(jobs: Iterable[Job], keywords: Sequence[str] | None) -> list[Job]:
    if not keywords:
        return list(jobs)
    lowered = [k.lower() for k in keywords]
    kept: list[Job] = []
    for job in jobs:
        hay = " ".join(filter(None, [job.title, job.company or "", job.location or ""]))
        h = hay.lower()
        if all(k in h for k in lowered):
            kept.append(job)
    return kept
