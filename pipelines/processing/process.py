from datetime import datetime, timezone

import httpx
from shared.config import settings
from shared.db.crud import save_clean_weather, get_unprocessed_raw_weather, mark_raw_as_processed
from shared.db.database import AsyncSessionLocal
from shared.db.models import CleanWeather

async def run_processing():
    async with AsyncSessionLocal() as session:
        all_raw_weather = await get_unprocessed_raw_weather(session)

        for raw in all_raw_weather:
            current = raw.payload["current"]

            cleaned = CleanWeather(
                raw_id=raw.id,
                location=raw.location,                       
                fetched_at=raw.fetched_at,
                processed_at = datetime.now(timezone.utc),      
                last_updated=current["last_updated"],
                temp_c=current["temp_c"],
                temp_f=current["temp_f"],
                condition=current["condition"]["text"],
                wind_mph=current["wind_mph"],
                wind_kph=current["wind_kph"],
                humidity=current["humidity"],
                feelslike_c=current["feelslike_c"],
                feelslike_f=current["feelslike_f"],
                windchill_c=current["windchill_c"],
                windchill_f=current["windchill_f"],
                heatindex_c=current["heatindex_c"],
                heatindex_f=current["heatindex_f"],
                dewpoint_c=current["dewpoint_c"],
                dewpoint_f=current["dewpoint_f"],
                uv=current["uv"],
                gust_mph=current["gust_mph"],
                gust_kph=current["gust_kph"]
            )

            await save_clean_weather(session, cleaned)
            await mark_raw_as_processed(session, raw.id)