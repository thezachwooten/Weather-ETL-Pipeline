import asyncio
from pipelines.ingestion.ingest import run_ingestion
from pipelines.processing.process import run_processing
from pipelines.aggregation.aggregate import run_aggregation
from shared.db.database import init_db
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def main():
    await init_db()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_ingestion, "interval", minutes=60)
    scheduler.add_job(run_processing, "interval", minutes=70)
    scheduler.add_job(run_aggregation, "cron", hour=0, minute=0)
    scheduler.start()

    # Keep the event loop running forever
    await asyncio.Event().wait()

asyncio.run(main())