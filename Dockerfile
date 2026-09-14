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

EXPOSE 10000

CMD ["uvicorn", "layer1.main:app", "--host", "0.0.0.0", "--port", "10000"]
