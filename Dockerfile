# Use lightweight Python 3.10 base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system utilities needed for building packages and performing health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download en_core_web_sm \
    && python -m spacy download en_core_web_lg

# Copy all application code
COPY . .

# Expose standard FastAPI application port
EXPOSE 8000

# Health check to verify application readiness
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/docs || exit 1

# Start FastAPI server using uvicorn binding to all network interfaces
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
