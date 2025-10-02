from __future__ import annotations

from typing import List

import httpx
from bs4 import BeautifulSoup

from ..models import Job
from ..utils import parse_datetime


async def fetch_job_jsonld(client: httpx.AsyncClient, url: str) -> List[Job]:
    resp = await client.get(url, timeout=30)
    resp.raise_for_status()
    html = resp.text
    soup = BeautifulSoup(html, "lxml")
    jobs: List[Job] = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            import orjson

            data = orjson.loads(tag.text)
        except Exception:
            continue
        # Handle list or single object
        items = data if isinstance(data, list) else [data]
        for obj in items:
            if not isinstance(obj, dict):
                continue
            typ = obj.get("@type")
            if typ == "JobPosting" or (isinstance(typ, list) and "JobPosting" in typ):
                title = obj.get("title") or ""
                hiring_org = obj.get("hiringOrganization")
                company = None
                if isinstance(hiring_org, dict):
                    company = hiring_org.get("name")
                employment_type = obj.get("employmentType")
                job_loc = obj.get("jobLocation")
                location = None
                if isinstance(job_loc, dict):
                    addr = job_loc.get("address") or {}
                    if isinstance(addr, dict):
                        parts = [addr.get("addressLocality"), addr.get("addressRegion"), addr.get("addressCountry")]
                        location = ", ".join([p for p in parts if p]) or None
                date_posted = parse_datetime(obj.get("datePosted"))
                jobs.append(
                    Job(
                        title=title,
                        company=company,
                        location=location,
                        job_type=employment_type if isinstance(employment_type, str) else None,
                        url=url,
                        platform="JSON-LD",
                        posted_at=date_posted,
                        remote="remote" in (location or "").lower(),
                    )
                )
    return jobs
