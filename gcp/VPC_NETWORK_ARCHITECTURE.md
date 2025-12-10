# IHEP Healthcare Platform - VPC Network Architecture

## Overview

This document describes the complete VPC network architecture for the IHEP (Integrated Health Engagement Platform) healthcare application. The architecture is designed to be **HIPAA-compliant**, **highly available**, and **secure** while providing excellent performance for healthcare services.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Internet / Users                               │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Cloud Armor (WAF)     │
                    │  - DDoS Protection      │
                    │  - SQL Injection Block  │
                    │  - XSS Prevention       │
                    │  - Rate Limiting        │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   HTTPS Load Balancer   │
                    │   - SSL/TLS Termination │
                    │   - Cloud CDN           │
                    └────────────┬────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────────────────┐
│                              IHEP VPC (10.0.0.0/16)                      │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Frontend Subnet (10.0.1.0/24)                                  │    │
│  │  - Next.js Frontend (Cloud Run)                                 │    │
│  │  - Serverless VPC Connector                                     │    │
│  └────────────────────────┬────────────────────────────────────────┘    │
│                           │                                              │
│  ┌────────────────────────▼────────────────────────────────────────┐    │
│  │  Backend Subnet (10.0.2.0/24)                                   │    │
│  │  - Healthcare API (Cloud Run)                                   │    │
│  │  - Auth Service (Cloud Run)                                     │    │
│  │  - Serverless VPC Connector                                     │    │
│  └────────────────────────┬────────────────────────────────────────┘    │
│                           │                                              │
│  ┌────────────────────────▼────────────────────────────────────────┐    │
│  │  Data Subnet (10.0.3.0/24) - PRIVATE                            │    │
│  │  - Cloud SQL PostgreSQL (Primary)    [Regional HA]              │    │
│  │  - Cloud SQL PostgreSQL (Replica)    [Read-only]                │    │
│  │  - Memorystore Redis                 [Standard HA]               │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  Proxy Subnet (10.0.4.0/24)                                      │    │
│  │  - Load Balancer Proxy Only                                      │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  GKE Subnet (10.0.10.0/24) - OPTIONAL                            │    │
│  │  - GKE Pods:     10.1.0.0/16                                     │    │
│  │  - GKE Services: 10.2.0.0/20                                     │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  Cloud Router + Cloud NAT                                        │    │
│  │  - Outbound internet for private instances                       │    │
│  │  - Access to OpenAI, SendGrid, Twilio APIs                       │    │
│  └──────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   External Services      │
                    │  - OpenAI API            │
                    │  - SendGrid (Email)      │
                    │  - Twilio (SMS/Video)    │
                    │  - Healthcare API (FHIR) │
                    └──────────────────────────┘
