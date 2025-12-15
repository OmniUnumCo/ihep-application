#!/bin/bash

# Health Insight Ventures - Deployment Manager Deploy Script
set -e

PROJECT_ID="ihep-app"
DEPLOYMENT_NAME="health-insight-ha"

echo "🚀 Health Insight Ventures - Deployment Manager Deploy"
echo "Project: $PROJECT_ID | Deployment: $DEPLOYMENT_NAME"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "⚙️ Enabling required APIs..."
gcloud services enable deploymentmanager.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable monitoring.googleapis.com

# Validate deployment configuration
echo "✅ Validating deployment configuration..."
gcloud deployment-manager deployments create $DEPLOYMENT_NAME \
    --config deployment.yaml \
    --preview

# Confirm deployment
echo "📋 Review the preview above. Press Enter to deploy, Ctrl+C to cancel..."
read

# Deploy
echo "🚀 Deploying infrastructure..."
gcloud deployment-manager deployments update $DEPLOYMENT_NAME

# Get deployment info
echo "📊 Getting deployment outputs..."
gcloud deployment-manager deployments describe $DEPLOYMENT_NAME

echo ""
echo "✅ Deployment Completed!"
echo "============================================"
echo ""
echo "🌐 Next steps:"
echo "1. Configure DNS for ihep.app domain"
echo "2. Set up SSL certificates"
echo "3. Add API keys to Secret Manager"
echo "4. Update application configuration"
echo ""
echo "🎉 Your healthcare platform infrastructure is deployed!"