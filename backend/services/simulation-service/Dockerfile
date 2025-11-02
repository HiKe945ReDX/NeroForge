FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .
RUN mkdir -p logs

# Environment
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

EXPOSE 8080

# NO HEALTHCHECK - Cloud Run handles readiness
# NO LONG STARTUP - Fast graceful startup only
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--timeout-keep-alive", "65"]
