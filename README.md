## JobScraper (24h, remote-first)

Command-line job scraper with default filters: last 24 hours and remote-only. Pulls from multiple sources (RemoteOK API, WeWorkRemotely RSS, Lever and Greenhouse company boards) and can extract JobPosting JSON-LD from arbitrary URLs.

### Features
- Default filters: last 24 hours, remote-only
- Sources: RemoteOK, WeWorkRemotely, Lever (per company), Greenhouse (per board)
- Generic JSON-LD extraction for arbitrary pages via `--url`
- Output as table or JSON

### Quickstart

```bash
pip install -r requirements.txt
python3 -m jobscraper.cli --limit 20 --output table
```

### Examples

- RemoteOK + WWR (default):
```bash
python3 -m jobscraper.cli
```

- Include Lever for a company (e.g. `stripe`):
```bash
python3 -m jobscraper.cli --lever stripe
```

- Include Greenhouse board (e.g. `brex`):
```bash
python3 -m jobscraper.cli --greenhouse brex
```

- Scrape a specific page with JSON-LD JobPosting:
```bash
python3 -m jobscraper.cli --url https://example.com/jobs/senior-engineer
```

- Change the time window and output format:
```bash
python3 -m jobscraper.cli --since-hours 12 --output json
```

### Notes
- Some sources may throttle or modify formats. This tool uses best-effort parsing and may skip malformed items.
- For Lever and Greenhouse, you must know the company handle/board token.
- Pass `--keyword` multiple times to AND-match terms, e.g. `--keyword python --keyword backend`.
- Default filters: `--since-hours 24` and `--remote-only` (use `--no-remote-only` to disable).
# web-scrape-tools