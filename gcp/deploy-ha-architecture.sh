#!/bin/bash

# Health Insight Ventures - High Availability Deployment Script
set -e

PROJECT_ID="ihep-app"
REGION="us-central1"

echo "🚀 Starting High Availability deployment for Health Insight Ventures"
echo "Project: $PROJECT_ID | Region: $REGION"
echo "Architecture: Multi-zone with 6 load balancers and database cluster"

# Set project
gcloud config set project $PROJECT_ID

echo "📋 Phase 1: Infrastructure Setup"
cd gcp/terraform

# Initialize Terraform
terraform init

echo "🏗️ Phase 2: Deploying Base Infrastructure"
echo "Creating VPC network and subnets..."
terraform apply -target=google_compute_network.vpc_network -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_subnetwork.web_subnet_us_central1_a -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_subnetwork.web_subnet_us_central1_b -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_subnetwork.app_subnet_us_central1_a -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_subnetwork.app_subnet_us_central1_b -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_subnetwork.db_subnet_us_central1_a -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_subnetwork.db_subnet_us_central1_b -var="project_id=$PROJECT_ID" -auto-approve

echo "🔒 Deploying firewall rules..."
terraform apply -target=google_compute_firewall.allow_http_https -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_firewall.allow_app_tier -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_firewall.allow_db_tier -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_firewall.allow_health_checks -var="project_id=$PROJECT_ID" -auto-approve

echo "🗄️ Phase 3: Database Cluster Deployment"
echo "Creating primary PostgreSQL instance (this may take 10-15 minutes)..."
terraform apply -target=google_sql_database_instance.postgres_primary -var="project_id=$PROJECT_ID" -auto-approve

echo "Waiting for primary database to be ready..."
sleep 300

echo "Creating read replica..."
terraform apply -target=google_sql_database_instance.postgres_replica -var="project_id=$PROJECT_ID" -auto-approve

echo "⚙️ Phase 4: Service Accounts"
terraform apply -target=google_service_account.web_server_sa -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_service_account.app_server_sa -var="project_id=$PROJECT_ID" -auto-approve

echo "🖥️ Phase 5: Instance Templates and Groups"
echo "Creating web server template and group..."
terraform apply -target=google_compute_instance_template.web_server_template -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_region_instance_group_manager.web_server_group -var="project_id=$PROJECT_ID" -auto-approve

echo "Creating application server template and group..."
terraform apply -target=google_compute_instance_template.app_server_template -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_region_instance_group_manager.app_server_group -var="project_id=$PROJECT_ID" -auto-approve

echo "⚖️ Phase 6: Load Balancers"
echo "Creating health checks..."
terraform apply -target=google_compute_health_check.web_health_check -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_health_check.app_health_check -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_region_health_check.app_health_check_regional -var="project_id=$PROJECT_ID" -auto-approve

echo "Creating backend services..."
terraform apply -target=google_compute_backend_service.web_backend_primary -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_backend_service.web_backend_secondary -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_region_backend_service.app_backend_primary -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_region_backend_service.app_backend_secondary -var="project_id=$PROJECT_ID" -auto-approve

echo "Creating SSL certificate..."
terraform apply -target=google_compute_managed_ssl_certificate.web_ssl -var="project_id=$PROJECT_ID" -auto-approve

echo "Deploying global load balancers (Internet → Web Servers)..."
terraform apply -target=google_compute_global_forwarding_rule.web_lb_primary -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_global_forwarding_rule.web_lb_primary_https -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_global_forwarding_rule.web_lb_secondary -var="project_id=$PROJECT_ID" -auto-approve

echo "Deploying internal load balancers (Web → App Servers)..."
terraform apply -target=google_compute_forwarding_rule.app_lb_primary -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_forwarding_rule.app_lb_secondary -var="project_id=$PROJECT_ID" -auto-approve

echo "📈 Phase 7: Auto-scaling Configuration"
terraform apply -target=google_compute_region_autoscaler.web_server_autoscaler -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_compute_region_autoscaler.app_server_autoscaler -var="project_id=$PROJECT_ID" -auto-approve

echo "🛡️ Phase 8: Security and Monitoring"
terraform apply -target=google_compute_security_policy.security_policy -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_monitoring_uptime_check_config.primary_lb_check -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_monitoring_uptime_check_config.secondary_lb_check -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_monitoring_alert_policy.high_error_rate -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_monitoring_notification_channel.email -var="project_id=$PROJECT_ID" -auto-approve

echo "🎯 Phase 9: DNS and Domain Configuration"
echo "Setting up ihep.app domain..."
terraform apply -target=google_dns_managed_zone.ihep_app_zone -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_dns_record_set.root_a -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_dns_record_set.www_a -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_dns_record_set.api_a -var="project_id=$PROJECT_ID" -auto-approve
terraform apply -target=google_dns_record_set.backup_cname -var="project_id=$PROJECT_ID" -auto-approve

echo "🔧 Phase 10: Final Configuration"
echo "Applying any remaining resources..."
terraform apply -var="project_id=$PROJECT_ID" -auto-approve

cd ../..

# Get deployment information
PRIMARY_LB_IP=$(cd gcp/terraform && terraform output -raw primary_load_balancer_ip)
SECONDARY_LB_IP=$(cd gcp/terraform && terraform output -raw secondary_load_balancer_ip)

echo ""
echo "✅ High Availability Deployment Completed!"
echo "=================================================="
echo ""
echo "🌐 Your Production URLs:"
echo "   Main Site:    https://ihep.app"
echo "   API Endpoint: https://api.ihep.app"
echo "   Backup:       https://backup.ihep.app"
echo ""
echo "🌐 Load Balancer IPs:"
echo "   Primary:   $PRIMARY_LB_IP (Port 80/443)"
echo "   Secondary: $SECONDARY_LB_IP (Port 8080)"
echo ""
echo "📊 Architecture Summary:"
echo "   • Web Servers: 4-10 instances (auto-scaling)"
echo "   • App Servers: 6-15 instances (auto-scaling)"  
echo "   • Load Balancers: 6 (2 external + 4 internal)"
echo "   • Database: Regional cluster with read replica"
echo "   • Zones: us-central1-a, us-central1-b"
echo ""
echo "🌍 Domain Setup Required:"
echo "   Configure nameservers with your domain registrar:"
terraform output dns_nameservers
echo ""
echo "🔐 Next Steps - Set API Keys:"
echo "   echo -n 'your-key' | gcloud secrets create OPENAI_API_KEY --data-file=-"
echo "   echo -n 'your-key' | gcloud secrets create SENDGRID_API_KEY --data-file=-"
echo "   echo -n 'your-sid' | gcloud secrets create TWILIO_ACCOUNT_SID --data-file=-"
echo "   echo -n 'your-token' | gcloud secrets create TWILIO_AUTH_TOKEN --data-file=-"
echo "   echo -n 'your-phone' | gcloud secrets create TWILIO_PHONE_NUMBER --data-file=-"
echo ""
echo "📋 Monitoring Dashboard:"
echo "   https://console.cloud.google.com/monitoring/dashboards"
echo ""
echo "🧪 Test Your Deployment:"
echo "   ./gcp/validate-deployment.sh"
echo ""
echo "📚 Full Documentation:"
echo "   See DETAILED_DEPLOYMENT_GUIDE.md"
echo ""
echo "🎉 Your enterprise-grade healthcare platform is ready!"