# VPC Network Architecture for IHEP Healthcare Platform
# HIPAA-compliant network design with multiple security layers

# ============================================================================
# VPC NETWORK
# ============================================================================

resource "google_compute_network" "ihep_vpc" {
  name                            = "ihep-vpc"
  auto_create_subnetworks         = false
  routing_mode                    = "REGIONAL"
  delete_default_routes_on_create = false
  description                     = "VPC network for IHEP healthcare platform"

  depends_on = [google_project_service.required_apis]
}

# ============================================================================
# SUBNETS - Multi-tier architecture
# ============================================================================

# Frontend subnet for Cloud Run frontend services
resource "google_compute_subnetwork" "frontend_subnet" {
  name          = "ihep-frontend-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.ihep_vpc.id
  description   = "Subnet for frontend services (Next.js app)"

  # Enable VPC Flow Logs for security monitoring (HIPAA requirement)
  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }

  # Private Google Access for accessing GCP services
  private_ip_google_access = true
}

# Backend subnet for Cloud Run backend services (Healthcare API, Auth Service)
resource "google_compute_subnetwork" "backend_subnet" {
  name          = "ihep-backend-subnet"
  ip_cidr_range = "10.0.2.0/24"
  region        = var.region
  network       = google_compute_network.ihep_vpc.id
  description   = "Subnet for backend services (Healthcare API, Auth Service)"

  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }

  private_ip_google_access = true
}

# Data subnet for databases (Cloud SQL, Memorystore Redis)
resource "google_compute_subnetwork" "data_subnet" {
  name          = "ihep-data-subnet"
  ip_cidr_range = "10.0.3.0/24"
  region        = var.region
  network       = google_compute_network.ihep_vpc.id
  description   = "Subnet for data layer (Cloud SQL PostgreSQL, Memorystore Redis)"

  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 1.0 # Full sampling for data layer
    metadata             = "INCLUDE_ALL_METADATA"
  }

  private_ip_google_access = true
}

# Proxy subnet for Load Balancer (required for internal load balancers)
resource "google_compute_subnetwork" "proxy_subnet" {
  name          = "ihep-proxy-subnet"
  ip_cidr_range = "10.0.4.0/24"
  region        = var.region
  network       = google_compute_network.ihep_vpc.id
  purpose       = "REGIONAL_MANAGED_PROXY"
  role          = "ACTIVE"
  description   = "Proxy subnet for Load Balancer"
}

# GKE subnet (optional - if you decide to use GKE instead of Cloud Run)
resource "google_compute_subnetwork" "gke_subnet" {
  name          = "ihep-gke-subnet"
  ip_cidr_range = "10.0.10.0/24"
  region        = var.region
  network       = google_compute_network.ihep_vpc.id
  description   = "Subnet for GKE cluster (optional)"

  # Secondary IP ranges for GKE pods and services
  secondary_ip_range {
    range_name    = "ihep-gke-pods"
    ip_cidr_range = "10.1.0.0/16"
  }

  secondary_ip_range {
    range_name    = "ihep-gke-services"
    ip_cidr_range = "10.2.0.0/20"
  }

  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }

  private_ip_google_access = true
}

# ============================================================================
# CLOUD ROUTER & CLOUD NAT
# ============================================================================

# Cloud Router for Cloud NAT
resource "google_compute_router" "ihep_router" {
  name    = "ihep-router"
  region  = var.region
  network = google_compute_network.ihep_vpc.id

  bgp {
    asn = 64514
  }
}

# Cloud NAT for outbound internet access from private instances
# Required for calling external APIs (OpenAI, SendGrid, Twilio)
resource "google_compute_router_nat" "ihep_nat" {
  name                               = "ihep-nat"
  router                             = google_compute_router.ihep_router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# ============================================================================
# FIREWALL RULES - Defense in depth
# ============================================================================

# Allow HTTP/HTTPS from internet to Load Balancer
resource "google_compute_firewall" "allow_lb_to_frontend" {
  name    = "ihep-allow-lb-to-frontend"
  network = google_compute_network.ihep_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8080"]
  }

  source_ranges = [
    "130.211.0.0/22",  # GCP Load Balancer health check ranges
    "35.191.0.0/16",   # GCP Load Balancer health check ranges
    "0.0.0.0/0"        # Internet traffic
  ]

  target_tags = ["frontend", "lb-backend"]

  description = "Allow HTTP/HTTPS from Load Balancer and internet to frontend"
}

# Allow frontend to communicate with backend services
resource "google_compute_firewall" "allow_frontend_to_backend" {
  name    = "ihep-allow-frontend-to-backend"
  network = google_compute_network.ihep_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["8080", "8081", "443"]
  }

  source_ranges = ["10.0.1.0/24"] # Frontend subnet
  target_tags   = ["backend"]

  description = "Allow frontend to communicate with backend services"
}

# Allow backend to communicate with data layer
resource "google_compute_firewall" "allow_backend_to_data" {
  name    = "ihep-allow-backend-to-data"
  network = google_compute_network.ihep_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["5432", "6379", "3306"] # PostgreSQL, Redis, MySQL
  }

  source_ranges = ["10.0.2.0/24"] # Backend subnet
  target_tags   = ["database", "cache"]

  description = "Allow backend to communicate with databases and cache"
}

