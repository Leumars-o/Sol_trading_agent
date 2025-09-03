# Dockerfile for Analyzer Service
# analyzer_service/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY config.py .
COPY env_validator.py .
COPY telegram_utils.py .
COPY ai_service/ ai_service/

WORKDIR /app/ai_service
CMD ["python", "ai_token_screener.py"]
