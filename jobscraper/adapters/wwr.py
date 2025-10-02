from __future__ import annotations

from typing import List
import httpx
from bs4 import BeautifulSoup

from ..models import Job
from ..utils import parse_datetime


RSS_URL = "https://weworkremotely.com/categories/remote-programming-jobs.rss"


async def fetch_wwr(client: httpx.AsyncClient) -> List[Job]:
    # Prefer RSS, but parse lightweight without feedparser to keep a single async client
    resp = await client.get(RSS_URL, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "xml")
    jobs: List[Job] = []
    for item in soup.find_all("item"):
        title_tag = item.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""
        link_tag = item.find("link")
        link = link_tag.get_text(strip=True) if link_tag else None
        author_tag = item.find("author")
        author = author_tag.get_text(strip=True) if author_tag else None
        pub_tag = item.find("pubDate")
        pub_date = pub_tag.get_text(strip=True) if pub_tag else None
        jobs.append(
            Job(
                title=title,
                company=author,
                location=None,
                job_type=None,
                url=link,
                platform="WeWorkRemotely",
                posted_at=parse_datetime(pub_date),
                remote=True,
            )
        )
    return jobs
