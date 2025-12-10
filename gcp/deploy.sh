#!/bin/bash

# Health Insight Ventures - GCP Deployment Script
set -e

PROJECT_ID=${1:-"ihep-app"}
REGION="us-central1"

echo "🚀 Starting deployment for Health Insight Ventures to GCP..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"

# Set the project
gcloud config set project $PROJECT_ID

echo "📦 Step 1: Deploying infrastructure with Terraform..."
cd gcp/terraform

# Initialize Terraform
terraform init

# Plan infrastructure
terraform plan -var="project_id=$PROJECT_ID" -var="region=$REGION"

# Apply infrastructure
terraform apply -var="project_id=$PROJECT_ID" -var="region=$REGION" -auto-approve

echo "✅ Infrastructure deployed successfully!"

cd ../..

echo "🗄️ Step 2: Setting up BigQuery schema..."
# Apply BigQuery schema
bq query --use_legacy_sql=false < gcp/bigquery/schema.sql

echo "✅ BigQuery schema applied successfully!"

echo "☁️ Step 3: Deploying Cloud Functions..."
# Deploy backend functions
gcloud builds submit --config=gcp/backend-deploy.yaml .

echo "✅ Cloud Functions deployed successfully!"

echo "🌐 Step 4: Building and deploying React frontend..."
# Deploy frontend
gcloud builds submit --config=gcp/frontend-build.yaml .

echo "✅ Frontend deployed successfully!"

echo "🔐 Step 5: Setting up secrets..."
echo "Please manually set the following secrets in Google Secret Manager:"
echo "- OPENAI_API_KEY"
echo "- SENDGRID_API_KEY"
echo "- TWILIO_ACCOUNT_SID"
echo "- TWILIO_AUTH_TOKEN"
echo "- TWILIO_PHONE_NUMBER"

echo ""
echo "🎉 Deployment completed successfully!"
echo "🌍 Your application is now available at:"
echo "   Frontend: https://storage.googleapis.com/ihep-app-health-insight-frontend/index.html"
echo "   API: https://us-central1-ihep-app.cloudfunctions.net/health-insight-api"
echo ""
echo "📋 Next steps:"
echo "1. Set up the required API keys in Secret Manager"
echo "2. Configure your custom domain (optional)"
echo "3. Set up monitoring and alerting"
echo "4. Configure SSL certificate for custom domain"