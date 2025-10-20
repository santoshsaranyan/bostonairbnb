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

CMD ["/bin/sh", "-c", "\
    echo 'Running Task: datascraper.py' && python datascraper.py || { echo 'Failure: Task datascraper.py Failed'; exit 1; } && \
    echo 'Running Task: datapreprocessor.py' && python datapreprocessor.py || { echo 'Failure: Task datapreprocessor.py Failed'; exit 1; } && \
    echo 'Running Task: dbbronzeloader.py' && python dbbronzeloader.py || { echo 'Failure: Task dbbronzeloader.py Failed'; exit 1; } && \
    echo 'Running Task: dbsilverloader.py' && python dbsilverloader.py || { echo 'Failure: Task dbsilverloader.py Failed'; exit 1; } && \
    echo 'Running Task: dbgoldrefresh.py' && python dbgoldrefresh.py || { echo 'Failure: Task dbgoldrefresh.py Failed'; exit 1; } \
"]