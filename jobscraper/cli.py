from __future__ import annotations

import argparse
import asyncio
from typing import List, Optional

import httpx
import orjson
from rich.console import Console
from rich.table import Table

from .models import Job
from .filters import filter_since, filter_remote, filter_query
from .adapters import (
    fetch_remoteok,
    fetch_wwr,
    fetch_lever,
    fetch_greenhouse,
    fetch_job_jsonld,
)


console = Console()


async def gather_jobs(
    include_remoteok: bool = True,
    include_wwr: bool = True,
    lever_companies: Optional[List[str]] = None,
    greenhouse_boards: Optional[List[str]] = None,
    urls: Optional[List[str]] = None,
) -> List[Job]:
    jobs: List[Job] = []
    async with httpx.AsyncClient() as client:
        tasks = []
        if include_remoteok:
            tasks.append(fetch_remoteok(client))
        if include_wwr:
            tasks.append(fetch_wwr(client))
        for company in (lever_companies or []):
            tasks.append(fetch_lever(client, company))
        for board in (greenhouse_boards or []):
            tasks.append(fetch_greenhouse(client, board))
        for u in (urls or []):
            tasks.append(fetch_job_jsonld(client, u))

        results = await asyncio.gather(*tasks, return_exceptions=True)
    for res in results:
        if isinstance(res, Exception):
            continue
        jobs.extend(res)
    return jobs


def render_table(jobs: List[Job]):
    table = Table(show_header=True, header_style="bold magenta")
    for col in [
        "Platform",
        "Title",
        "Company",
        "Location",
        "Type",
        "Remote",
        "Posted",
        "URL",
    ]:
        table.add_column(col)
    for job in jobs:
        table.add_row(*job.as_row())
    console.print(table)


def run_cli(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Job scraper (24h, remote-first)")
    parser.add_argument("--since-hours", type=int, default=24, help="Look back this many hours")
    parser.add_argument("--remote-only", action="store_true", default=True, help="Only remote roles (default true)")
    parser.add_argument("--no-remote-only", action="store_false", dest="remote_only", help="Disable remote-only filter")
    parser.add_argument("--keyword", action="append", help="Keyword filter (repeatable, ANDed)")
    parser.add_argument("--limit", type=int, default=50, help="Max jobs to display")
    parser.add_argument("--output", choices=["table", "json"], default="table", help="Output format")
    parser.add_argument("--skip-remoteok", action="store_true", help="Skip RemoteOK source")
    parser.add_argument("--skip-wwr", action="store_true", help="Skip WWR source")
    parser.add_argument("--lever", action="append", help="Lever company handle (repeatable)")
    parser.add_argument("--greenhouse", action="append", help="Greenhouse board token (repeatable)")
    parser.add_argument("--url", action="append", help="Job page URL with JSON-LD (repeatable)")
    args = parser.parse_args(argv)

    jobs = asyncio.run(
        gather_jobs(
            include_remoteok=not args.skip_remoteok,
            include_wwr=not args.skip_wwr,
            lever_companies=args.lever,
            greenhouse_boards=args.greenhouse,
            urls=args.url,
        )
    )
    jobs = filter_since(jobs, args.since_hours)
    jobs = filter_remote(jobs, args.remote_only)
    jobs = filter_query(jobs, args.keyword)
    jobs = sorted(
        [j for j in jobs if j.title],
        key=lambda j: (j.posted_at.timestamp() if j.posted_at else 0.0),
        reverse=True,
    )[: args.limit]
    if args.output == "json":
        payload = [j.model_dump(mode="python") for j in jobs]
        console.print(orjson.dumps(payload, option=orjson.OPT_INDENT_2).decode())
    else:
        render_table(jobs)


if __name__ == "__main__":
    run_cli()
