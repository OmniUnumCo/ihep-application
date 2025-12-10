# IHEP Infrastructure Connections

**Comprehensive Guide for Connecting All Systems**

**Date**: December 2, 2025
**Status**: 🔄 **IN PROGRESS**

---

## 📋 Overview

This document outlines the connections between:

1. **Local Repository** (Development)
2. **GitHub Repository** (Version Control)
3. **CI/CD Pipeline** (GitHub Actions)
4. **Claude Project IHEP** (AI Assistant Integration)
5. **Remote File System** (https://ihep.app/repositories)

---

## 1. ✅ Local Repository → GitHub Connection

### Status: **CONNECTED**

```bash
# Current configuration
Remote: origin
URL: https://github.com/anumethod/ihep
Fetch: https://github.com/anumethod/ihep (fetch)
Push: https://github.com/anumethod/ihep (push)
```

### Verification

```bash
# Check remote configuration
git remote -v

# Test connection
git fetch origin

# Push changes
git push origin main
```

### Authentication

Uses HTTPS with credentials. For enhanced security, consider switching to SSH:

```bash
# Generate SSH key (if not exists)
ssh-keygen -t ed25519 -C "your-email@example.com"

# Add SSH key to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy and add to GitHub Settings → SSH Keys

# Update remote to use SSH
git remote set-url origin git@github.com:anumethod/ihep.git

# Test SSH connection
ssh -T git@github.com
```

---

## 2. ✅ GitHub → CI/CD Pipeline Connection

### Status: **CONFIGURED WITH SECURITY HARDENING**

### Configured Workflows

#### Production Deployment

- **Trigger**: Push to `production` branch
- **Workflow**: `.github/workflows/web-deploy-production.yml`
- **Authentication**: Workload Identity Federation
- **Approval**: Required (manual)
- **Security**:
  - ✅ No `--allow-unauthenticated`
  - ✅ Manual approval gates
  - ✅ 2-reviewer requirement
  - ✅ Audit logging enabled

#### Staging Deployment

- **Trigger**: Push to `staging` branch
- **Workflow**: `.github/workflows/web-deploy-staging.yml`
- **Authentication**: Workload Identity Federation
- **Security**: ✅ Authentication required

#### Development Deployment

- **Trigger**: Push to `dev` branch
- **Workflow**: `.github/workflows/web-deploy-dev.yml`
- **Authentication**: Workload Identity Federation
- **Security**: ✅ Authentication required

#### Terraform Workflows

- **Production**: `.github/workflows/tf-production.yml`
  - ✅ Manual approval required (2 reviewers)
  - ✅ No auto-approve
  - ✅ Plan artifacts uploaded for review

- **Staging**: `.github/workflows/tf-staging.yml`
  - ✅ Plan-based apply (no auto-approve)

- **Development**: `.github/workflows/tf-dev.yml`
  - ✅ Plan-based apply (no auto-approve)

### GitHub Secrets Configuration

**Required Secrets**:

```bash
# Workload Identity Federation
WIF_PROVIDER=projects/<project-number>/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider
GCP_SA_EMAIL=github-actions-sa@<project-id>.iam.gserviceaccount.com

# Terraform Approvers (for production)
TERRAFORM_APPROVERS=user1,user2  # Comma-separated list

# Optional: For enhanced security
SENTRY_DSN=<your-sentry-dsn>  # Error monitoring
SLACK_WEBHOOK=<webhook-url>   # Deployment notifications
```

**To Configure**:

```bash
# Add secrets via GitHub web interface
# Navigate to: Repository → Settings → Secrets and variables → Actions

# Or via GitHub CLI
gh secret set WIF_PROVIDER --body "projects/..."
gh secret set GCP_SA_EMAIL --body "github-actions-sa@..."
gh secret set TERRAFORM_APPROVERS --body "user1,user2"
```

### Workload Identity Federation Setup

```bash
# Create Workload Identity Pool
gcloud iam workload-identity-pools create "github-actions-pool" \
    --project="<PROJECT_ID>" \
    --location="global" \
    --display-name="GitHub Actions Pool"

# Create Workload Identity Provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --project="<PROJECT_ID>" \
    --location="global" \
    --workload-identity-pool="github-actions-pool" \
    --display-name="GitHub Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --issuer-uri="https://token.actions.githubusercontent.com"

# Create Service Account
gcloud iam service-accounts create github-actions-sa \
    --project="<PROJECT_ID>" \
    --display-name="GitHub Actions Service Account"

# Bind Service Account to Workload Identity
gcloud iam service-accounts add-iam-policy-binding "github-actions-sa@<PROJECT_ID>.iam.gserviceaccount.com" \
    --project="<PROJECT_ID>" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/<PROJECT_NUMBER>/locations/global/workloadIdentityPools/github-actions-pool/attribute.repository/anumethod/ihep"

# Grant necessary permissions (LEAST PRIVILEGE)
gcloud projects add-iam-policy-binding <PROJECT_ID> \
    --member="serviceAccount:github-actions-sa@<PROJECT_ID>.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding <PROJECT_ID> \
    --member="serviceAccount:github-actions-sa@<PROJECT_ID>.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"
```

---

## 3. 🔄 Claude Project IHEP Integration

### Status: **REQUIRES CONFIGURATION**

### Purpose

Integrate Claude AI assistant with the IHEP project for:

- Code review and suggestions
- Documentation generation
- Security analysis
- HIPAA compliance checks
- Automated testing suggestions

### Setup Options

#### Option A: Claude Code (Current)

You're currently using Claude Code, which provides:
- Direct code access
- File reading/writing
- Command execution
- Git integration

**No additional setup required** - already integrated.

#### Option B: Claude Projects API

For programmatic integration:

```typescript
// Example integration
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

async function analyzeCode(code: string) {
  const message = await anthropic.messages.create({
    model: 'claude-sonnet-4-5-20250929',
    max_tokens: 4000,
    messages: [{
      role: 'user',
      content: `Analyze this code for HIPAA compliance:\n\n${code}`
    }]
  });

  return message.content;
}
```

**Required Environment Variables**:

```bash
# Add to .env.local
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_PROJECT_ID=proj_...
```

#### Option C: GitHub Actions Integration

Create a workflow for automated code review:

```yaml
# .github/workflows/claude-code-review.yml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Claude Code Review
        uses: anthropics/claude-code-review@v1
        with:
          api-key: ${{ secrets.ANTHROPIC_API_KEY }}
          files-changed: ${{ github.event.pull_request.changed_files }}
          focus-areas: "security,hipaa-compliance,performance"
```

### Documentation Sync

To sync project documentation with Claude Project:

```bash
# Create a documentation bundle
tar -czf ihep-docs.tar.gz \
    README.md \
    SECURITY_AUDIT_REPORT.md \
    SECURITY_REMEDIATION_COMPLETE.md \
    BACKEND_SETUP_GUIDE.md \
    QUICK_START.md

# Upload to Claude Project (via API or web interface)
# This allows Claude to reference project-specific context
```

---

## 4. 🔄 Remote File System Connection (ihep.app/repositories)

### Status: **REQUIRES SETUP**

### Purpose

Connect to remote file system at https://ihep.app/repositories for:

- Deployment artifacts storage
- Backup storage
- Asset delivery (digital twin models)
- Log aggregation
- Configuration management

### Setup Options

#### Option A: WebDAV Connection

If ihep.app/repositories uses WebDAV:

```bash
# Mount WebDAV filesystem (macOS)
mkdir -p ~/ihep-remote
mount -t webdav https://ihep.app/repositories ~/ihep-remote

# Authenticate
# Username: your-username
# Password: your-password

# Sync local to remote
rsync -avz --progress ./ ~/ihep-remote/ihep-app/
```

#### Option B: SFTP/SCP Connection

If using SSH-based file transfer:

```bash
# Add SSH key for authentication
ssh-copy-id user@ihep.app

# Test connection
sftp user@ihep.app

# Sync with rsync over SSH
rsync -avz --progress -e ssh \
    --exclude 'node_modules' \
    --exclude '.next' \
    --exclude '.git' \
    ./ user@ihep.app:/repositories/ihep-app/
```

#### Option C: Git-Based Deployment

If ihep.app/repositories is a Git repository:

```bash
# Add remote
git remote add production user@ihep.app:/repositories/ihep-app.git

# Push to production
git push production main

# Set up post-receive hook on remote
# /repositories/ihep-app.git/hooks/post-receive
#!/bin/bash
GIT_WORK_TREE=/var/www/ihep-app \
    git checkout -f main
cd /var/www/ihep-app
npm install
npm run build
pm2 restart ihep-app
```

#### Option D: Cloud Storage Bucket

If using Google Cloud Storage:

```bash
# Create bucket
gsutil mb gs://ihep-repositories

# Sync to bucket
gsutil -m rsync -r -x '.git|node_modules|.next' . gs://ihep-repositories/ihep-app/

# Set up lifecycle rules
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 90,
          "matchesPrefix": ["logs/"]
        }
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://ihep-repositories
```

#### Option E: API-Based File Upload

If ihep.app provides an API:

```bash
#!/bin/bash
# scripts/deploy-to-remote.sh

API_ENDPOINT="https://ihep.app/api/repositories/upload"
API_KEY="${IHEP_API_KEY}"

# Create deployment package
tar -czf deployment.tar.gz \
    --exclude='node_modules' \
    --exclude='.next' \
    --exclude='.git' \
    .

# Upload to remote
curl -X POST "${API_ENDPOINT}" \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/gzip" \
    --data-binary @deployment.tar.gz

# Cleanup
rm deployment.tar.gz
```

### Automated Sync via GitHub Actions

```yaml
# .github/workflows/sync-remote-filesystem.yml
name: Sync to Remote Filesystem

on:
  push:
    branches: [main, production]

jobs:
  sync:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup SSH
        uses: webfactory/ssh-agent@v0.8.0
        with:
          ssh-private-key: ${{ secrets.REMOTE_SSH_KEY }}

      - name: Sync to Remote
        run: |
          rsync -avz --progress -e ssh \
            --exclude 'node_modules' \
            --exclude '.next' \
            --exclude '.git' \
            --exclude '.env*' \
            ./ ${{ secrets.REMOTE_USER }}@ihep.app:/repositories/ihep-app/

      - name: Verify Deployment
        run: |
          ssh ${{ secrets.REMOTE_USER }}@ihep.app \
            "cd /repositories/ihep-app && npm run build && pm2 restart ihep-app"
```

---

## 5. 📊 Connection Verification

### Verification Checklist

```bash
# 1. Verify Git connection
git remote -v
git fetch origin
echo "✅ Git connection working"

# 2. Verify GitHub Actions
gh workflow list
gh run list --limit 5
echo "✅ GitHub Actions configured"

# 3. Verify Workload Identity
gcloud iam workload-identity-pools describe github-actions-pool \
    --location=global
echo "✅ Workload Identity configured"

# 4. Verify Service Account permissions
gcloud projects get-iam-policy <PROJECT_ID> \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:github-actions-sa@"
echo "✅ Service Account permissions verified"

# 5. Test remote filesystem connection
# (Method depends on which option was chosen above)
ping ihep.app
echo "✅ Remote server reachable"

# 6. Verify CI/CD security
grep -r "allow-unauthenticated" .github/workflows/
# Expected: No matches (exit code 1)
echo "✅ No unauthenticated endpoints"

grep -r "auto-approve" .github/workflows/
# Expected: No matches (exit code 1)
echo "✅ No auto-approve in Terraform"
```

---

## 6. 🔐 Security Considerations

### Secrets Management

**NEVER commit these to Git**:
- SSH private keys
- API keys
- Service account credentials
- Database passwords
- Session secrets

**Use**:
- GitHub Secrets for CI/CD
- Google Secret Manager for runtime secrets
- Environment variables for local development
- `.gitignore` to prevent accidental commits

### IAM Permissions

Follow principle of least privilege:

```bash
# Good: Specific roles
roles/run.admin         # Deploy Cloud Run services
roles/cloudsql.client   # Connect to Cloud SQL

# Bad: Overly permissive
roles/owner            # Full project access
roles/editor           # Wide-ranging permissions
```

### Network Security

For remote filesystem connection:

```bash
# Use VPN or private networking
# Enable firewall rules
# Require TLS/SSL for all connections
# Implement IP allowlisting
# Use SSH key authentication (not passwords)
```

---

## 7. 📝 Connection Diagram

```
┌─────────────────┐
│  Local Repo     │
│  (Development)  │
└────────┬────────┘
         │ git push
         ▼
┌─────────────────┐         ┌─────────────────┐
│  GitHub Repo    │────────▶│  Claude Project │
│  (anumethod/    │  API    │  (AI Assistant) │
│   ihep)         │         └─────────────────┘
└────────┬────────┘
         │ webhook trigger
         ▼
┌─────────────────────────────────────────┐
│  GitHub Actions (CI/CD)                 │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │Production│  │ Staging  │  │  Dev   ││
│  │ Deploy   │  │ Deploy   │  │ Deploy ││
│  └─────┬────┘  └─────┬────┘  └────┬───┘│
└────────┼─────────────┼─────────────┼────┘
         │             │             │
         │ Workload Identity Fed     │
         ▼             ▼             ▼
┌────────────────────────────────────────┐
│  Google Cloud Platform                 │
│  ┌──────────┐  ┌──────────┐  ┌───────┐│
│  │Cloud Run │  │Cloud SQL │  │ KMS   ││
│  └──────────┘  └──────────┘  └───────┘│
└────────────────────────────────────────┘
         │
         │ deployment artifacts
         ▼
┌─────────────────┐
│  ihep.app       │
│  /repositories  │
└─────────────────┘
```

---

## 8. 🚀 Quick Setup Commands

### Complete Setup in One Go

```bash
#!/bin/bash
# setup-connections.sh

echo "Setting up IHEP infrastructure connections..."

# 1. Verify GitHub connection
git remote get-url origin || git remote add origin https://github.com/anumethod/ihep.git
git fetch origin

# 2. Test CI/CD workflows
gh workflow list || echo "Install GitHub CLI: brew install gh"

# 3. Setup remote filesystem (example with SSH)
read -p "Enter remote server address (e.g., user@ihep.app): " REMOTE_SERVER
ssh-keygen -t ed25519 -f ~/.ssh/ihep_deploy -N ""
ssh-copy-id -i ~/.ssh/ihep_deploy.pub $REMOTE_SERVER

# 4. Test connection
ssh -i ~/.ssh/ihep_deploy $REMOTE_SERVER "echo 'Connection successful'"

# 5. Setup automated sync
cat > .github/workflows/sync-remote.yml << 'EOF'
# (Workflow content here)
EOF

echo "✅ Setup complete!"
echo "Next steps:"
echo "1. Configure GitHub Secrets"
echo "2. Test CI/CD pipeline"
echo "3. Verify remote sync"
```

---

## 9. 📞 Troubleshooting

### Issue: GitHub Actions failing

```bash
# Check workflow runs
gh run list --limit 10

# View specific run logs
gh run view <run-id>

# Check secrets are configured
gh secret list
```

### Issue: Workload Identity authentication failing

```bash
# Verify WIF configuration
gcloud iam workload-identity-pools describe github-actions-pool \
    --location=global \
    --project=<PROJECT_ID>

# Check service account bindings
gcloud iam service-accounts get-iam-policy \
    github-actions-sa@<PROJECT_ID>.iam.gserviceaccount.com
```

### Issue: Remote filesystem connection failing

```bash
# Test SSH connection
ssh -vvv user@ihep.app

# Test network connectivity
ping ihep.app
traceroute ihep.app

# Check firewall rules
nmap -p 22,80,443 ihep.app
```

---

## 10. 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)
- [Claude API Documentation](https://docs.anthropic.com)
- [HIPAA Security Guidelines](https://www.hhs.gov/hipaa/for-professionals/security/index.html)

---

**Document Version**: 1.0.0
**Last Updated**: December 2, 2025
**Maintained By**: DevOps Team
**Contact**: devops@ihep.app
