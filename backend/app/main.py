from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models.job import Job
from app.scrapers.greenhouse import GreenhouseScraper
from app.scrapers.lever import LeverScraper
from app.services.job_service import JobService
from app.models.schemas import JobResponse
from typing import List
from datetime import datetime, timedelta, timezone
from app.config import COMPANIES


app = FastAPI(title="Job Scraper API")

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Job Scraper Backend Running"}


@app.post("/scrape/{company_slug}")
def scrape_jobs(company_slug: str, db: Session = Depends(get_db)):
    scraper = GreenhouseScraper(company_slug)
    jobs = scraper.fetch_jobs()
    JobService.save_jobs(db, jobs)

    return {
        "company": company_slug,
        "jobs_found": len(jobs)
    }


@app.get("/jobs", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()

@app.get("/jobs/recent", response_model=List[JobResponse])
def get_recent_jobs(db: Session = Depends(get_db)):
    last_24 = datetime.now(timezone.utc) - timedelta(hours=24)
    return db.query(Job).filter(Job.posted_at >= last_24).all()

@app.post("/scrape-all")
def scrape_all(db: Session = Depends(get_db)):
    total_inserted = 0
    company_results = []

    for company in COMPANIES:

        if company["ats"] == "greenhouse":
            scraper = GreenhouseScraper(company["slug"])
        elif company["ats"] == "lever":
            scraper = LeverScraper(company["slug"])
        else:
            continue

        jobs = scraper.fetch_jobs()
        stats = JobService.save_jobs(db, jobs)

        company_results.append({
            "company": company["name"],
            "fetched_count": stats["fetched_count"],
            "inserted_count": stats["inserted_count"]
        })

        total_inserted += stats["inserted_count"]

    return {
        "total_companies": len(COMPANIES),
        "total_new_jobs_inserted": total_inserted,
        "details": company_results
    }