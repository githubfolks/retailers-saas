# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install build dependencies (needed for prophet, psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    python3-dev \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set pip to use cache mounts for faster subsequent builds
# Install heavy ML dependencies first (rarely change)
COPY requirements-ml.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --default-timeout=1000 -r requirements-ml.txt

# Install base application dependencies
COPY requirements-base.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements-base.txt

# Copy the rest of the application
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
