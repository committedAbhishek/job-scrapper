import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict
from app.scrapers.base import BaseScraper


class GreenhouseScraper(BaseScraper):

    def __init__(self, company_slug: str):
        self.company_slug = company_slug
        self.url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs"

    def fetch_jobs(self) -> List[Dict]:
        response = requests.get(self.url)

        if response.status_code != 200:
            return []

        data = response.json()
        jobs = []

        now = datetime.now(timezone.utc)
        last_24_hours = now - timedelta(hours=24)

        for job in data.get("jobs", []):
            updated_at = job.get("updated_at")

            if not updated_at:
                continue

            posted_time = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))

            if posted_time >= last_24_hours:
                jobs.append({
                    "company": self.company_slug,
                    "title": job.get("title"),
                    "location": job.get("location", {}).get("name"),
                    "url": job.get("absolute_url"),
                    "posted_at": posted_time
                })

        return jobs