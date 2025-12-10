# IHEP Next.js - Google Cloud Deployment

## Prerequisites

- Google Cloud Project: `gen-lang-client-0928975904`
- Workload Identity Pool configured
- Service Account: `github-actions-sa@gen-lang-client-0928975904.iam.gserviceaccount.com`
- Artifact Registry repository: `us-docker.pkg.dev/gen-lang-client-0928975904/ihep`

## Deployment Configuration

### Environments

| Environment | Branch | Cloud Run Service | Resources |
|-------------|--------|------------------|-----------|
| Development | `dev` | `ihep-web-dev` | 512Mi RAM, 1 CPU |
| Staging | `CI` | `ihep-web-staging` | 512Mi RAM, 1 CPU |
| Production | `production` | `ihep-web-production` | 1Gi RAM, 2 CPU |

### Workload Identity Federation

The deployment uses Workload Identity Federation instead of service account keys for enhanced security.

**Provider**: `projects/934473355501/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider`

**Service Account**: `github-actions-sa@gen-lang-client-0928975904.iam.gserviceaccount.com`

## Quick Start

### Local Development

1. Copy environment variables:
   ```bash
   cp .env.example .env.local
   ```

2. Update `.env.local` with your values

3. Install dependencies:
   ```bash
   npm install
   ```

4. Run development server:
   ```bash
   npm run dev
   ```

### Deploy to Development

Push to the `dev` branch:
```bash
git checkout dev
git merge main
git push origin dev
```

The workflow will automatically:
1. Build the Docker image
2. Push to Artifact Registry
3. Deploy to Cloud Run (`ihep-web-dev`)

### Deploy to Staging

Push to the `CI` branch:
```bash
git checkout CI
git merge main
git push origin CI
```

### Deploy to Production

Push to the `production` branch:
```bash
git checkout production
git merge main
git push origin production
```

## Environment Variables

### Required for Deployment

These are configured in the workflow files:
- `PROJECT_ID`: gen-lang-client-0928975904
- `REGION`: us-central1
- `SERVICE_NAME`: ihep-web-{env}

### Required for Application

Set these in Cloud Run service environment variables:

```bash
# Example: Set NEXTAUTH_SECRET for production
gcloud run services update ihep-web-production \
  --project gen-lang-client-0928975904 \
  --region us-central1 \
  --set-env-vars "NEXTAUTH_SECRET=your-secret-here"
```

Or use the Google Cloud Console → Cloud Run → Service → Variables & Secrets

## Dockerfile

The application uses Next.js standalone output for optimized Docker images:

- **Base Image**: node:20-alpine
- **Output**: Next.js standalone server
- **Port**: 5000 (configurable via PORT env var)
- **Build**: Multi-stage with separate deps/build/runtime layers

## Troubleshooting

### Build Failures

Check the GitHub Actions logs for detailed error messages.

### Deployment Failures

1. Verify Cloud Run service exists:
   ```bash
   gcloud run services describe ihep-web-dev \
     --project gen-lang-client-0928975904 \
     --region us-central1
   ```

2. Check service logs:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=ihep-web-dev" \
     --project gen-lang-client-0928975904 \
     --limit 50
   ```

### Local Docker Testing

Build and test the Docker image locally:

```bash
# Build
docker build -t ihep-test .

# Run
docker run -p 5000:5000 \
  -e NEXTAUTH_SECRET=test-secret \
  ihep-test

# Test
curl http://localhost:5000
```

## Next Steps

1. Configure environment variables in Cloud Run
2. Set up custom domain (optional)
3. Configure CI/CD monitoring and alerts
4. Set up Cloud CDN (optional for static assets)
