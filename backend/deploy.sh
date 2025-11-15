#!/bin/bash

# Harrison's Medical RAG - Google Cloud Run Deployment Script
# Project: flingoos-bridge

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🚀 Deploying Harrison's Medical RAG to Google Cloud Run    ║"
echo "╔════════════════════════════════════════════════════════════════╗"
echo ""

# Configuration
PROJECT_ID="flingoos-bridge"
SERVICE_NAME="harrisons-medical-rag"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "📋 Configuration:"
echo "   Project: ${PROJECT_ID}"
echo "   Service: ${SERVICE_NAME}"
echo "   Region: ${REGION}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✓ gcloud CLI found"

# Set project
echo "🔧 Setting GCP project..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "🔧 Enabling required APIs (if not already enabled)..."
gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com --quiet

# Build and push Docker image for AMD64 (Cloud Run requirement)
echo ""
echo "🐳 Building Docker image for AMD64/linux (Cloud Run compatible)..."
docker buildx build --platform linux/amd64 -t ${IMAGE_NAME}:latest --push .

echo ""
echo "✅ Image built and pushed to Google Container Registry"

# Load API key from .env file
if [ -f .env ]; then
    source .env
    echo "✓ Loaded environment variables from .env"
else
    echo "⚠️  Warning: .env file not found. OpenAI API key may not be set."
fi

# Deploy to Cloud Run
echo ""
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "OPENAI_API_KEY=${OPENAI_API_KEY}"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ DEPLOYMENT COMPLETE!                     ║"
echo "╔════════════════════════════════════════════════════════════════╗"
echo ""
echo "📍 Your application is now live at:"
echo ""

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
echo "   🌐 URL: ${SERVICE_URL}"
echo "   📱 Web Interface: ${SERVICE_URL}/web"
echo "   📚 API Docs: ${SERVICE_URL}/docs"
echo ""
echo "✅ HTTPS enabled automatically (no certificate errors!)"
echo "✅ Access from anywhere (iPhone, Watch, Chrome, etc.)"
echo ""
echo "🧪 Test it now in Chrome:"
echo "   ${SERVICE_URL}/web"
echo ""

