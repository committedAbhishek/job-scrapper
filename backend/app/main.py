from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional
from sqlalchemy import desc
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
def get_jobs(
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):

    query = db.query(Job)

    if status:
        query = query.filter(Job.status == status)

    if keyword:
        query = query.filter(Job.title.ilike(f"%{keyword}%"))

    query = query.order_by(desc(Job.posted_at))

    return query.offset(offset).limit(limit).all()

@app.get("/jobs/recent", response_model=List[JobResponse])
def get_recent_jobs(db: Session = Depends(get_db)):
    last_24 = datetime.now(timezone.utc) - timedelta(hours=24)
    return db.query(Job).filter(Job.posted_at >= last_24).all()

@app.patch("/jobs/{job_id}/status")
def update_job_status(job_id: int, status: str, db: Session = Depends(get_db)):

    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if status not in ["new", "applied", "ignored"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    job.status = status

    if status == "applied":
        job.applied_at = datetime.now(timezone.utc)
    else:
        job.applied_at = None

    db.commit()

    return {"message": "Status updated", "job_id": job_id}

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

