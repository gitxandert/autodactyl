FROM python:3.13-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./

# Default envs
ENV UVICORN_HOST=0.0.0.0 UVICORN_PORT=8000
CMD ["sh", "-c", "python -m uvicorn main:app --host ${UVICORN_HOST} --port ${UVICORN_PORT}"]

