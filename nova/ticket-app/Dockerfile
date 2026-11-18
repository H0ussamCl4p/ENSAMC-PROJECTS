# Minimal Dockerfile to run Flask dashboard with Waitress
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (build tools if any wheels need compiling)
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt ./
RUN pip install -r requirements.txt

# App code
COPY . ./

# Default port for Cloud Run; can be overridden by platform setting PORT
ENV PORT=8080
EXPOSE 8080

# Run via Waitress, binding to 0.0.0.0 and respecting $PORT
CMD ["sh", "-c", "waitress-serve --host 0.0.0.0 --port ${PORT:-8080} dashboard:app"]