```

## Network Components

### 1. VPC Network

- **Name**: `ihep-vpc`
- **IP Range**: `10.0.0.0/16`
- **Routing Mode**: Regional
- **Region**: `us-central1` (configurable)

### 2. Subnets

#### Frontend Subnet
- **CIDR**: `10.0.1.0/24` (254 usable IPs)
- **Purpose**: Cloud Run frontend services
- **Resources**:
  - Next.js application
  - Serverless VPC Access Connector
- **Features**:
  - VPC Flow Logs enabled (50% sampling)
  - Private Google Access enabled
  - Auto-scaling based on traffic

#### Backend Subnet
- **CIDR**: `10.0.2.0/24` (254 usable IPs)
- **Purpose**: Cloud Run backend services
- **Resources**:
  - Healthcare API service
  - Auth Service
  - Serverless VPC Access Connector
- **Features**:
  - VPC Flow Logs enabled (50% sampling)
  - Private Google Access enabled
  - Internal load balancing

#### Data Subnet
- **CIDR**: `10.0.3.0/24` (254 usable IPs)
- **Purpose**: Database and cache layer
- **Resources**:
  - Cloud SQL PostgreSQL (Primary + Replica)
  - Memorystore Redis (Standard HA)
  - Healthcare API FHIR Store (via Private Service Connection)
- **Features**:
  - VPC Flow Logs enabled (100% sampling for compliance)
  - Private Google Access enabled
  - No public IPs (fully private)
  - SSL/TLS required for all connections

#### Proxy Subnet
- **CIDR**: `10.0.4.0/24` (254 usable IPs)
- **Purpose**: Load Balancer proxy-only subnet
- **Features**:
  - Required for internal load balancers
  - Managed by Google

#### GKE Subnet (Optional)
- **CIDR**: `10.0.10.0/24` (254 usable IPs)
- **Pod Secondary Range**: `10.1.0.0/16` (65,536 IPs)
- **Service Secondary Range**: `10.2.0.0/20` (4,096 IPs)
- **Purpose**: GKE cluster (if used instead of Cloud Run)

### 3. Cloud Router & Cloud NAT

- **Router Name**: `ihep-router`
- **NAT Name**: `ihep-nat`
- **Purpose**: Provide outbound internet access for private instances
- **Features**:
  - Automatic IP allocation
  - Logging enabled (errors only)
  - Required for accessing external APIs:
    - OpenAI API
    - SendGrid API
    - Twilio API

### 4. Firewall Rules

#### Allow Load Balancer to Frontend
- **Name**: `ihep-allow-lb-to-frontend`
- **Direction**: Ingress
- **Source**: Load Balancer ranges + Internet (0.0.0.0/0)
- **Target Tags**: `frontend`, `lb-backend`
- **Ports**: 80, 443, 8080
- **Protocol**: TCP

#### Allow Frontend to Backend
- **Name**: `ihep-allow-frontend-to-backend`
- **Direction**: Ingress
- **Source**: Frontend subnet (10.0.1.0/24)
- **Target Tags**: `backend`
- **Ports**: 8080, 8081, 443
- **Protocol**: TCP

#### Allow Backend to Data Layer
- **Name**: `ihep-allow-backend-to-data`
- **Direction**: Ingress
- **Source**: Backend subnet (10.0.2.0/24)
- **Target Tags**: `database`, `cache`
- **Ports**: 5432 (PostgreSQL), 6379 (Redis)
- **Protocol**: TCP

#### Allow Health Checks
- **Name**: `ihep-allow-health-checks`
- **Direction**: Ingress
- **Source**: GCP health check ranges
- **Target Tags**: `frontend`, `backend`, `lb-backend`
- **Ports**: 80, 443, 8080, 8081
- **Protocol**: TCP

#### Allow IAP SSH Access
- **Name**: `ihep-allow-iap-ssh`
- **Direction**: Ingress
- **Source**: IAP range (35.235.240.0/20)
- **Ports**: 22
- **Protocol**: TCP
- **Purpose**: Secure SSH access via Identity-Aware Proxy

#### Deny All Other Traffic
- **Name**: `ihep-deny-all-ingress`
- **Direction**: Ingress
- **Priority**: 65534 (lowest)
- **Action**: Deny all traffic not explicitly allowed

### 5. Private Service Connection

- **Purpose**: Enable private access to Google-managed services
- **IP Range**: Automatically allocated /16 range
- **Services**:
  - Cloud SQL (private IP)
  - Memorystore Redis
  - Healthcare API
  - Other managed services

### 6. Serverless VPC Access Connector

- **Name**: `ihep-serverless-connector`
- **IP Range**: `10.8.0.0/28` (14 usable IPs)
- **Throughput**: 200-1000 Mbps (auto-scaling)
- **Purpose**: Allow Cloud Run and Cloud Functions to access VPC resources

## Security Architecture

### Cloud Armor Security Policy

- **Name**: `ihep-security-policy`
- **Features**:
  - **SQL Injection Protection**: Blocks SQLi attempts using pre-configured rules
  - **XSS Protection**: Blocks cross-site scripting attempts
  - **Rate Limiting**: 1000 requests/minute per IP
  - **Ban Duration**: 10 minutes for rate limit violations
  - **Adaptive Protection**: AI-powered DDoS defense enabled
  - **OWASP Top 10 Protection**: Pre-configured rules

### Network Security

1. **Defense in Depth**:
   - Multiple layers of security (Cloud Armor → Firewall → Private IPs)
   - Default deny all traffic
   - Explicit allow rules only

2. **Zero Trust Architecture**:
   - No public IPs for data layer
   - All traffic authenticated and encrypted
   - Identity-Aware Proxy for admin access

3. **Encryption**:
   - TLS 1.2+ required for all connections
   - Data encrypted at rest (Google-managed keys)
   - Transit encryption for all inter-service communication

4. **Monitoring & Auditing**:
   - VPC Flow Logs enabled on all subnets
   - Cloud Audit Logs enabled (HIPAA requirement)
   - Real-time security monitoring
   - 90-day log retention

## Data Layer Architecture

### Cloud SQL PostgreSQL

#### Primary Instance
- **Type**: Regional (High Availability)
- **Version**: PostgreSQL 15
- **Machine Type**: db-custom-2-8192 (2 vCPU, 8 GB RAM)
- **Disk**: 100 GB SSD (auto-resize enabled)
- **Backups**:
  - Automated daily backups
  - Point-in-time recovery (7 days transaction logs)
  - 30 backup retention
- **Security**:
  - Private IP only (no public IP)
  - SSL/TLS required
  - pgAudit enabled
  - Connection logging enabled
- **Monitoring**:
  - Query Insights enabled
  - Performance monitoring
  - Automatic failover to standby

#### Read Replica
- **Type**: Zonal (Read-only)
- **Machine Type**: db-custom-1-4096 (1 vCPU, 4 GB RAM)
- **Purpose**: Analytics workloads, reporting
- **Features**:
  - Asynchronous replication
  - Can be promoted to primary if needed

### Memorystore Redis

- **Type**: Standard HA (High Availability)
- **Version**: Redis 7.0
- **Memory**: 5 GB (configurable)
- **Features**:
  - Automatic failover
  - In-transit encryption
  - Auth enabled
  - Maxmemory policy: allkeys-lru
- **Purpose**:
  - Session management
  - API response caching
  - Rate limiting data

### Healthcare API Dataset

- **Type**: FHIR Store
- **Version**: FHIR R4
- **Features**:
  - HIPAA-compliant
  - Audit logging
  - Real-time notifications (Pub/Sub)
  - BigQuery streaming for analytics
- **Purpose**:
  - Store patient health records
  - FHIR-compliant data exchange
  - Healthcare interoperability

## Deployment

### Prerequisites

1. **Tools**:
   - gcloud CLI (authenticated)
   - Terraform 1.5+
   - jq (for JSON parsing)

2. **Permissions**:
   - Project Editor or Owner role
   - Compute Admin
   - Service Account Admin

### Deployment Steps

```bash
# 1. Set environment variables
export PROJECT_ID="gen-lang-client-0928975904"
export REGION="us-central1"
export ZONE="us-central1-a"
export ENVIRONMENT="prod"

