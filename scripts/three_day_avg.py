from datetime import datetime, timezone, timedelta
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, FloatType, TimestampType
from shared.db.database import AsyncSessionLocal, init_db
from shared.db.crud import save_3day_avg
from shared.db.models import ThreeDayWeatherAvg
import asyncio
import uuid

JDBC_URL = "jdbc:postgresql://db:5432/WeatherETL"
JDBC_PROPS = {
    "user": "WeatherETL",
    "password": "WeatherETL",
    "driver": "org.postgresql.Driver"
}
JDBC_JAR = "/opt/postgresql-42.7.2.jar"

def run_3_day_avg():
    spark = SparkSession.builder \
        .appName("WeatherETL-Gold") \
        .config("spark.jars", JDBC_JAR) \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    clean_df = spark.read.jdbc(
        url=JDBC_URL,
        table="clean_weather",
        properties=JDBC_PROPS
    )

    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=3)

    hourly_df = (
        clean_df
        .where(F.col("last_updated").cast("timestamp") >= F.lit(window_start))
        .withColumn("hour", F.date_trunc("hour", F.col("last_updated").cast("timestamp")))
        .groupBy("location", "hour")
        .agg(F.avg("temp_f").alias("hourly_avg"))
    )

    gold_df = (
        hourly_df
        .groupBy("location")
        .agg(F.avg("hourly_avg").alias("avg_temp_f"))
    )

    # Collect rows and construct ORM objects — same pattern as silver's mark_processed
    rows = gold_df.collect()

    async def persist_aggs():
        await init_db()
        async with AsyncSessionLocal() as session:
            for row in rows:
                agg = ThreeDayWeatherAvg(
                    id=uuid.uuid4(),
                    location=row["location"],
                    window_start=window_start,
                    window_end=now,
                    avg_temp_f=row["avg_temp_f"],
                )
                await save_3day_avg(session, agg)

    asyncio.run(persist_aggs())

    print(f"✅ Saved {len(rows)} 3-day averages to weather_3day_agg.")
    spark.stop()


if __name__ == "__main__":
    run_3_day_avg()