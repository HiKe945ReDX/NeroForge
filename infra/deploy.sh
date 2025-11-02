#!/bin/bash
set -e

PROJECT="guidora-main"
REGION="us-central1"

echo "🚀 Deploying Guidora Platform..."

# Backend
cd ../../backend
docker build -t gcr.io/$PROJECT/guidora-backend:latest .
docker push gcr.io/$PROJECT/guidora-backend:latest
gcloud run deploy guidora-backend --image gcr.io/$PROJECT/guidora-backend:latest --project $PROJECT --region $REGION --port 8080 --allow-unauthenticated --memory 512Mi --quiet

# Frontend
cd ../frontend
docker build -t gcr.io/$PROJECT/guidora-frontend:latest .
docker push gcr.io/$PROJECT/guidora-frontend:latest
gcloud run deploy guidora-frontend --image gcr.io/$PROJECT/guidora-frontend:latest --project $PROJECT --region $REGION --memory 512Mi --port 80 --allow-unauthenticated --quiet

echo "✅ Live at https://guidora-frontend-746485305795.us-central1.run.app"
