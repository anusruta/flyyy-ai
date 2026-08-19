from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta, timezone
from sqlalchemy import delete, select
from app.database import AsyncSessionLocal
from app.models.models import AIAsset, AIInteraction
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def run_retention_cleanup():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AIAsset))
        assets = result.scalars().all()
        total_deleted = 0
        for asset in assets:
            cutoff = datetime.now(timezone.utc) - timedelta(days=asset.retention_days)
            del_result = await session.execute(
                delete(AIInteraction).where(
                    AIInteraction.asset_id == asset.id,
                    AIInteraction.timestamp < cutoff
                )
            )
            deleted = del_result.rowcount
            if deleted > 0:
                logger.info(f"Retention: deleted {deleted} records for asset {asset.name}")
                total_deleted += deleted
        await session.commit()
        logger.info(f"Retention cleanup complete. Total deleted: {total_deleted}")

def start_retention_scheduler(interval_hours: int = 1):
    scheduler.add_job(
        run_retention_cleanup,
        trigger="interval",
        hours=interval_hours,
        id="retention_cleanup",
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"Retention scheduler started (every {interval_hours}h)")

def stop_retention_scheduler():
    scheduler.shutdown(wait=False)
