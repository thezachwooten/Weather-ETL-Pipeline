from datetime import datetime, timedelta, timezone

import httpx
from shared.config import settings
from shared.db.crud import get_3day_avg, save_3day_avg
from shared.db.database import AsyncSessionLocal
from shared.db.models import CleanWeather, ThreeDayWeatherAvg
from shared.locations import LOCATIONS

async def run_aggregation():
    async with AsyncSessionLocal() as session:
        rows = await get_3day_avg(session)
        
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(days=3)

        for row in rows:
            agg = ThreeDayWeatherAvg(
                location=row.location,
                window_start=window_start,
                window_end=now,
                avg_temp_f=row.avg_3day_temp
            )
            await save_3day_avg(session, agg)