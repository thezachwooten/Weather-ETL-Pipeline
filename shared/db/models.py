import uuid
from pydantic import BaseModel
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

class RawWeather(Base):
    __tablename__ = "raw_weather"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location: Mapped[str] = mapped_column()
    fetched_at: Mapped[datetime] = mapped_column(default=func.now())
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True) 
    payload: Mapped[dict] =  mapped_column(JSONB) 

class CleanWeather(Base):
    __tablename__ = "clean_weather"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raw_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("raw_weather.id"))
    location: Mapped[str] = mapped_column()
    fetched_at: Mapped[datetime] = mapped_column()
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_updated: Mapped[str] = mapped_column()
    temp_c: Mapped[float] = mapped_column()
    temp_f: Mapped[float] = mapped_column()
    condition: Mapped[str] = mapped_column()
    wind_mph: Mapped[float] = mapped_column()
    wind_kph: Mapped[float] = mapped_column()
    humidity: Mapped[int] = mapped_column()
    feelslike_c: Mapped[float] = mapped_column()
    feelslike_f: Mapped[float] = mapped_column()
    windchill_c: Mapped[float] = mapped_column()
    windchill_f: Mapped[float] = mapped_column()
    heatindex_c: Mapped[float] = mapped_column()
    heatindex_f: Mapped[float] = mapped_column()
    dewpoint_c: Mapped[float] = mapped_column()
    dewpoint_f: Mapped[float] = mapped_column()
    uv: Mapped[float] = mapped_column()
    gust_mph: Mapped[float] = mapped_column()
    gust_kph: Mapped[float] = mapped_column()

class ThreeDayWeatherAvg(Base):
    __tablename__ = "weather_3day_agg"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location: Mapped[str] = mapped_column()
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    avg_temp_f: Mapped[float] = mapped_column()
    aggregated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())