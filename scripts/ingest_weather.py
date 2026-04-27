import asyncio
import httpx
from datetime import datetime, timezone
from shared.db.database import AsyncSessionLocal, init_db
from shared.db.models import RawWeather
from shared.config import settings
from shared.locations import LOCATIONS

async def run_ingestion():
    # 1. Ensure tables exist
    await init_db()
    
    async with AsyncSessionLocal() as session:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for location in LOCATIONS:
                try:
                    # 2. Fetch
                    url = f"http://api.weatherapi.com/v1/current.json?key={settings.weather_api_key}&q={location}"
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()

                    # 3. Create Model instance (Bronze Layer)
                    new_entry = RawWeather(
                        location=location,
                        payload=data,
                        fetched_at=datetime.now(timezone.utc)
                    )
                    
                    session.add(new_entry)
                    print(f"✅ Staged: {location}")
                
                except httpx.HTTPStatusError as e:
                    print(f"❌ HTTP error for {location}: {e.response.status_code} - {e.response.text}")
                except httpx.RequestError as e:
                    print(f"❌ Request failed for {location}: {e}")
                except Exception as e:
                    print(f"❌ Unexpected error for {location}: {e}")
            
            # 4. Commit all staged entries, roll back on failure
            try:
                await session.commit()
                print("✅ All staged entries committed.")
            except Exception as e:
                await session.rollback()
                print(f"❌ Commit failed, transaction rolled back: {e}")
                raise

if __name__ == "__main__":
    asyncio.run(run_ingestion())