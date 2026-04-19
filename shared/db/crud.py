import uuid
from sqlalchemy import DateTime, cast, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from shared.db.models import RawWeather, CleanWeather, ThreeDayWeatherAvg
from datetime import datetime, timezone

async def save_raw_weather(session: AsyncSession, location: str, payload: dict) -> RawWeather:
    raw = RawWeather(
        id=uuid.uuid4(),
        location=location,
        payload=payload
    )
    session.add(raw)
    await session.commit()
    await session.refresh(raw)
    return raw

async def get_unprocessed_raw_weather(session: AsyncSession) -> list[RawWeather]:
    result = await session.execute(
        select(RawWeather).where(RawWeather.processed_at == None)
    )
    return result.scalars().all()

async def save_clean_weather(session: AsyncSession, cleanedWeather: CleanWeather) -> CleanWeather:
    session.add(cleanedWeather)
    await session.commit()
    await session.refresh(cleanedWeather)
    return cleanedWeather

async def mark_raw_as_processed(session: AsyncSession, raw_id: uuid.UUID):
    result = await session.execute(
        select(RawWeather).where(RawWeather.id == raw_id)
    )
    raw = result.scalar_one()
    raw.processed_at = datetime.now(timezone.utc)
    await session.commit()

async def get_3day_avg(session: AsyncSession):
    last_updated_ts = cast(CleanWeather.last_updated, DateTime)
    hour_trunc = func.date_trunc('hour', last_updated_ts)

    subq = (
        select(
            CleanWeather.location,
            hour_trunc.label("hour"),
            func.avg(CleanWeather.temp_f).label("hourly_avg")
        )
        .where(last_updated_ts >= func.now() - text("INTERVAL '3 days'"))
        .group_by(
            CleanWeather.location,
            hour_trunc
        )
    ).subquery()

    stmt = (
        select(
            subq.c.location,
            func.avg(subq.c.hourly_avg).label("avg_3day_temp")
        )
        .group_by(subq.c.location)
    )

    result = await session.execute(stmt)
    return result.all()

async def save_3day_avg(session: AsyncSession, agg: ThreeDayWeatherAvg) -> ThreeDayWeatherAvg:
    session.add(agg)
    await session.commit()
    await session.refresh(agg)
    return agg