import uuid
from datetime import datetime, timezone
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, from_json, lit, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
from shared.config import settings
from shared.db.database import AsyncSessionLocal, init_db
from shared.db.crud import mark_raw_as_processed, save_clean_weather
from shared.db.models import CleanWeather
import asyncio

JDBC_URL = f"jdbc:postgresql://db:5432/WeatherETL"
JDBC_PROPS = {
    "user": "WeatherETL",
    "password": "WeatherETL",
    "driver": "org.postgresql.Driver"
}
JDBC_JAR = "/opt/postgresql-42.7.2.jar"

# Schema of the 'current' field inside the WeatherAPI payload
CURRENT_SCHEMA = StructType([
    StructField("last_updated", StringType()),
    StructField("temp_c", DoubleType()),
    StructField("temp_f", DoubleType()),
    StructField("condition", StructType([
        StructField("text", StringType())
    ])),
    StructField("wind_mph", DoubleType()),
    StructField("wind_kph", DoubleType()),
    StructField("humidity", IntegerType()),
    StructField("feelslike_c", DoubleType()),
    StructField("feelslike_f", DoubleType()),
    StructField("windchill_c", DoubleType()),
    StructField("windchill_f", DoubleType()),
    StructField("heatindex_c", DoubleType()),
    StructField("heatindex_f", DoubleType()),
    StructField("dewpoint_c", DoubleType()),
    StructField("dewpoint_f", DoubleType()),
    StructField("uv", DoubleType()),
    StructField("gust_mph", DoubleType()),
    StructField("gust_kph", DoubleType()),
])


def run_transform():
    spark = SparkSession.builder \
        .appName("WeatherETL-Silver") \
        .config("spark.jars", JDBC_JAR) \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # 1. Read unprocessed raw records from Postgres
    raw_df = spark.read.jdbc(
        url=JDBC_URL,
        table="(SELECT id, location, fetched_at, payload FROM raw_weather WHERE processed_at IS NULL) AS unprocessed",
        properties=JDBC_PROPS
    )

    if raw_df.count() == 0:
        print("✅ No unprocessed records found.")
        spark.stop()
        return

    # 2. Parse the payload JSONB -> extract 'current' field
    # Full payload schema wrapper
    PAYLOAD_SCHEMA = StructType([
        StructField("current", CURRENT_SCHEMA)
    ])

    # In run_transform, replace the withColumn line with:
    raw_df = raw_df.withColumn(
        "current", from_json(col("payload"), PAYLOAD_SCHEMA).getField("current")
    )

    # 3. Flatten into clean_weather schema
    clean_df = raw_df.select(
        col("id").alias("raw_id"),
        col("location"),
        col("fetched_at"),
        col("current.last_updated").alias("last_updated"),
        col("current.temp_c").alias("temp_c"),
        col("current.temp_f").alias("temp_f"),
        col("current.condition.text").alias("condition"),
        col("current.wind_mph").alias("wind_mph"),
        col("current.wind_kph").alias("wind_kph"),
        col("current.humidity").alias("humidity"),
        col("current.feelslike_c").alias("feelslike_c"),
        col("current.feelslike_f").alias("feelslike_f"),
        col("current.windchill_c").alias("windchill_c"),
        col("current.windchill_f").alias("windchill_f"),
        col("current.heatindex_c").alias("heatindex_c"),
        col("current.heatindex_f").alias("heatindex_f"),
        col("current.dewpoint_c").alias("dewpoint_c"),
        col("current.dewpoint_f").alias("dewpoint_f"),
        col("current.uv").alias("uv"),
        col("current.gust_mph").alias("gust_mph"),
        col("current.gust_kph").alias("gust_kph"),
    ).dropna()

    # 4. Write clean records to Postgres
    clean_df.withColumn("raw_id", col("raw_id").cast("string")) \
    .withColumn("id", expr("uuid()")) \
    .write.jdbc(
        url=JDBC_URL,
        table="clean_weather",
        mode="append",
        properties={**JDBC_PROPS, "stringtype": "unspecified"}
    )

    # 5. Mark raw records as processed
    raw_ids = [row["id"] for row in raw_df.select("id").collect()]

    async def mark_processed():
        await init_db()
        async with AsyncSessionLocal() as session:
            for raw_id in raw_ids:
                await mark_raw_as_processed(session, uuid.UUID(str(raw_id)))

    asyncio.run(mark_processed())

    print(f"✅ Transformed and loaded {clean_df.count()} records to clean_weather.")
    spark.stop()


if __name__ == "__main__":
    run_transform()