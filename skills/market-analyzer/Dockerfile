# Market Analyzer - Production Dockerfile
# Target: linux/amd64 (Unraid / x86_64)
FROM python:3.12-slim

LABEL maintainer="Market Analyzer"
LABEL description="Market Analyzer Dashboard - FastAPI trading signals"

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY config.example.json .
COPY strategies.json .
COPY scripts/ ./scripts/

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create data volume mountpoint
VOLUME ["/app/data"]

# Expose port
EXPOSE 8080

# Environment
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["/entrypoint.sh"]
