# IHEP VPC Infrastructure - Quick Start Guide

## 🚀 Quick Deployment (5 Minutes)

### Prerequisites
- GCP account with billing enabled
- Project ID: `gen-lang-client-0928975904`
- gcloud CLI installed and authenticated
- Terraform 1.5+ installed

### One-Command Deployment

```bash
cd /Users/nexus1/Documents/ihep-app/ihep/gcp
export PROJECT_ID="gen-lang-client-0928975904"
export REGION="us-central1"
export ENVIRONMENT="prod"
chmod +x deploy-vpc-infrastructure.sh
./deploy-vpc-infrastructure.sh
```

That's it! The script will:
1. ✅ Check prerequisites
2. ✅ Enable required GCP APIs
3. ✅ Create terraform.tfvars
4. ✅ Initialize Terraform
5. ✅ Deploy VPC infrastructure
6. ✅ Output connection details

## 📋 What Gets Deployed

### Network Infrastructure
- **VPC Network**: `ihep-vpc` (10.0.0.0/16)
- **5 Subnets**: Frontend, Backend, Data, Proxy, GKE
- **Cloud Router + NAT**: For outbound internet access
- **Firewall Rules**: 6 security rules configured

### Data Layer
- **Cloud SQL PostgreSQL**: Primary + Read Replica
  - Version: PostgreSQL 15
  - Size: 2 vCPUs, 8 GB RAM (primary)
  - High Availability enabled
  - Private IP only

- **Memorystore Redis**: Standard HA
  - Version: Redis 7.0
  - Memory: 5 GB
  - Auth + Encryption enabled

- **Healthcare API**: FHIR Store R4
  - HIPAA-compliant
  - BigQuery streaming
  - Pub/Sub notifications

### Security
- **Cloud Armor**: WAF with OWASP rules
- **VPC Flow Logs**: All subnets monitored
- **Private Service Connection**: For managed services
- **SSL/TLS**: Required for all connections

## 🔑 Post-Deployment Configuration

### 1. Set API Keys (Required)

```bash
# OpenAI API Key
echo -n "sk-your-openai-key" | gcloud secrets versions add OPENAI_API_KEY --data-file=-

# SendGrid API Key
echo -n "<YOUR_SENDGRID_API_KEY>" | gcloud secrets versions add SENDGRID_API_KEY --data-file=-

# Twilio Credentials
echo -n "AC..." | gcloud secrets versions add TWILIO_ACCOUNT_SID --data-file=-
echo -n "your-token" | gcloud secrets versions add TWILIO_AUTH_TOKEN --data-file=-
echo -n "+1234567890" | gcloud secrets versions add TWILIO_PHONE_NUMBER --data-file=-
```

### 2. Get Database Connection Info

```bash
cd terraform
terraform output postgres_private_ip
terraform output redis_host
terraform output fhir_store_id
```

### 3. Connect to Cloud SQL

```bash
# Using Cloud SQL Proxy
gcloud sql connect ihep-postgres-prod --user=ihep_app

# Connection string is stored in Secret Manager
gcloud secrets versions access latest --secret=IHEP_DB_CONNECTION_STRING
```

## 📊 Verify Deployment

### Check VPC Network
```bash
gcloud compute networks describe ihep-vpc
gcloud compute networks subnets list --network=ihep-vpc
```

### Check Firewall Rules
```bash
gcloud compute firewall-rules list --filter="network:ihep-vpc"
```

### Check Cloud SQL
```bash
gcloud sql instances list
gcloud sql instances describe ihep-postgres-prod
```

### Check Redis
```bash
gcloud redis instances list
gcloud redis instances describe ihep-redis-prod --region=us-central1
```

### Check Cloud NAT
```bash
gcloud compute routers describe ihep-router --region=us-central1
gcloud compute routers nats describe ihep-nat --router=ihep-router --region=us-central1
```

## 💰 Cost Summary

**Estimated Monthly Cost: $605-800**

| Resource | Cost |
|----------|------|
| Cloud SQL (Primary + Replica) | $320-370 |
| Memorystore Redis | $150-180 |
| Cloud NAT | $30-50 |
| Load Balancer + Cloud Armor | $25-40 |
| VPC Flow Logs | $20-40 |
| Healthcare API | $50-100 |

### Cost Optimization for Dev/Staging

