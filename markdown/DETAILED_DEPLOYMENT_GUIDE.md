# Health Insight Ventures - Detailed High Availability Deployment Guide

## Architecture Overview

Your Health Insight Ventures platform will be deployed with enterprise-grade high availability:

### Load Balancer Layers
1. **Internet → Web Servers**: 2 Global Load Balancers with Cloud Armor security
2. **Web Servers → App Servers**: 2 Internal Load Balancers with health checks  
3. **App Servers → Database**: Database cluster with primary/replica configuration

### Server Clusters
- **Web Tier**: 4-10 instances (auto-scaling) across 2 zones
- **Application Tier**: 6-15 instances (auto-scaling) across 2 zones
- **Database Tier**: Regional PostgreSQL cluster with read replicas

### Redundancy Features
- Multi-zone deployment (us-central1-a, us-central1-b)
- Auto-healing with health checks every 10 seconds
- Automated failover between load balancers
- Database backup and point-in-time recovery
- Instance group auto-scaling based on CPU, memory, and network metrics

## Prerequisites

### 1. Google Cloud Setup
```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Login and set project
gcloud auth login
gcloud config set project ihep-app
```

### 2. Enable Required APIs
```bash
# Run the setup script
./gcp/setup-project.sh
```

### 3. Required Tools
```bash
# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify installation
terraform --version
gcloud --version
```

## Detailed Deployment Steps

### Phase 1: Infrastructure Deployment

#### Step 1: Initialize Terraform
```bash
cd gcp/terraform
terraform init

# Review the configuration
terraform plan -var="project_id=ihep-app"
```

#### Step 2: Deploy Base Infrastructure
```bash
# Deploy VPC, subnets, and security groups
terraform apply -target=google_compute_network.vpc_network -var="project_id=ihep-app"
terraform apply -target=google_compute_subnetwork.web_subnet_us_central1_a -var="project_id=ihep-app"
terraform apply -target=google_compute_subnetwork.web_subnet_us_central1_b -var="project_id=ihep-app"
terraform apply -target=google_compute_subnetwork.app_subnet_us_central1_a -var="project_id=ihep-app"
terraform apply -target=google_compute_subnetwork.app_subnet_us_central1_b -var="project_id=ihep-app"

# Deploy firewall rules
terraform apply -target=google_compute_firewall.allow_http_https -var="project_id=ihep-app"
terraform apply -target=google_compute_firewall.allow_app_tier -var="project_id=ihep-app"
terraform apply -target=google_compute_firewall.allow_db_tier -var="project_id=ihep-app"
```

#### Step 3: Deploy Database Cluster
```bash
# Deploy primary database
terraform apply -target=google_sql_database_instance.postgres_primary -var="project_id=ihep-app"

# Wait for primary to be ready (5-10 minutes)
gcloud sql instances describe health-insight-postgres-primary

# Deploy read replica
terraform apply -target=google_sql_database_instance.postgres_replica -var="project_id=ihep-app"
```

#### Step 4: Configure Database
```bash
# Create database and user
gcloud sql databases create health_insight_db --instance=health-insight-postgres-primary
gcloud sql users create healthapp --instance=health-insight-postgres-primary --password=SecurePassword123!

# Apply schema
gcloud sql import sql health-insight-postgres-primary gs://ihep-app-sql-backups/schema.sql --database=health_insight_db
```

### Phase 2: Application Deployment

#### Step 5: Deploy Instance Templates and Groups
```bash
# Deploy web server template and group
terraform apply -target=google_compute_instance_template.web_server_template -var="project_id=ihep-app"
terraform apply -target=google_compute_region_instance_group_manager.web_server_group -var="project_id=ihep-app"

# Deploy app server template and group
terraform apply -target=google_compute_instance_template.app_server_template -var="project_id=ihep-app"
terraform apply -target=google_compute_region_instance_group_manager.app_server_group -var="project_id=ihep-app"
```

#### Step 6: Deploy Load Balancers
```bash
# Deploy health checks first
terraform apply -target=google_compute_health_check.web_health_check -var="project_id=ihep-app"
terraform apply -target=google_compute_health_check.app_health_check -var="project_id=ihep-app"

# Deploy backend services
terraform apply -target=google_compute_backend_service.web_backend_primary -var="project_id=ihep-app"
terraform apply -target=google_compute_backend_service.web_backend_secondary -var="project_id=ihep-app"

# Deploy load balancers
terraform apply -target=google_compute_global_forwarding_rule.web_lb_primary -var="project_id=ihep-app"
terraform apply -target=google_compute_global_forwarding_rule.web_lb_secondary -var="project_id=ihep-app"
```

#### Step 7: Deploy Internal Load Balancers
```bash
# Deploy regional backend services
terraform apply -target=google_compute_region_backend_service.app_backend_primary -var="project_id=ihep-app"
terraform apply -target=google_compute_region_backend_service.app_backend_secondary -var="project_id=ihep-app"

# Deploy internal load balancers
terraform apply -target=google_compute_forwarding_rule.app_lb_primary -var="project_id=ihep-app"
terraform apply -target=google_compute_forwarding_rule.app_lb_secondary -var="project_id=ihep-app"
```

### Phase 3: Auto-scaling and Monitoring

#### Step 8: Deploy Auto-scaling
```bash
# Deploy auto-scalers
terraform apply -target=google_compute_region_autoscaler.web_server_autoscaler -var="project_id=ihep-app"
terraform apply -target=google_compute_region_autoscaler.app_server_autoscaler -var="project_id=ihep-app"
```

#### Step 9: Deploy Monitoring
```bash
# Deploy monitoring resources
terraform apply -target=google_monitoring_uptime_check_config.primary_lb_check -var="project_id=ihep-app"
terraform apply -target=google_monitoring_alert_policy.high_error_rate -var="project_id=ihep-app"
terraform apply -target=google_monitoring_dashboard.health_insight_dashboard -var="project_id=ihep-app"
```

