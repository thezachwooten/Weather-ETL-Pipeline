# Use the official Airflow image as a starting point
FROM apache/airflow:2.8.1-python3.11

# Switch to root to install Java (needed for PySpark)
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-17-jre-headless curl && \
    apt-get autoremove -yqq --purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download the Postgres JDBC driver so Spark can connect to your DB
RUN curl -L https://jdbc.postgresql.org/download/postgresql-42.7.2.jar -o /opt/airflow/postgresql-42.7.2.jar

# CORRECT WAY: Use ENV. It sets the variable AND exports it automatically.
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Switch back to the airflow user
USER airflow

# Install PySpark and any other libs you need
RUN pip install pyspark httpx psycopg2-binary