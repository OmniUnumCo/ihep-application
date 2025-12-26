#!/bin/bash

# IHEP - GCP Cloud Run Deployment Script
# Deploys the Next.js application to Google Cloud Run
set -e

PROJECT_ID=${1:-"gen-lang-client-0928975904"}
REGION="us-central1"
SERVICE_NAME="ihep-web"

echo "============================================"
echo "IHEP - GCP Cloud Run Deployment"
echo "============================================"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Set the project
gcloud config set project $PROJECT_ID

# Enable required services
echo "[1/5] Enabling required GCP services..."
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable secretmanager.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet

echo "Services enabled successfully."

# Check if running from project root
if [ ! -f "package.json" ]; then
    echo "Error: Must run from project root directory"
    exit 1
fi

if [ ! -f "Dockerfile" ]; then
    echo "Error: Dockerfile not found in project root"
    exit 1
fi

# Build and deploy using Cloud Build
echo ""
echo "[2/5] Building and deploying Next.js application..."
gcloud builds submit --config=gcp/frontend-build.yaml . \
    --substitutions=_SERVICE_NAME=$SERVICE_NAME,_REGION=$REGION

# Get the service URL
echo ""
echo "[3/5] Getting service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --format 'value(status.url)')

# Set environment secrets (if they exist)
echo ""
echo "[4/5] Configuring environment variables..."

# Check if NEXTAUTH_SECRET exists in Secret Manager
if gcloud secrets describe NEXTAUTH_SECRET --project=$PROJECT_ID >/dev/null 2>&1; then
    echo "Setting NEXTAUTH_SECRET from Secret Manager..."
    gcloud run services update $SERVICE_NAME \
        --region $REGION \
        --set-secrets "NEXTAUTH_SECRET=NEXTAUTH_SECRET:latest" \
        --quiet
else
    echo "Warning: NEXTAUTH_SECRET not found in Secret Manager."
    echo "Create it with: echo -n 'your-secret' | gcloud secrets create NEXTAUTH_SECRET --data-file=-"
fi

# Update NEXTAUTH_URL to the service URL
echo "Setting NEXTAUTH_URL..."
gcloud run services update $SERVICE_NAME \
    --region $REGION \
    --update-env-vars "NEXTAUTH_URL=$SERVICE_URL" \
    --quiet

# Verify deployment
echo ""
echo "[5/5] Verifying deployment..."
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/api/health" || echo "000")

if [ "$HEALTH_CHECK" = "200" ]; then
    echo "Health check passed."
else
    echo "Warning: Health check returned $HEALTH_CHECK (service may still be starting)"
fi

echo ""
echo "============================================"
echo "Deployment Completed Successfully!"
echo "============================================"
echo ""
echo "Application URL: $SERVICE_URL"
echo "Health Check:    $SERVICE_URL/api/health"
echo ""
echo "Required Secrets (set in Secret Manager):"
echo "  - NEXTAUTH_SECRET (required for auth)"
echo "  - DATABASE_URL (optional - for database)"
echo ""
echo "To create NEXTAUTH_SECRET:"
echo "  openssl rand -base64 32 | gcloud secrets create NEXTAUTH_SECRET --data-file=-"
echo ""
echo "To view logs:"
echo "  gcloud run logs read $SERVICE_NAME --region $REGION --limit 50"
echo ""