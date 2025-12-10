# High Availability Architecture for Health Insight Ventures
# Multi-zone deployment with load balancers at every tier

# Network configuration
resource "google_compute_network" "vpc_network" {
  name                    = "health-insight-vpc"
  auto_create_subnetworks = false
}

# Subnets across multiple zones
resource "google_compute_subnetwork" "web_subnet_us_central1_a" {
  name          = "web-subnet-us-central1-a"
  ip_cidr_range = "10.1.1.0/24"
  region        = var.region
  network       = google_compute_network.vpc_network.id
}

resource "google_compute_subnetwork" "web_subnet_us_central1_b" {
  name          = "web-subnet-us-central1-b"
  ip_cidr_range = "10.1.2.0/24"
  region        = var.region
  network       = google_compute_network.vpc_network.id
}

resource "google_compute_subnetwork" "app_subnet_us_central1_a" {
  name          = "app-subnet-us-central1-a"
  ip_cidr_range = "10.2.1.0/24"
  region        = var.region
  network       = google_compute_network.vpc_network.id
}

resource "google_compute_subnetwork" "app_subnet_us_central1_b" {
  name          = "app-subnet-us-central1-b"
  ip_cidr_range = "10.2.2.0/24"
  region        = var.region
  network       = google_compute_network.vpc_network.id
}

resource "google_compute_subnetwork" "db_subnet_us_central1_a" {
  name          = "db-subnet-us-central1-a"
  ip_cidr_range = "10.3.1.0/24"
  region        = var.region
  network       = google_compute_network.vpc_network.id
}

resource "google_compute_subnetwork" "db_subnet_us_central1_b" {
  name          = "db-subnet-us-central1-b"
  ip_cidr_range = "10.3.2.0/24"
  region        = var.region
  network       = google_compute_network.vpc_network.id
}

# Firewall rules
resource "google_compute_firewall" "allow_http_https" {
  name    = "allow-http-https"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["web-server"]
}

resource "google_compute_firewall" "allow_app_tier" {
  name    = "allow-app-tier"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["8080", "3000"]
  }

  source_tags = ["web-server"]
  target_tags = ["app-server"]
}

resource "google_compute_firewall" "allow_db_tier" {
  name    = "allow-db-tier"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["5432", "3306"]
  }

  source_tags = ["app-server"]
  target_tags = ["db-server"]
}

resource "google_compute_firewall" "allow_health_checks" {
  name    = "allow-health-checks"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8080", "3000"]
  }

  source_ranges = [
    "130.211.0.0/22",
    "35.191.0.0/16"
  ]

  target_tags = ["web-server", "app-server"]
}