Edit `terraform/terraform.tfvars`:
```hcl
db_tier           = "db-custom-1-3840"  # Reduce to 1 vCPU, 3.75 GB
redis_tier        = "BASIC"             # Disable HA
db_ha_enabled     = false               # Disable HA
```

**Estimated Dev Cost: $200-300/month (60% savings)**

## 🔧 Customization

### Change Region
```bash
export REGION="us-east1"
export ZONE="us-east1-b"
./deploy-vpc-infrastructure.sh
```

### Modify Resources

Edit `terraform/terraform.tfvars`:
```hcl
# Increase database size
db_tier = "db-custom-4-16384"  # 4 vCPUs, 16 GB RAM

# Increase Redis memory
redis_memory_size_gb = 10

# Scale Cloud Run
min_instances = 2
max_instances = 20
```

Apply changes:
```bash
cd terraform
terraform plan
terraform apply
```

## 🛡️ Security Checklist

- [x] VPC Flow Logs enabled
- [x] Cloud Armor WAF configured
- [x] Private IPs only for data layer
- [x] SSL/TLS required
- [x] Firewall rules configured
- [x] Cloud NAT for outbound access
- [ ] Update API keys in Secret Manager
- [ ] Configure VPC Service Controls (optional)
- [ ] Set up monitoring alerts
- [ ] Review IAM permissions

## 📈 Monitoring

### View VPC Flow Logs
```bash
gcloud logging read 'resource.type="gce_subnetwork"' \
  --limit=50 \
  --format=json
```

### View Cloud SQL Metrics
```bash
# Open Cloud Console
gcloud sql instances describe ihep-postgres-prod --format="value(connectionName)"
```

### View Redis Metrics
```bash
gcloud redis instances describe ihep-redis-prod \
  --region=us-central1 \
  --format="value(host,port)"
```

## 🚨 Troubleshooting

### Issue: Cannot connect to Cloud SQL
```bash
# Check private service connection
gcloud services vpc-peerings list --network=ihep-vpc

# Verify Cloud SQL instance is running
gcloud sql instances describe ihep-postgres-prod --format="value(state)"

# Check firewall rules
gcloud compute firewall-rules list --filter="network:ihep-vpc AND name~backend-to-data"
```

### Issue: Cloud NAT not working
```bash
# Check NAT configuration
gcloud compute routers nats describe ihep-nat --router=ihep-router --region=us-central1

# View NAT logs
gcloud logging read 'resource.type="nat_gateway"' --limit=10
```

### Issue: Deployment failed
```bash
# Check Terraform state
cd terraform
terraform show

# View detailed error
terraform plan

# Re-initialize if needed
rm -rf .terraform
terraform init
```

## 🔄 Cleanup (Warning: Destroys All Resources!)

```bash
cd terraform
terraform destroy
```

⚠️ **This will delete**:
- VPC Network and all subnets
- Cloud SQL instances (backups retained for 7 days)
- Redis instances
- Healthcare API datasets
- All firewall rules and routes

## 📚 Additional Resources

- [Full Architecture Documentation](./VPC_NETWORK_ARCHITECTURE.md)
- [Terraform Variables Reference](./terraform/variables.tf)
- [Deployment Script Source](./deploy-vpc-infrastructure.sh)
- [Google Cloud VPC Best Practices](https://cloud.google.com/vpc/docs/best-practices)

## 🆘 Support

For issues or questions:
1. Check [VPC_NETWORK_ARCHITECTURE.md](./VPC_NETWORK_ARCHITECTURE.md)
2. Review Terraform logs: `cd terraform && terraform show`
3. Check GCP Console: [Console](https://console.cloud.google.com)
4. Contact: support@ihep.app

## ✅ Next Steps

1. ✅ Deploy VPC infrastructure (you just did this!)
2. ⬜ Configure API keys in Secret Manager
3. ⬜ Deploy frontend application (Cloud Run)
4. ⬜ Deploy backend services (Cloud Run)
5. ⬜ Configure custom domain and SSL
6. ⬜ Set up monitoring and alerts
7. ⬜ Run security compliance scan
8. ⬜ Configure CI/CD pipeline

---

**Deployment Time**: ~15-20 minutes
**Cost**: $605-800/month (production) | $200-300/month (dev/staging)
**HIPAA Compliant**: ✅ Yes (with BAA from Google)
