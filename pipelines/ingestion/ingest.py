import httpx
from shared.config import settings
from shared.db.crud import save_raw_weather
from shared.db.database import AsyncSessionLocal
from shared.locations import LOCATIONS

WEATHER_API_KEY = settings.weather_api_key

async def fetch_weather(location: str) -> dict:
    url = "https://api.weatherapi.com/v1/current.json"
    params = {
        "key": WEATHER_API_KEY,
        "q": location,
        "aqi": "no"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

async def run_ingestion():
    for location in LOCATIONS:
        raw_weather_json = await fetch_weather(str(location))
    
        async with AsyncSessionLocal() as session:
            await save_raw_weather(session, str(location), raw_weather_json)