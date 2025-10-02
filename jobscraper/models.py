from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl, Field


class Job(BaseModel):
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = Field(default=None, description="Employment type, e.g., Full-time/Contract")
    url: Optional[HttpUrl] = None
    platform: Optional[str] = None
    posted_at: Optional[datetime] = None
    remote: bool = True

    def as_row(self) -> list[str]:
        posted = self.posted_at.isoformat() if self.posted_at else ""
        return [
            self.platform or "",
            self.title,
            self.company or "",
            self.location or "",
            self.job_type or "",
            "Remote" if self.remote else "Onsite/Hybrid",
            posted,
            str(self.url) if self.url else "",
        ]