# 2. Make deployment script executable
chmod +x gcp/deploy-vpc-infrastructure.sh

# 3. Run deployment
cd gcp
./deploy-vpc-infrastructure.sh

# 4. Verify deployment
cd terraform
terraform output
```

### Manual Deployment

```bash
# 1. Navigate to terraform directory
cd gcp/terraform

# 2. Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# 3. Initialize Terraform
terraform init

# 4. Plan deployment
terraform plan -out=tfplan

# 5. Review plan and apply
terraform apply tfplan
```

## Cost Estimation

### Monthly Costs (Production Environment)

| Resource | Configuration | Estimated Cost |
|----------|--------------|----------------|
| Cloud SQL (Primary) | db-custom-2-8192, 100GB SSD, HA | $220-250/month |
| Cloud SQL (Replica) | db-custom-1-4096, 100GB SSD | $100-120/month |
| Memorystore Redis | 5GB Standard HA | $150-180/month |
| Cloud NAT | Data processing + IP allocation | $30-50/month |
| VPC Flow Logs | Storage + analysis | $20-40/month |
| Load Balancer | HTTP(S) LB + forwarding rules | $20-30/month |
| Cloud Armor | Security policy + rules | $5-10/month |
| Serverless Connector | Throughput charges | $10-20/month |
| Healthcare API | FHIR storage + operations | $50-100/month |
| **Total** | | **$605-800/month** |

### Cost Optimization Tips

1. **Development/Staging**:
   - Use smaller machine types (db-g1-small, db-custom-1-3840)
   - Use BASIC tier for Redis (no HA)
   - Disable read replicas
   - Estimated savings: 60-70%

2. **Production**:
   - Enable committed use discounts (up to 57% off)
   - Use preemptible instances for non-critical workloads
   - Implement data lifecycle policies
   - Monitor and optimize query performance

## Operations

### Monitoring

1. **VPC Flow Logs**:
   ```bash
   gcloud logging read 'resource.type="gce_subnetwork"' --limit=50
   ```

2. **Cloud SQL Metrics**:
   - CPU utilization
   - Memory usage
   - Connections
   - Replication lag

3. **Redis Metrics**:
   - Memory usage
   - Calls per second
   - Connected clients
   - Evicted keys

### Backup & Disaster Recovery

1. **Cloud SQL**:
   - Automated daily backups
   - Point-in-time recovery (7 days)
   - Manual backups before major changes
   - Cross-region replication (optional)

2. **Redis**:
   - Automatic persistence (RDB snapshots)
   - Standard HA for automatic failover
   - Manual backups via export

3. **FHIR Data**:
   - BigQuery streaming for analytics
   - GCS export for long-term archival
   - Audit logs for compliance

### Scaling

1. **Vertical Scaling** (Cloud SQL):
   ```bash
   gcloud sql instances patch ihep-postgres-prod \
     --tier=db-custom-4-16384
   ```

2. **Horizontal Scaling** (Cloud Run):
   - Automatic based on traffic
   - Configure in Cloud Run service settings

3. **Redis Scaling**:
   ```bash
   gcloud redis instances update ihep-redis-prod \
     --size=10
   ```

## Security Compliance

### HIPAA Compliance

1. **BAA (Business Associate Agreement)**:
   - Required with Google Cloud
   - Contact Google Cloud sales

2. **Audit Logging**:
   - All data access logged
   - 90-day retention minimum
   - Regular audit reviews

3. **Encryption**:
   - At-rest: Google-managed encryption
   - In-transit: TLS 1.2+
   - Optional: Customer-managed encryption keys (CMEK)

4. **Access Controls**:
   - IAM roles and permissions
   - Identity-Aware Proxy
   - Service account authentication

### Security Best Practices

1. **Network Security**:
   - Private IPs only for data layer
   - Firewall rules audited regularly
   - VPC Service Controls (optional)

2. **Application Security**:
   - Cloud Armor WAF enabled
   - Rate limiting
   - DDoS protection

3. **Data Security**:
   - Encrypted backups
   - Secure key management (Secret Manager)
   - Regular security scanning

## Troubleshooting

### Common Issues

1. **Cannot connect to Cloud SQL**:
   ```bash
   # Check if instance is running
   gcloud sql instances describe ihep-postgres-prod

   # Check VPC peering
   gcloud services vpc-peerings list --network=ihep-vpc

   # Test connection from Cloud Shell
   gcloud sql connect ihep-postgres-prod --user=ihep_app
   ```

2. **Cloud NAT not working**:
   ```bash
   # Check NAT gateway status
   gcloud compute routers nats describe ihep-nat --router=ihep-router --region=us-central1

   # Check logs
   gcloud logging read 'resource.type="nat_gateway"' --limit=50
   ```

3. **Firewall rules not applied**:
   ```bash
   # List firewall rules
   gcloud compute firewall-rules list --filter="network:ihep-vpc"

   # Test connectivity
   gcloud compute instances create test-vm --subnet=ihep-backend-subnet
   ```

## Next Steps

After deploying the VPC infrastructure:

1. **Configure Secrets**:
   - Update Secret Manager with API keys
   - Configure database credentials
   - Set up service account keys

2. **Deploy Applications**:
   - Build and deploy frontend (Cloud Run)
   - Deploy Healthcare API backend
   - Deploy Auth Service

3. **Configure Domain**:
   - Set up DNS records
   - Configure SSL certificates
   - Enable Cloud CDN

4. **Set Up Monitoring**:
   - Create alerting policies
   - Configure uptime checks
   - Set up log-based metrics

5. **Security Hardening**:
   - Enable VPC Service Controls
   - Configure Binary Authorization
   - Implement Secret Rotation

## Support & Documentation

- [Google Cloud VPC Documentation](https://cloud.google.com/vpc/docs)
- [Cloud SQL Best Practices](https://cloud.google.com/sql/docs/postgres/best-practices)
- [HIPAA Compliance on GCP](https://cloud.google.com/security/compliance/hipaa)
- [Cloud Armor Documentation](https://cloud.google.com/armor/docs)

## License

This architecture and code is proprietary to IHEP Healthcare Platform.
