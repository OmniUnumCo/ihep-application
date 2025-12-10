#!/bin/bash

# ============================================================================
# IHEP Healthcare Platform - VPC Infrastructure Deployment Script
# ============================================================================
# This script deploys the complete VPC network architecture including:
# - VPC Network with multiple subnets
# - Cloud NAT and Cloud Router
# - Firewall rules
# - Cloud SQL PostgreSQL with high availability
# - Memorystore Redis
# - Healthcare API dataset and FHIR store
# - Security policies and monitoring
# ============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# FUNCTIONS
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi

    # Check if terraform is installed
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed. Please install it first."
        exit 1
    fi

    # Check terraform version
    TERRAFORM_VERSION=$(terraform version -json | jq -r '.terraform_version')
    log_info "Terraform version: $TERRAFORM_VERSION"

    # Check if authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        log_error "Not authenticated with gcloud. Run: gcloud auth login"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

set_project() {
    if [ -z "${PROJECT_ID:-}" ]; then
        log_error "PROJECT_ID environment variable is not set"
        log_info "Usage: PROJECT_ID=your-project-id $0"
        exit 1
    fi

    log_info "Setting GCP project to: $PROJECT_ID"
    gcloud config set project "$PROJECT_ID"

    # Verify project exists
    if ! gcloud projects describe "$PROJECT_ID" &> /dev/null; then
        log_error "Project $PROJECT_ID does not exist or you don't have access"
        exit 1
    fi

    log_success "Project set successfully"
}

enable_apis() {
    log_info "Enabling required GCP APIs (this may take a few minutes)..."

    APIS=(
        "compute.googleapis.com"
        "servicenetworking.googleapis.com"
        "vpcaccess.googleapis.com"
        "redis.googleapis.com"
        "sqladmin.googleapis.com"
        "healthcare.googleapis.com"
        "pubsub.googleapis.com"
        "run.googleapis.com"
        "dns.googleapis.com"
        "secretmanager.googleapis.com"
        "cloudresourcemanager.googleapis.com"
        "iam.googleapis.com"
        "monitoring.googleapis.com"
        "logging.googleapis.com"
    )

    for api in "${APIS[@]}"; do
        log_info "Enabling $api..."
        gcloud services enable "$api" --project="$PROJECT_ID" 2>/dev/null || true
    done

    log_success "APIs enabled successfully"
}

create_tfvars() {
    log_info "Creating terraform.tfvars file..."

    TFVARS_FILE="./terraform/terraform.tfvars"

    if [ -f "$TFVARS_FILE" ]; then
        log_warning "terraform.tfvars already exists. Skipping..."
        return
    fi

    cat > "$TFVARS_FILE" <<EOF
# Auto-generated terraform.tfvars for IHEP Healthcare Platform
# Generated on: $(date)

project_id  = "$PROJECT_ID"
region      = "${REGION:-us-central1}"
zone        = "${ZONE:-us-central1-a}"
environment = "${ENVIRONMENT:-prod}"

# VPC Configuration
vpc_name             = "ihep-vpc"
enable_vpc_flow_logs = true
enable_cloud_nat     = true

# Database Configuration
db_tier           = "db-custom-2-8192"
db_replica_tier   = "db-custom-1-4096"
db_backup_enabled = true
db_ha_enabled     = true
db_disk_size_gb   = 100

# Redis Configuration
redis_memory_size_gb = 5
redis_tier           = "STANDARD_HA"

# Security Configuration
enable_cloud_armor     = true
enable_ssl_policy      = true
enable_private_ip_only = true
enable_audit_logs      = true

# Monitoring Configuration
log_retention_days = 90

# Scaling Configuration
min_instances  = 1
max_instances  = 10
cpu_throttling = false

# Domain Configuration
domain_name = "ihep.app"
enable_cdn  = true

# Labels
labels = {
  project     = "ihep"
  managed_by  = "terraform"
  environment = "${ENVIRONMENT:-prod}"
  compliance  = "hipaa"
}
EOF

    log_success "terraform.tfvars created successfully"
}

init_terraform() {
    log_info "Initializing Terraform..."

    cd terraform

    terraform init -upgrade

    log_success "Terraform initialized successfully"
}

plan_terraform() {
    log_info "Creating Terraform execution plan..."

    terraform plan -out=tfplan

    log_success "Terraform plan created successfully"
    log_warning "Review the plan above carefully before applying"
}

apply_terraform() {
    log_info "Applying Terraform configuration..."

    # Ask for confirmation
    read -p "Do you want to apply this Terraform plan? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_warning "Deployment cancelled by user"
        exit 0
    fi

    terraform apply tfplan

    log_success "Terraform applied successfully"
}

output_info() {
    log_info "Retrieving deployment information..."

    echo ""
    echo "============================================================================"
    echo "DEPLOYMENT SUMMARY"
    echo "============================================================================"

    terraform output -json | jq -r 'to_entries[] | "\(.key): \(.value.value)"'

    echo ""
    echo "============================================================================"
    echo "NEXT STEPS"
    echo "============================================================================"
    echo "1. Update API keys in Secret Manager:"
    echo "   - OPENAI_API_KEY"
    echo "   - SENDGRID_API_KEY"
    echo "   - TWILIO_ACCOUNT_SID"
    echo "   - TWILIO_AUTH_TOKEN"
    echo "   - TWILIO_PHONE_NUMBER"
    echo ""
    echo "2. Deploy Cloud Run services:"
    echo "   - Frontend (Next.js app)"
    echo "   - Healthcare API backend"
    echo "   - Auth Service backend"
    echo ""
    echo "3. Configure domain and SSL certificates"
    echo ""
    echo "4. Set up monitoring alerts"
    echo ""
    echo "5. Run security compliance checks"
    echo "============================================================================"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    log_info "Starting IHEP VPC Infrastructure Deployment"
    log_info "============================================"

    # Set default values
    REGION=${REGION:-us-central1}
    ZONE=${ZONE:-us-central1-a}
    ENVIRONMENT=${ENVIRONMENT:-prod}

    # Check prerequisites
    check_prerequisites

    # Set GCP project
    set_project

    # Enable APIs
    enable_apis

    # Create terraform.tfvars
    create_tfvars

    # Initialize Terraform
    init_terraform

    # Create plan
    plan_terraform

    # Apply plan
    apply_terraform

    # Output information
    output_info

    log_success "Deployment completed successfully!"
}

# Run main function
main "$@"
