# Dockerfile for WebSocket Service
# websocket_service/Dockerfile
FROM python:3.9-slim

# set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy the content of the program files to the working directory
COPY config.py .
COPY transactions.py .
COPY env_validator.py .
COPY telegram_utils.py .
COPY websocket_service/ websocket_service/

WORKDIR /app/websocket_service
CMD ["python", "main.py"]
