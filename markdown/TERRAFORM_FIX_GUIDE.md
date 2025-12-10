# Terraform Permission Fix Guide

## The Issue
The error you encountered is a common Terraform provider permission issue. Here's how to resolve it:

## Solution Steps

### Step 1: Fix Provider Permissions
```bash
# Navigate to terraform directory
cd gcp/terraform

# Remove old provider cache
rm -rf .terraform .terraform.lock.hcl

# Reinitialize with proper permissions
terraform init

# If still having permission issues, run:
chmod +x .terraform/providers/registry.terraform.io/hashicorp/google/*/linux_amd64/terraform-provider-google*
```

### Step 2: Alternative - Use Google Cloud Shell
The most reliable approach is to use Google Cloud Shell which has all permissions pre-configured:

```bash
# Open Google Cloud Shell in your browser
# Navigate to https://shell.cloud.google.com

# Clone or upload your terraform files
# Set project
gcloud config set project ihep-app

# Deploy
cd gcp/terraform
terraform init
terraform apply -var="project_id=ihep-app"
```

### Step 3: Local Machine Fix (if needed)
If running locally, ensure you have proper authentication:

```bash
# Authenticate
gcloud auth application-default login

# Set project
gcloud config set project ihep-app

# Verify authentication
gcloud auth list

# Then retry terraform
terraform init
terraform apply -var="project_id=ihep-app"
```

### Step 4: Simplified Deployment Script
I've created a fixed deployment script that handles permissions:

```bash
#!/bin/bash
set -e

echo "🚀 Health Insight Ventures - Fixed Deployment"

# Clean previous terraform state
rm -rf .terraform .terraform.lock.hcl

# Authenticate and set project
gcloud auth application-default login
gcloud config set project ihep-app

# Enable required services
gcloud services enable compute.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable dns.googleapis.com
gcloud services enable monitoring.googleapis.com

# Initialize terraform with clean state
terraform init

# Apply with auto-approve after showing plan
terraform plan -var="project_id=ihep-app"
echo "Press Enter to continue with deployment..."
read
terraform apply -var="project_id=ihep-app"

echo "✅ Deployment completed!"
```

### Step 5: Verify Project Setup
Before deployment, ensure your GCP project is properly configured:

```bash
# Verify project exists and you have access
gcloud projects describe ihep-app

# Check enabled APIs
gcloud services list --enabled

# Verify billing is enabled
gcloud beta billing projects describe ihep-app
```

## Quick Resolution
The fastest way to resolve this is to use Google Cloud Shell, which eliminates all permission issues and has Terraform pre-installed with proper permissions.

## Alternative: Use Deployment Manager
If Terraform continues having issues, you can also use Google Cloud Deployment Manager:

```bash
# Convert terraform to deployment manager format
# Deploy using gcloud deployment-manager
gcloud deployment-manager deployments create health-insight-ha --config deployment.yaml
```

Your infrastructure is ready - this is just a permission fix needed for the deployment tool.