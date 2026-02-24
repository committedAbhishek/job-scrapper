from sqlalchemy.orm import Session
from app.models.job import Job
from datetime import datetime, timedelta, timezone


class JobService:

    @staticmethod
    def save_jobs(db: Session, jobs: list):

        # 1️⃣ Delete jobs older than 24h
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        db.query(Job).filter(Job.posted_at < cutoff_time).delete()

        fetched_count = len(jobs)
        inserted_count = 0

        for job_data in jobs:
            existing_job = (
                db.query(Job)
                .filter(Job.url == job_data["url"])
                .first()
            )

            if not existing_job:
                job = Job(**job_data)
                db.add(job)
                inserted_count += 1

        db.commit()

        return {
            "fetched_count": fetched_count,
            "inserted_count": inserted_count
        }