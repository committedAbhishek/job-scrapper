import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict
from app.scrapers.base import BaseScraper


class LeverScraper(BaseScraper):

    def __init__(self, company_slug: str):
        self.company_slug = company_slug
        self.url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"

    def fetch_jobs(self) -> List[Dict]:
        response = requests.get(self.url)

        if response.status_code != 200:
            return []

        data = response.json()
        jobs = []

        now = datetime.now(timezone.utc)
        last_24_hours = now - timedelta(hours=24)

        for job in data:

            created_at_ms = job.get("createdAt")
            if not created_at_ms:
                continue

            # Lever gives timestamp in milliseconds
            posted_time = datetime.fromtimestamp(
                created_at_ms / 1000,
                tz=timezone.utc
            )

            if posted_time >= last_24_hours:
                jobs.append({
                    "company": self.company_slug,
                    "title": job.get("text"),
                    "location": job.get("categories", {}).get("location"),
                    "url": job.get("hostedUrl"),
                    "posted_at": posted_time
                })

        return jobs