# Instance templates
resource "google_compute_instance_template" "web_server_template" {
  name         = "web-server-template"
  machine_type = "e2-standard-2"

  disk {
    source_image = "ubuntu-os-cloud/ubuntu-2204-lts"
    auto_delete  = true
    boot         = true
    disk_size_gb = 20
  }

  network_interface {
    network    = google_compute_network.vpc_network.id
    subnetwork = google_compute_subnetwork.web_subnet_us_central1_a.id
    access_config {}
  }

  tags = ["web-server"]

  metadata_startup_script = file("${path.module}/../scripts/web-server-startup.sh")

  service_account {
    email = google_service_account.web_server_sa.email
    scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

resource "google_compute_instance_template" "app_server_template" {
  name         = "app-server-template"
  machine_type = "e2-standard-4"

  disk {
    source_image = "ubuntu-os-cloud/ubuntu-2204-lts"
    auto_delete  = true
    boot         = true
    disk_size_gb = 30
  }

  network_interface {
    network    = google_compute_network.vpc_network.id
    subnetwork = google_compute_subnetwork.app_subnet_us_central1_a.id
  }

  tags = ["app-server"]

  metadata_startup_script = file("${path.module}/../scripts/app-server-startup.sh")

  service_account {
    email = google_service_account.app_server_sa.email
    scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

# Managed Instance Groups
resource "google_compute_region_instance_group_manager" "web_server_group" {
  name = "web-server-group"

  base_instance_name = "web-server"
  region             = var.region

  version {
    instance_template = google_compute_instance_template.web_server_template.id
  }

  target_size = 4

  distribution_policy_zones = [
    "${var.region}-a",
    "${var.region}-b"
  ]

  named_port {
    name = "http"
    port = 80
  }

  named_port {
    name = "https"
    port = 443
  }

  auto_healing_policies {
    health_check      = google_compute_health_check.web_health_check.id
    initial_delay_sec = 300
  }
}

resource "google_compute_region_instance_group_manager" "app_server_group" {
  name = "app-server-group"

  base_instance_name = "app-server"
  region             = var.region

  version {
    instance_template = google_compute_instance_template.app_server_template.id
  }

  target_size = 6

  distribution_policy_zones = [
    "${var.region}-a",
    "${var.region}-b"
  ]

  named_port {
    name = "app"
    port = 3000
  }

  auto_healing_policies {
    health_check      = google_compute_health_check.app_health_check.id
    initial_delay_sec = 300
  }
}

# Health checks
resource "google_compute_health_check" "web_health_check" {
  name = "web-health-check"

  timeout_sec        = 5
  check_interval_sec = 10

  http_health_check {
    port = 80
    path = "/health"
  }
}

resource "google_compute_health_check" "app_health_check" {
  name = "app-health-check"

  timeout_sec        = 5
  check_interval_sec = 10

  http_health_check {
    port = 3000
    path = "/api/health"
  }
}

# Load Balancer 1: Internet to Web Servers (Primary)
resource "google_compute_global_forwarding_rule" "web_lb_primary" {
  name       = "web-lb-primary"
  target     = google_compute_target_http_proxy.web_proxy_primary.id
  port_range = "80"
}

resource "google_compute_global_forwarding_rule" "web_lb_primary_https" {
  name       = "web-lb-primary-https"
  target     = google_compute_target_https_proxy.web_proxy_primary_https.id
  port_range = "443"
}

resource "google_compute_target_http_proxy" "web_proxy_primary" {
  name    = "web-proxy-primary"
  url_map = google_compute_url_map.web_map_primary.id
}

resource "google_compute_target_https_proxy" "web_proxy_primary_https" {
  name             = "web-proxy-primary-https"
  url_map          = google_compute_url_map.web_map_primary.id
  ssl_certificates = [google_compute_managed_ssl_certificate.web_ssl.id]
}

resource "google_compute_url_map" "web_map_primary" {
  name            = "web-map-primary"
  default_service = google_compute_backend_service.web_backend_primary.id

  host_rule {
    hosts        = ["*"]
    path_matcher = "allpaths"
  }

  path_matcher {
    name            = "allpaths"
    default_service = google_compute_backend_service.web_backend_primary.id
  }
}

resource "google_compute_backend_service" "web_backend_primary" {
  name        = "web-backend-primary"
  port_name   = "http"
  protocol    = "HTTP"
  timeout_sec = 10

  backend {
    group = google_compute_region_instance_group_manager.web_server_group.instance_group
  }

  health_checks = [google_compute_health_check.web_health_check.id]
}

# Load Balancer 2: Internet to Web Servers (Secondary)
resource "google_compute_global_forwarding_rule" "web_lb_secondary" {
  name       = "web-lb-secondary"
  target     = google_compute_target_http_proxy.web_proxy_secondary.id
  port_range = "8080"
}

resource "google_compute_target_http_proxy" "web_proxy_secondary" {
  name    = "web-proxy-secondary"
  url_map = google_compute_url_map.web_map_secondary.id
}

resource "google_compute_url_map" "web_map_secondary" {
  name            = "web-map-secondary"
  default_service = google_compute_backend_service.web_backend_secondary.id
}

resource "google_compute_backend_service" "web_backend_secondary" {
  name        = "web-backend-secondary"
  port_name   = "http"
  protocol    = "HTTP"
  timeout_sec = 10

  backend {
    group = google_compute_region_instance_group_manager.web_server_group.instance_group
  }

  health_checks = [google_compute_health_check.web_health_check.id]
}

# Internal Load Balancer 1: Web to App Servers (Primary)
resource "google_compute_region_backend_service" "app_backend_primary" {
  name          = "app-backend-primary"
  port_name     = "app"
  protocol      = "HTTP"
  timeout_sec   = 10
  health_checks = [google_compute_region_health_check.app_health_check_regional.id]
  region        = var.region

  backend {
    group = google_compute_region_instance_group_manager.app_server_group.instance_group
  }
}

resource "google_compute_forwarding_rule" "app_lb_primary" {
  name                  = "app-lb-primary"
  backend_service       = google_compute_region_backend_service.app_backend_primary.id
  region                = var.region
  network               = google_compute_network.vpc_network.id
  subnetwork            = google_compute_subnetwork.web_subnet_us_central1_a.id
  load_balancing_scheme = "INTERNAL"
  ports                 = ["3000"]
}

# Internal Load Balancer 2: Web to App Servers (Secondary)
resource "google_compute_region_backend_service" "app_backend_secondary" {
  name          = "app-backend-secondary"
  port_name     = "app"
  protocol      = "HTTP"
  timeout_sec   = 10
  health_checks = [google_compute_region_health_check.app_health_check_regional.id]
  region        = var.region

  backend {
    group = google_compute_region_instance_group_manager.app_server_group.instance_group
  }
}

resource "google_compute_forwarding_rule" "app_lb_secondary" {
  name                  = "app-lb-secondary"
  backend_service       = google_compute_region_backend_service.app_backend_secondary.id
  region                = var.region
  network               = google_compute_network.vpc_network.id
  subnetwork            = google_compute_subnetwork.web_subnet_us_central1_b.id
  load_balancing_scheme = "INTERNAL"
  ports                 = ["3000"]
}

resource "google_compute_region_health_check" "app_health_check_regional" {
  name   = "app-health-check-regional"
  region = var.region

  timeout_sec        = 5
  check_interval_sec = 10

  http_health_check {
    port = 3000
    path = "/api/health"
  }
}

# Database cluster with high availability
resource "google_sql_database_instance" "postgres_primary" {
  name             = "health-insight-postgres-primary"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-custom-4-16384"

    availability_type = "REGIONAL"

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      location                       = var.region
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 30
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc_network.id
      require_ssl     = true
    }

    database_flags {
      name  = "max_connections"
      value = "200"
    }

    database_flags {
      name  = "shared_preload_libraries"
      value = "pg_stat_statements"
    }
  }

  deletion_protection = true

  depends_on = [google_project_service.required_apis]
}

# Read replica for load distribution
resource "google_sql_database_instance" "postgres_replica" {
  name             = "health-insight-postgres-replica"
  database_version = "POSTGRES_15"
  region           = var.region

  replica_configuration {
    master_instance_name = google_sql_database_instance.postgres_primary.name
  }

  settings {
    tier = "db-custom-4-16384"

    availability_type = "ZONAL"

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc_network.id
      require_ssl     = true
    }
  }

  deletion_protection = true
}

# Service accounts
resource "google_service_account" "web_server_sa" {
  account_id   = "web-server-sa"
  display_name = "Web Server Service Account"
}

resource "google_service_account" "app_server_sa" {
  account_id   = "app-server-sa"
  display_name = "App Server Service Account"
}

# SSL Certificate
resource "google_compute_managed_ssl_certificate" "web_ssl" {
  name = "web-ssl-cert"

  managed {
    domains = ["ihep.app", "www.ihep.app", "api.ihep.app"]
  }
}

# Cloud Armor security policy
resource "google_compute_security_policy" "security_policy" {
  name = "health-insight-security-policy"

  rule {
    action   = "allow"
    priority = "1000"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default allow rule"
  }

  rule {
    action   = "deny(403)"
    priority = "900"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["192.0.2.0/24"]
      }
    }
    description = "Deny traffic from specific IPs"
  }
}

# Outputs for the HA architecture
output "primary_load_balancer_ip" {
  value = google_compute_global_forwarding_rule.web_lb_primary.ip_address
}

output "secondary_load_balancer_ip" {
  value = google_compute_global_forwarding_rule.web_lb_secondary.ip_address
}

output "database_connection_name" {
  value = google_sql_database_instance.postgres_primary.connection_name
}

output "database_replica_connection_name" {
  value = google_sql_database_instance.postgres_replica.connection_name
}