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
from app.models.schemas import PaginatedJobsResponse
from typing import List
from datetime import datetime, timedelta, timezone
from app.config import COMPANIES
from fastapi.middleware.cors import CORSMiddleware
from app.services.scrape_service import scrape_all_companies
from app.scheduler import start_scheduler

app = FastAPI(title="Job Scraper API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/jobs", response_model=PaginatedJobsResponse)
def get_jobs(
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    company: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):

    query = db.query(Job)

    if status:
        query = query.filter(Job.status == status)

    if keyword:
        query = query.filter(Job.title.ilike(f"%{keyword}%"))
    
    if company:
        query = query.filter(Job.company == company)

    total = query.count()

    query = query.order_by(desc(Job.posted_at))

    jobs = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": jobs
    }

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
def scrape_all():
    return scrape_all_companies()

@app.on_event("startup")
def startup_event():
    start_scheduler()