from apscheduler.schedulers.background import BackgroundScheduler
from app.services.scrape_service import scrape_all_companies
import logging

scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(
        scrape_all_companies,
        trigger="cron",
        hour=8,
        minute=0,
    )
    scheduler.start()
    logging.info("Scheduler started: Daily scrape at 8:00 AM")