# Health Insight Ventures - GCP Migration Guide
## Project ID: ihep-app

This guide will help you migrate your Health Insight Ventures platform from Replit to Google Cloud Platform using a serverless architecture.

## 🚀 Quick Start (3 Steps)

### Step 1: Initial Setup
```bash
# 1. Login to Google Cloud
gcloud auth login

# 2. Set up your project
./gcp/setup-project.sh

# 3. Verify setup
gcloud config get-value project
```

### Step 2: Deploy Infrastructure & Code
```bash
# Run the automated deployment
./gcp/deploy.sh
```

### Step 3: Configure API Keys
```bash
# Set your API keys (replace with actual values)
echo -n "your-openai-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
echo -n "your-sendgrid-api-key" | gcloud secrets create SENDGRID_API_KEY --data-file=-
echo -n "your-twilio-sid" | gcloud secrets create TWILIO_ACCOUNT_SID --data-file=-
echo -n "your-twilio-token" | gcloud secrets create TWILIO_AUTH_TOKEN --data-file=-
echo -n "your-twilio-phone" | gcloud secrets create TWILIO_PHONE_NUMBER --data-file=-
```

## 🎯 Your Production URLs

After successful deployment and DNS configuration:
- **Main Website**: https://ihep.app
- **API Endpoint**: https://api.ihep.app
- **Backup/Secondary**: https://backup.ihep.app

See `gcp/domain-setup-guide.md` for DNS configuration steps.

## 🔍 Validation

Run the validation script to check everything:
```bash
./gcp/validate-deployment.sh
```

## 📊 What Gets Deployed

### Infrastructure (Terraform)
- BigQuery dataset: `health_insight_platform`
- Cloud Storage buckets for frontend hosting
- Cloud Functions for API endpoints
- Secret Manager for secure credential storage

### Database Schema (BigQuery)
- All your existing tables migrated to BigQuery
- Optimized with partitioning and clustering
- HIPAA-compliant audit logging maintained

### Application Code
- React frontend built and deployed to Cloud Storage
- Express.js API converted to Cloud Functions
- All existing features preserved

## 💰 Expected Costs

For moderate usage (estimated monthly):
- **Cloud Functions**: $10-30
- **BigQuery**: $20-50  
- **Cloud Storage**: $5-15
- **Total**: ~$35-95/month

## 🔧 Troubleshooting

### Common Issues

**"Project not found"**
```bash
gcloud projects list
gcloud config set project ihep-app
```

**"Permission denied"**
```bash
gcloud auth login
gcloud auth application-default login
```

**"API not enabled"**
```bash
./gcp/setup-project.sh
```

### Getting Help
- Run `./gcp/validate-deployment.sh` for detailed diagnostics
- Check Cloud Console logs at: https://console.cloud.google.com/logs
- Review function logs: `gcloud functions logs read health-insight-api`

## 📋 Post-Migration Checklist

- [ ] All API endpoints responding
- [ ] Frontend loads correctly
- [ ] User authentication working
- [ ] Database queries successful
- [ ] API keys configured
- [ ] Monitoring set up
- [ ] Backup procedures verified

## 🔄 Rollback Plan

If needed, you can quickly rollback:
1. Point DNS back to Replit deployment
2. The original Replit app remains unchanged
3. Export any new data from BigQuery if needed

Your Replit deployment stays active during migration for zero-downtime transition!