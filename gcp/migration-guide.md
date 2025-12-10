# Health Insight Ventures - GCP Migration Guide

## Overview
This guide walks you through migrating the Health Insight Ventures platform to Google Cloud Platform using a serverless architecture with React frontend and BigQuery database.

## Architecture Overview

### Current (Replit)
- **Frontend**: React with Vite build system
- **Backend**: Express.js server 
- **Database**: PostgreSQL with Drizzle ORM
- **Hosting**: Replit platform

### Target (GCP Serverless)
- **Frontend**: React SPA hosted on Cloud Storage
- **Backend**: Cloud Functions (Node.js 20)
- **Database**: BigQuery for analytics and data storage
- **CDN**: Cloud CDN for global distribution
- **Infrastructure**: Terraform for IaC

## Prerequisites

1. **Google Cloud Project**
   - Create a new GCP project
   - Enable billing
   - Install Google Cloud CLI

2. **Required Tools**
   - `gcloud` CLI tool
   - `terraform` (v1.5+)
   - `bq` command line tool
   - Node.js 20+

3. **API Keys**
   - OpenAI API key
   - SendGrid API key
   - Twilio credentials (Account SID, Auth Token, Phone Number)

## Migration Steps

### Step 1: Set up GCP Project
```bash
# Set your project ID
export PROJECT_ID="your-health-insight-project"

# Login and set project
gcloud auth login
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com
```

### Step 2: Deploy Infrastructure
```bash
# Navigate to terraform directory
cd gcp/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var="project_id=$PROJECT_ID"

# Apply infrastructure
terraform apply -var="project_id=$PROJECT_ID"
```

### Step 3: Set up BigQuery
```bash
# Create dataset and tables
bq query --use_legacy_sql=false < ../bigquery/schema.sql
```

### Step 4: Configure Secrets
```bash
# Set API keys in Secret Manager
echo -n "your-openai-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
echo -n "your-sendgrid-api-key" | gcloud secrets create SENDGRID_API_KEY --data-file=-
echo -n "your-twilio-sid" | gcloud secrets create TWILIO_ACCOUNT_SID --data-file=-
echo -n "your-twilio-token" | gcloud secrets create TWILIO_AUTH_TOKEN --data-file=-
echo -n "your-twilio-phone" | gcloud secrets create TWILIO_PHONE_NUMBER --data-file=-
```

### Step 5: Deploy Cloud Functions
```bash
# Deploy backend API
gcloud builds submit --config=gcp/backend-deploy.yaml .
```

### Step 6: Deploy Frontend
```bash
# Build and deploy React app
gcloud builds submit --config=gcp/frontend-build.yaml .
```

## Data Migration

### PostgreSQL to BigQuery
1. **Export existing data** from PostgreSQL
2. **Transform data** to match BigQuery schema
3. **Load data** using `bq load` command

```bash
# Example data load
bq load --source_format=CSV health_insight_platform.users users.csv
```

## Configuration Updates

### Frontend Environment Variables
Update `client/.env.production`:
```
VITE_API_BASE_URL=https://us-central1-PROJECT_ID.cloudfunctions.net/health-insight-api
VITE_ENVIRONMENT=production
```

### Backend Configuration
Cloud Functions automatically inject:
- Project ID
- BigQuery dataset connection
- Secret Manager access

## Monitoring & Logging

### Cloud Monitoring
- Function invocations
- Error rates
- Latency metrics

### Cloud Logging
- Application logs
- Audit logs for HIPAA compliance

## Cost Optimization

### Cloud Functions
- Use minimum instances for consistent performance
- Set appropriate memory allocation
- Implement proper caching

### BigQuery
- Partition tables by date
- Use clustering for frequently queried columns
- Monitor query costs

### Cloud Storage
- Use appropriate storage classes
- Enable lifecycle policies
- Implement CDN caching

## Security Considerations

### HIPAA Compliance
- Enable audit logging
- Use VPC for network isolation
- Encrypt data at rest and in transit
- Regular security reviews

### Access Control
- Use IAM roles for fine-grained permissions
- Enable Cloud Security Command Center
- Regular vulnerability assessments

## Backup & Disaster Recovery

### BigQuery
- Automatic backups enabled
- Cross-region replication
- Point-in-time recovery

### Cloud Storage
- Versioning enabled
- Cross-region backup buckets
- Automated backup scripts

## Performance Testing

### Load Testing
```bash
# Use Cloud Load Testing or Artillery.js
artillery quick --count 100 --num 10 https://your-frontend-url
```

### Monitoring
- Set up alerting for high error rates
- Monitor function cold starts
- Track BigQuery query performance

## Rollback Plan

### Quick Rollback
1. Revert DNS to original Replit deployment
2. Disable new Cloud Functions
3. Restore data from backups if needed

### Full Rollback
1. Export data from BigQuery
2. Restore PostgreSQL database
3. Redeploy to Replit platform

## Post-Migration Checklist

- [ ] All endpoints responding correctly
- [ ] Data integrity verified
- [ ] SSL certificates configured
- [ ] Monitoring alerts set up
- [ ] Backup procedures tested
- [ ] Performance benchmarks met
- [ ] Security scan completed
- [ ] Documentation updated

## Troubleshooting

### Common Issues
1. **Function timeout**: Increase timeout in deployment config
2. **BigQuery quota**: Request quota increase
3. **CORS errors**: Update Cloud Function CORS settings
4. **Secret access**: Verify IAM permissions

### Support Resources
- [GCP Documentation](https://cloud.google.com/docs)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
- [Cloud Functions Troubleshooting](https://cloud.google.com/functions/docs/troubleshooting)