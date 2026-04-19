from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the directory where this script is located
BASE_DIR = Path(__file__).parent


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://WeatherETL:WeatherETL@localhost:5435/WeatherETL"
    weather_api_key: str =""
    zipcode: str = ""

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8")

settings = Settings()