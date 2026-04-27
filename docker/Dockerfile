FROM apache/airflow:3.2.1-python3.11

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-17-jre-headless curl && \
    apt-get autoremove -yqq --purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -L https://jdbc.postgresql.org/download/postgresql-42.7.2.jar -o /opt/airflow/postgresql-42.7.2.jar

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

USER airflow

# FAB auth manager is now a separate package in Airflow 3.x
RUN pip install pyspark httpx psycopg2-binary apache-airflow-providers-fab