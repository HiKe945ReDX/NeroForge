#!/bin/bash
set -e

echo "🚀 DEPLOYING GUIDORA TO GOOGLE CLOUD - ALL SERVICES"

# Set project
gcloud config set project guidora-main

# Deploy Frontend
echo "📱 DEPLOYING FRONTEND..."
cd ~/main/frontend
gcloud run deploy guidora-frontend \
  --source . \
  --port 8080 \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --platform managed \
  --project guidora-main

# Deploy API Gateway
echo "🔌 DEPLOYING API GATEWAY..."
cd ~/main/backend/services/api-gateway  
gcloud run deploy guidora-api \
  --source . \
  --port 3000 \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --timeout 300 \
  --project guidora-main \
  --set-env-vars="NODE_ENV=production,MONGODB_URL=mongodb+srv://guidora_admin:Sris0945@sris0945.yim8u.mongodb.net/guidora_db?retryWrites=true&w=majority&appName=Sris0945"

# Deploy AI Service  
echo "🤖 DEPLOYING AI SERVICE..."
cd ~/main/backend/services/ai-guidance
gcloud run deploy guidora-ai \
  --source . \
  --port 5002 \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --project guidora-main \
  --set-env-vars="GEMINI_API_KEY=AIzaSyDTDLfzkAzJEbqdFkR2jT9sbIITi0xsepA,MONGODB_URL=mongodb+srv://guidora_admin:Sris0945@sris0945.yim8u.mongodb.net/guidora_db?retryWrites=true&w=majority&appName=Sris0945"

# Deploy User Service
echo "👤 DEPLOYING USER SERVICE..."
cd ~/main/backend/services/user-service
gcloud run deploy guidora-users \
  --source . \
  --port 5001 \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --project guidora-main \
  --set-env-vars="MONGODB_URL=mongodb+srv://guidora_admin:Sris0945@sris0945.yim8u.mongodb.net/guidora_db?retryWrites=true&w=majority&appName=Sris0945,JWT_SECRET=guidora_super_secure_jwt_secret_key_2025_very_long_at_least_32_characters"

echo "✅ ALL SERVICES DEPLOYED!"
echo "🌟 Your URLs:"
gcloud run services list --platform managed --region us-central1
