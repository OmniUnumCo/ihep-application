# Health Insight Ventures - GCP Serverless Migration

This directory contains all the necessary files and configurations to migrate your Health Insight Ventures platform to Google Cloud Platform using a serverless architecture.

## 🏗️ Architecture Overview

**Frontend**: React SPA → Cloud Storage + Cloud CDN  
**Backend**: Express.js → Cloud Functions (Node.js 20)  
**Database**: PostgreSQL → BigQuery  
**Infrastructure**: Manual → Terraform (IaC)  

## 📁 Directory Structure

```
gcp/
├── terraform/           # Infrastructure as Code
│   └── main.tf         # GCP resources definition
├── functions/          # Cloud Functions backend
│   ├── index.ts        # API endpoints
│   ├── package.json    # Dependencies
│   └── tsconfig.json   # TypeScript config
├── bigquery/           # Database schema
│   └── schema.sql      # BigQuery tables
├── deploy.sh           # One-click deployment script
├── migration-guide.md  # Detailed migration guide
├── frontend-build.yaml # Frontend deployment config
├── backend-deploy.yaml # Backend deployment config
└── README.md          # This file
```

## 🚀 Quick Start

### Prerequisites
- Google Cloud CLI installed and authenticated
- Terraform installed (v1.5+)
- Node.js 20+ installed
- BigQuery CLI tools

### One-Click Deployment
```bash
# Make the script executable
chmod +x gcp/deploy.sh

# Run deployment (replace with your project ID)
./gcp/deploy.sh your-gcp-project-id
```

### Manual Deployment
See `migration-guide.md` for step-by-step instructions.

## 🔑 Required API Keys

After deployment, set these in Google Secret Manager:

1. **OPENAI_API_KEY** - For AI-powered wellness tips
2. **SENDGRID_API_KEY** - For email notifications  
3. **TWILIO_ACCOUNT_SID** - For SMS and video calls
4. **TWILIO_AUTH_TOKEN** - Twilio authentication
5. **TWILIO_PHONE_NUMBER** - Your Twilio phone number

```bash
# Example: Setting OpenAI API key
echo -n "sk-your-openai-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
```

## 💰 Cost Estimation

### Monthly costs for moderate usage:
- **Cloud Functions**: $10-50 (1M requests)
- **BigQuery**: $20-100 (1TB processed)
- **Cloud Storage**: $5-20 (frontend hosting)
- **Cloud CDN**: $10-30 (global distribution)
- **Total**: ~$45-200/month

## 🔒 Security Features

- **HIPAA Compliance**: Audit logging, encryption at rest/transit
- **IAM**: Fine-grained access control
- **Secret Manager**: Secure API key storage
- **VPC**: Network isolation (optional)

## 📊 Monitoring

Access your application metrics:
- **Cloud Monitoring**: Function performance, errors
- **Cloud Logging**: Application and audit logs
- **BigQuery**: Query analytics and costs

## 🌐 Production Endpoints

After deployment and DNS setup:
- **Main Website**: `https://ihep.app`
- **API Endpoint**: `https://api.ihep.app`
- **Backup/Secondary**: `https://backup.ihep.app`

## 🔄 CI/CD Pipeline

Automated deployment via Cloud Build:
```bash
# Trigger build from repository
gcloud builds submit --config=cloudbuild.yaml .
```

## 📞 Support

- [Migration Guide](./migration-guide.md) - Detailed instructions
- [GCP Documentation](https://cloud.google.com/docs)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)

## 🎯 Next Steps

1. **Run deployment script**
2. **Set API keys in Secret Manager**
3. **Configure custom domain** (optional)
4. **Set up monitoring alerts**
5. **Test all features**
6. **Update DNS** to point to new deployment