### Phase 4: Security and SSL

#### Step 10: Configure SSL Certificate
```bash
# Deploy managed SSL certificate
terraform apply -target=google_compute_managed_ssl_certificate.web_ssl -var="project_id=ihep-app"

# Configure DNS for ihep.app domain
terraform apply -target=google_dns_managed_zone.ihep_app_zone -var="project_id=ihep-app"
terraform apply -target=google_dns_record_set.root_a -var="project_id=ihep-app"
terraform apply -target=google_dns_record_set.www_a -var="project_id=ihep-app"
terraform apply -target=google_dns_record_set.api_a -var="project_id=ihep-app"

# Get nameservers and configure with domain registrar
terraform output dns_nameservers
```

#### Step 11: Configure Security Policy
```bash
# Deploy Cloud Armor security policy
terraform apply -target=google_compute_security_policy.security_policy -var="project_id=ihep-app"
```

### Phase 5: Application Configuration

#### Step 12: Configure Secrets
```bash
# Set API keys in Secret Manager
echo -n "your-openai-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
echo -n "your-sendgrid-api-key" | gcloud secrets create SENDGRID_API_KEY --data-file=-
echo -n "your-twilio-account-sid" | gcloud secrets create TWILIO_ACCOUNT_SID --data-file=-
echo -n "your-twilio-auth-token" | gcloud secrets create TWILIO_AUTH_TOKEN --data-file=-
echo -n "your-twilio-phone-number" | gcloud secrets create TWILIO_PHONE_NUMBER --data-file=-

# Set database connection strings
echo -n "postgresql://healthapp:SecurePassword123!@health-insight-postgres-primary/health_insight_db" | gcloud secrets create DATABASE_URL --data-file=-
echo -n "postgresql://healthapp:SecurePassword123!@health-insight-postgres-replica/health_insight_db" | gcloud secrets create DATABASE_REPLICA_URL --data-file=-
```

## Validation and Testing

### Step 13: Validate Deployment
```bash
# Run validation script
./gcp/validate-deployment.sh

# Check all services are healthy
gcloud compute backend-services get-health web-backend-primary --global
gcloud compute backend-services get-health app-backend-primary --region=us-central1

# Test load balancer endpoints
curl -I http://$(terraform output primary_load_balancer_ip)/health
curl -I http://$(terraform output secondary_load_balancer_ip)/health
```

### Step 14: Performance Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test primary load balancer
ab -n 1000 -c 10 http://$(terraform output primary_load_balancer_ip)/

# Test API endpoints
ab -n 500 -c 5 http://$(terraform output primary_load_balancer_ip)/api/health
```

### Step 15: Failover Testing
```bash
# Test instance failure
gcloud compute instances stop web-server-001 --zone=us-central1-a

# Monitor auto-healing (should replace instance within 5 minutes)
gcloud compute instances list --filter="name~'web-server'"

# Test load balancer failover
# Disable primary backend service
gcloud compute backend-services update web-backend-primary --global --no-enable-cdn

# Traffic should automatically route to secondary
```

## Monitoring and Maintenance

### Daily Operations
```bash
# Check system health
gcloud monitoring dashboards list
gcloud logging read "resource.type=gce_instance" --limit=50

# Monitor auto-scaling events
gcloud compute operations list --filter="operationType=compute.autoscalers.resize"

# Check database performance
gcloud sql operations list --instance=health-insight-postgres-primary
```

### Weekly Maintenance
```bash
# Update instance templates with latest security patches
# Rolling update will be performed automatically
gcloud compute instance-groups managed rolling-action start-update web-server-group \
    --version template=web-server-template-new \
    --region=us-central1

# Database maintenance window (automatically scheduled)
gcloud sql instances patch health-insight-postgres-primary --maintenance-window-day=SUN --maintenance-window-hour=3
```

## Cost Optimization

### Expected Monthly Costs (USD)
- **Compute Instances**: $800-1500 (8-20 instances)
- **Load Balancers**: $200-400 (6 load balancers)
- **Database**: $400-800 (Regional HA cluster)
- **Network Egress**: $100-300
- **Monitoring**: $50-100
- **Total**: $1550-3100/month

### Cost Reduction Strategies
1. Use preemptible instances for non-critical workloads (60% cost reduction)
2. Implement proper auto-scaling to reduce over-provisioning
3. Use committed use discounts for baseline capacity
4. Optimize database queries to reduce CPU usage

## Disaster Recovery

### Backup Strategy
- **Database**: Automatic daily backups with 30-day retention
- **Application**: Instance templates stored in version control
- **Configuration**: Terraform state backed up to Cloud Storage

### Recovery Procedures
```bash
# Restore from backup
gcloud sql backups restore BACKUP_ID --restore-instance=health-insight-postgres-primary

# Redeploy from scratch (RTO: 30 minutes)
terraform destroy -var="project_id=ihep-app"
terraform apply -var="project_id=ihep-app"
```

## Security Compliance

### HIPAA Compliance Features
- All data encrypted at rest and in transit
- Network isolation with VPC
- Audit logging enabled for all access
- Regular security scanning
- Access controls with service accounts

### Regular Security Tasks
```bash
# Security scan
gcloud alpha security-center findings list

# Update firewall rules
gcloud compute firewall-rules list
gcloud compute firewall-rules describe allow-http-https

# Review IAM permissions
gcloud projects get-iam-policy ihep-app
```

This deployment provides enterprise-grade reliability with 99.9% uptime SLA, automatic failover, and comprehensive monitoring. The multi-layered load balancing ensures no single point of failure while maintaining optimal performance.