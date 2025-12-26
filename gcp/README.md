# IHEP - GCP Cloud Run Deployment

This directory contains configuration and scripts for deploying the IHEP Next.js application to Google Cloud Run.

## Architecture Overview

**Application**: Next.js 16 (App Router) with standalone output
**Runtime**: Cloud Run (serverless containers)
**Database**: BigQuery (analytics) / Cloud SQL (optional for transactional data)
**Secrets**: Google Secret Manager
**Infrastructure**: Terraform (IaC)

## Directory Structure

```
gcp/
├── terraform/              # Infrastructure as Code
│   ├── main.tf            # Core GCP resources
│   ├── vpc-network.tf     # VPC networking
│   ├── ha-architecture.tf # High availability config
│   └── variables.tf       # Terraform variables
├── bigquery/              # Analytics schema
│   └── schema.sql         # BigQuery tables
├── deploy.sh              # One-click Cloud Run deployment
├── frontend-build.yaml    # Cloud Build config for Next.js
├── cloud-run-service.yaml # Cloud Run service spec
└── README.md              # This file
```

## Quick Start

### Prerequisites
- Google Cloud CLI installed and authenticated
- Docker installed (for local testing)
- Node.js 22+ installed

### Local Testing
```bash
# Build Docker image
docker build -t ihep-test .

# Run locally
docker run -p 5000:5000 \
  -e NEXTAUTH_SECRET=test-secret \
  ihep-test

# Test health endpoint
curl http://localhost:5000/api/health
```

### Deploy to GCP
```bash
# From project root directory
chmod +x gcp/deploy.sh
./gcp/deploy.sh

# Or with custom project ID
./gcp/deploy.sh your-project-id
```

The deployment script will:
1. Enable required GCP services
2. Build the Docker image using Cloud Build
3. Push to Google Container Registry
4. Deploy to Cloud Run
5. Configure environment variables

## Required Secrets

Before deploying, create the required secret in Secret Manager:

```bash
# Generate and create NEXTAUTH_SECRET (required)
openssl rand -base64 32 | gcloud secrets create NEXTAUTH_SECRET --data-file=-

# Optional: Database URL
echo -n "postgresql://..." | gcloud secrets create DATABASE_URL --data-file=-
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| NEXTAUTH_SECRET | Yes | JWT encryption secret |
| NEXTAUTH_URL | Auto | Set automatically to Cloud Run URL |
| NODE_ENV | Auto | Set to "production" |
| PORT | Auto | Set to 5000 |
| DATABASE_URL | No | Database connection string |

## Cost Estimation

### Cloud Run (pay per request)
- **CPU**: $0.00002400 per vCPU-second
- **Memory**: $0.00000250 per GiB-second
- **Requests**: $0.40 per million requests

### Estimated monthly costs:
- **Low traffic** (10k requests/day): ~$5-15/month
- **Medium traffic** (100k requests/day): ~$30-100/month
- **High traffic** (1M requests/day): ~$200-500/month

## Monitoring

```bash
# View logs
gcloud run logs read ihep-web --region us-central1 --limit 50

# View service details
gcloud run services describe ihep-web --region us-central1

# View metrics
gcloud run services metrics ihep-web --region us-central1
```

## Production URL

After deployment, your application will be available at:
```
https://ihep-web-XXXXXXXXXX-uc.a.run.app
```

To set up a custom domain:
1. Go to Cloud Run console
2. Select the ihep-web service
3. Click "Manage Custom Domains"
4. Follow the verification steps

## Troubleshooting

### Build Failures
```bash
# Check Cloud Build logs
gcloud builds list --limit 5
gcloud builds log BUILD_ID
```

### Container Startup Issues
```bash
# Check Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

### Health Check Failures
The application exposes `/api/health` for health checks. If probes fail:
1. Check if the container is starting properly
2. Verify environment variables are set
3. Check application logs for errors

## Security

- All traffic is encrypted (TLS)
- Secrets stored in Secret Manager
- Identity-Aware Proxy available for additional auth
- VPC connector available for private networking
- Cloud Armor for DDoS protection (optional)