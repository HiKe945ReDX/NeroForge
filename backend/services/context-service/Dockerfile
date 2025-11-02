FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p logs

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
EXPOSE 8080

# Health check for local Docker
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=2 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["uvicorn", "src.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8080", \
     "--timeout-keep-alive", "65"]
