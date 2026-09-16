FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy model artifacts and backend source code
COPY models/ ./models/
COPY backend/ ./backend/

ENV PYTHONPATH=/app/backend:/app
ENV MERIDIAN_MODEL_DIR=/app/models

# Cloud Run injects $PORT dynamically (default 8080).
# We use `sh -c` to allow variable expansion.
EXPOSE 8080

CMD ["sh", "-c", "uvicorn layer1.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
