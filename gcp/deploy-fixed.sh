#!/bin/bash

# Health Insight Ventures - Fixed Deployment Script
set -e

PROJECT_ID="ihep-app"
REGION="us-central1"

echo "🚀 Health Insight Ventures - Fixed HA Deployment"
echo "Project: $PROJECT_ID | Region: $REGION"
echo "Fixing Terraform permissions and deploying..."

# Authenticate and set project
echo "📋 Setting up authentication..."
gcloud config set project $PROJECT_ID

# Clean previous terraform state to fix permission issues
echo "🧹 Cleaning previous terraform state..."
rm -rf .terraform .terraform.lock.hcl

# Enable required services
echo "⚙️ Enabling required GCP services..."
gcloud services enable compute.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable dns.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Initialize terraform with clean state
echo "🔧 Initializing Terraform..."
terraform init

# Validate configuration
echo "✅ Validating Terraform configuration..."
terraform validate

# Show plan
echo "📋 Showing deployment plan..."
terraform plan -var="project_id=$PROJECT_ID"

# Apply deployment
echo "🚀 Starting deployment..."
terraform apply -var="project_id=$PROJECT_ID" -auto-approve

# Get outputs
echo "📊 Getting deployment outputs..."
PRIMARY_LB_IP=$(terraform output -raw primary_load_balancer_ip 2>/dev/null || echo "Not available yet")
SECONDARY_LB_IP=$(terraform output -raw secondary_load_balancer_ip 2>/dev/null || echo "Not available yet")
DNS_NAMESERVERS=$(terraform output -raw dns_nameservers 2>/dev/null || echo "Not available yet")

echo ""
echo "✅ Deployment Completed Successfully!"
echo "============================================"
echo ""
echo "🌐 Your Production URLs:"
echo "   Main Site:    https://ihep.app"
echo "   API Endpoint: https://api.ihep.app"
echo "   Backup:       https://backup.ihep.app"
echo ""
echo "🌐 Load Balancer IPs:"
echo "   Primary:   $PRIMARY_LB_IP"
echo "   Secondary: $SECONDARY_LB_IP"
echo ""
echo "🌍 DNS Nameservers (configure with domain registrar):"
echo "$DNS_NAMESERVERS"
echo ""
echo "🔐 Next Steps - Set API Keys:"
echo "   echo -n 'your-key' | gcloud secrets create OPENAI_API_KEY --data-file=-"
echo "   echo -n 'your-key' | gcloud secrets create SENDGRID_API_KEY --data-file=-"
echo "   echo -n 'your-sid' | gcloud secrets create TWILIO_ACCOUNT_SID --data-file=-"
echo "   echo -n 'your-token' | gcloud secrets create TWILIO_AUTH_TOKEN --data-file=-"
echo "   echo -n 'your-phone' | gcloud secrets create TWILIO_PHONE_NUMBER --data-file=-"
echo ""
echo "🎉 Your enterprise healthcare platform is deployed!"
echo "DNS propagation takes 24-48 hours, SSL certificates will be ready within 60 minutes after DNS propagation."