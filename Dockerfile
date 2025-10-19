FROM python:3.10-slim-bookworm

WORKDIR /app/etl_pipeline

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p logs \
    && mkdir -p data/downloads \
    && mkdir -p data/cleaned

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY etl_pipeline/ .

CMD ["/bin/sh", "-c", "python datascraper.py && python datapreprocessor.py && python dbbronzeloader.py && python dbsilverloader.py && python dbgoldrefresh.py"]
