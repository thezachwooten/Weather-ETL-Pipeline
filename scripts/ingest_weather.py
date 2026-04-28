import asyncio
import httpx
from shared.db.database import AsyncSessionLocal, init_db
from shared.config import settings
from shared.locations import LOCATIONS
from shared.db.crud import save_raw_weather  # import the function

async def run_ingestion():
    await init_db()
    
    async with AsyncSessionLocal() as session:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for location in LOCATIONS:
                try:
                    url = f"http://api.weatherapi.com/v1/current.json?key={settings.weather_api_key}&q={location}"
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()

                    await save_raw_weather(session, str(location), data)
                    print(f"✅ Saved: {location}")

                except httpx.HTTPStatusError as e:
                    print(f"❌ HTTP error for {location}: {e.response.status_code} - {e.response.text}")
                except httpx.RequestError as e:
                    print(f"❌ Request failed for {location}: {e}")
                except Exception as e:
                    print(f"❌ Unexpected error for {location}: {e}")

if __name__ == "__main__":
    asyncio.run(run_ingestion())