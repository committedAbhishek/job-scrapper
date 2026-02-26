from app.database import SessionLocal
from app.config import COMPANIES
from app.scrapers.greenhouse import GreenhouseScraper
from app.scrapers.lever import LeverScraper
from app.services.job_service import JobService


def scrape_all_companies():
    #print("AUTO SCRAPE TRIGGERED")


    db = SessionLocal()

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

    db.close()

    return {
        "total_companies": len(COMPANIES),
        "total_new_jobs_inserted": total_inserted,
        "details": company_results
    }