# Allow internal communication between backend services
resource "google_compute_firewall" "allow_backend_internal" {
  name    = "ihep-allow-backend-internal"
  network = google_compute_network.ihep_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["8080", "8081"]
  }

  source_tags = ["backend"]
  target_tags = ["backend"]

  description = "Allow internal communication between backend services"
}

# Allow health checks from GCP
resource "google_compute_firewall" "allow_health_checks" {
  name    = "ihep-allow-health-checks"
  network = google_compute_network.ihep_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8080", "8081"]
  }

  source_ranges = [
    "130.211.0.0/22",
    "35.191.0.0/16",
    "209.85.152.0/22",
    "209.85.204.0/22"
  ]

  target_tags = ["frontend", "backend", "lb-backend"]

  description = "Allow health checks from GCP Load Balancer"
}

# Allow SSH access via Identity-Aware Proxy (IAP)
resource "google_compute_firewall" "allow_iap_ssh" {
  name    = "ihep-allow-iap-ssh"
  network = google_compute_network.ihep_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["35.235.240.0/20"] # IAP IP range

  description = "Allow SSH via Identity-Aware Proxy for secure access"
}

# Deny all other traffic by default (implicit, but explicit for clarity)
resource "google_compute_firewall" "deny_all_ingress" {
  name     = "ihep-deny-all-ingress"
  network  = google_compute_network.ihep_vpc.name
  priority = 65534

  deny {
    protocol = "all"
  }

  source_ranges = ["0.0.0.0/0"]

  description = "Deny all other ingress traffic (default deny)"
}

# ============================================================================
# PRIVATE SERVICE CONNECTION
# ============================================================================

# Reserve IP range for private services (Cloud SQL, Memorystore)
resource "google_compute_global_address" "private_service_connection" {
  name          = "ihep-private-service-connection"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.ihep_vpc.id
}

# Create private service connection for Cloud SQL
resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.ihep_vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_service_connection.name]

  depends_on = [google_project_service.required_apis]
}

# ============================================================================
# SERVERLESS VPC ACCESS CONNECTOR
# ============================================================================

# VPC Access Connector for Cloud Run and Cloud Functions to access VPC resources
resource "google_vpc_access_connector" "serverless_connector" {
  name          = "ihep-serverless-connector"
  region        = var.region
  network       = google_compute_network.ihep_vpc.name
  ip_cidr_range = "10.8.0.0/28" # Small range for connector

  min_throughput = 200
  max_throughput = 1000

  depends_on = [google_project_service.required_apis]
}

# ============================================================================
# CLOUD ARMOR - Web Application Firewall
# ============================================================================

# Cloud Armor security policy for DDoS and application layer protection
resource "google_compute_security_policy" "ihep_security_policy" {
  name        = "ihep-security-policy"
  description = "Security policy for IHEP healthcare platform with OWASP rules"

  # Default rule - allow all traffic (specific rules below will take precedence)
  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default allow rule"
  }

  # Block SQL injection attempts
  rule {
    action   = "deny(403)"
    priority = "1000"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('sqli-stable')"
      }
    }
    description = "Block SQL injection attempts"
  }

  # Block XSS attempts
  rule {
    action   = "deny(403)"
    priority = "1001"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('xss-stable')"
      }
    }
    description = "Block XSS attempts"
  }

  # Rate limiting - prevent abuse
  rule {
    action   = "rate_based_ban"
    priority = "2000"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      enforce_on_key = "IP"
      rate_limit_threshold {
        count        = 1000
        interval_sec = 60
      }
      ban_duration_sec = 600
    }
    description = "Rate limiting - max 1000 requests per minute per IP"
  }

  # Adaptive protection for DDoS
  adaptive_protection_config {
    layer_7_ddos_defense_config {
      enable = true
    }
  }
}

# ============================================================================
# DNS CONFIGURATION
# ============================================================================

# Private DNS zone for internal service discovery
resource "google_dns_managed_zone" "private_zone" {
  name        = "ihep-private-zone"
  dns_name    = "ihep.internal."
  description = "Private DNS zone for internal service discovery"
  visibility  = "private"

  private_visibility_config {
    networks {
      network_url = google_compute_network.ihep_vpc.id
    }
  }
}

# ============================================================================
# OUTPUTS
# ============================================================================

output "vpc_network_name" {
  description = "Name of the VPC network"
  value       = google_compute_network.ihep_vpc.name
}

output "vpc_network_id" {
  description = "ID of the VPC network"
  value       = google_compute_network.ihep_vpc.id
}

output "frontend_subnet_name" {
  description = "Name of the frontend subnet"
  value       = google_compute_subnetwork.frontend_subnet.name
}

output "backend_subnet_name" {
  description = "Name of the backend subnet"
  value       = google_compute_subnetwork.backend_subnet.name
}

output "data_subnet_name" {
  description = "Name of the data subnet"
  value       = google_compute_subnetwork.data_subnet.name
}

output "serverless_connector_name" {
  description = "Name of the VPC Access Connector for serverless services"
  value       = google_vpc_access_connector.serverless_connector.name
}

output "cloud_nat_name" {
  description = "Name of the Cloud NAT gateway"
  value       = google_compute_router_nat.ihep_nat.name
}

output "security_policy_name" {
  description = "Name of the Cloud Armor security policy"
  value       = google_compute_security_policy.ihep_security_policy.name
}

output "private_service_connection_ip_range" {
  description = "IP range reserved for private service connection"
  value       = google_compute_global_address.private_service_connection.address
}
