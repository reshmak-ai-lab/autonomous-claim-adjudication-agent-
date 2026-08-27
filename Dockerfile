FROM python:3.10-slim

# ------------------------------------------------------------
# Environment
# ------------------------------------------------------------

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app


# ------------------------------------------------------------
# System dependencies
# ------------------------------------------------------------

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*


# ------------------------------------------------------------
# Python dependencies
# ------------------------------------------------------------

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# ------------------------------------------------------------
# Application
# ------------------------------------------------------------

COPY . .


# ------------------------------------------------------------
# Runtime directories
# ------------------------------------------------------------

RUN mkdir -p \
    /app/data/uploads \
    /app/data/runtime \
    /app/vectorstore


# ------------------------------------------------------------
# Non-root user
# ------------------------------------------------------------

RUN useradd \
    --create-home \
    --shell /bin/bash \
    appuser \
    && chown -R appuser:appuser /app

USER appuser


# ------------------------------------------------------------
# Port
# ------------------------------------------------------------

EXPOSE 8000


# ------------------------------------------------------------
# Health check
# ------------------------------------------------------------

HEALTHCHECK \
    --interval=30s \
    --timeout=10s \
    --start-period=20s \
    --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1


# ------------------------------------------------------------
# Start application
# ------------------------------------------------------------
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
