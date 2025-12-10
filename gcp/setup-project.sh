#!/bin/bash

# Health Insight Ventures - GCP Project Setup
# This script sets up the initial GCP project configuration

set -e

PROJECT_ID="gen-lang-client-0928975904"
REGION="us-central1"

echo "🚀 Setting up GCP project: $PROJECT_ID"

# Set the project
echo "📋 Setting active project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudfunctions.googleapis.com \
                       bigquery.googleapis.com \
                       secretmanager.googleapis.com \
                       cloudbuild.googleapis.com \
                       storage.googleapis.com \
                       firebase.googleapis.com \
                       firestore.googleapis.com \
                       monitoring.googleapis.com \
                       logging.googleapis.com

echo "✅ APIs enabled successfully!"

# Create service account for deployment
echo "🔐 Creating deployment service account..."
gcloud iam service-accounts create health-insight-deploy \
    --display-name="Health Insight Deployment Service Account" \
    --description="Service account for deploying Health Insight Ventures"

# Grant necessary permissions
echo "🔑 Granting permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:health-insight-deploy@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudfunctions.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:health-insight-deploy@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:health-insight-deploy@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:health-insight-deploy@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.admin"

echo "✅ Project setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Run: ./gcp/deploy.sh"
echo "2. Set up your API keys in Secret Manager"
echo "3. Test the deployment"
echo ""
echo "🔗 Useful commands:"
echo "gcloud auth login                     # Login to GCP"
echo "gcloud config list                    # Check current config"
echo "gcloud projects list                  # List your projects"