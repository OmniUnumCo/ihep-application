# terraform/main.tf
terraform {
  required_version = ">= 1.5"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "ihep-terraform-state"
    prefix = "prod/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "healthcare.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudkms.googleapis.com",
    "secretmanager.googleapis.com",
    "vpcaccess.googleapis.com",
    "compute.googleapis.com",
    "servicenetworking.googleapis.com",
    "identitytoolkit.googleapis.com",
  ])

  service = each.value
  disable_on_destroy = false
}

# VPC Network for private services
resource "google_compute_network" "ihep_vpc" {
  name                    = "ihep-vpc"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.required_apis]
}

resource "google_compute_subnetwork" "ihep_subnet" {
  name          = "ihep-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.ihep_vpc.id

  private_ip_google_access = true
}

# VPC Connector for Cloud Run to access private resources
resource "google_vpc_access_connector" "connector" {
  name          = "ihep-vpc-connector"
  region        = var.region
  network       = google_compute_network.ihep_vpc.name
  ip_cidr_range = "10.8.0.0/28"
  
  depends_on = [google_project_service.required_apis]
}

# Cloud SQL Instance (PostgreSQL)
resource "google_sql_database_instance" "ihep_db" {
  name             = "ihep-postgres-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = "db-custom-2-7680"
    availability_type = "REGIONAL"
    disk_size         = 100
    disk_type         = "PD_SSD"
    disk_autoresize   = true

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.ihep_vpc.id
      require_ssl     = true
    }

    database_flags {
      name  = "cloudsql.enable_pgaudit"
      value = "on"
    }

    database_flags {
      name  = "log_statement"
      value = "all"
    }

    insights_config {
      query_insights_enabled = true
      query_string_length    = 1024
      record_application_tags = true
    }
  }

  deletion_protection = true

  depends_on = [google_service_networking_connection.private_vpc_connection]
}

# Private IP for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "ihep-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.ihep_vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.ihep_vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

resource "google_sql_database" "ihep_database" {
  name     = "ihep"
  instance = google_sql_database_instance.ihep_db.name
}

resource "google_sql_user" "ihep_user" {
  name     = "ihep-app"
  instance = google_sql_database_instance.ihep_db.name
  password = var.db_password
}

# Memorystore (Redis) for caching
resource "google_redis_instance" "ihep_cache" {
  name           = "ihep-cache-${var.environment}"
  tier           = "STANDARD_HA"
  memory_size_gb = 5
  region         = var.region

  authorized_network = google_compute_network.ihep_vpc.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  redis_version     = "REDIS_7_0"
  display_name      = "IHEP Cache"
  reserved_ip_range = "10.1.0.0/29"

  redis_configs = {
    maxmemory-policy = "allkeys-lru"
  }

  depends_on = [google_service_networking_connection.private_vpc_connection]
}

# Healthcare Dataset for PHI storage
resource "google_healthcare_dataset" "ihep_dataset" {
  name     = "ihep-phi-dataset-${var.environment}"
  location = var.region
}

resource "google_healthcare_fhir_store" "ihep_fhir" {
  name    = "ihep-fhir-store"
  dataset = google_healthcare_dataset.ihep_dataset.id
  version = "R4"

  enable_update_create          = true
  disable_referential_integrity = false
  disable_resource_versioning   = false
  enable_history_import         = true

  notification_configs {
    pubsub_topic = google_pubsub_topic.fhir_notifications.id
  }

  stream_configs {
    resource_types = ["Patient", "Observation", "Appointment"]
    bigquery_destination {
      dataset_uri = "bq://${var.project_id}.${google_bigquery_dataset.fhir_analytics.dataset_id}"
      schema_config {
        recursive_structure_depth = 3
      }
    }
  }
}

resource "google_pubsub_topic" "fhir_notifications" {
  name = "fhir-notifications"
}

# BigQuery for PHI analytics (de-identified)
resource "google_bigquery_dataset" "fhir_analytics" {
  dataset_id  = "ihep_fhir_analytics"
  location    = var.region
  description = "De-identified PHI for analytics"

  default_encryption_configuration {
    kms_key_name = google_kms_crypto_key.bigquery_key.id
  }
}

# Cloud KMS for encryption keys
resource "google_kms_key_ring" "ihep_keyring" {
  name     = "ihep-keyring-${var.environment}"
  location = var.region
}

resource "google_kms_crypto_key" "bigquery_key" {
  name            = "bigquery-key"
  key_ring        = google_kms_key_ring.ihep_keyring.id
  rotation_period = "7776000s" # 90 days

  version_template {
    algorithm = "GOOGLE_SYMMETRIC_ENCRYPTION"
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_kms_crypto_key" "application_key" {
  name            = "application-key"
  key_ring        = google_kms_key_ring.ihep_keyring.id
  rotation_period = "7776000s"

  version_template {
    algorithm = "GOOGLE_SYMMETRIC_ENCRYPTION"
  }

  lifecycle {
    prevent_destroy = true
  }
}

# Secret Manager for sensitive configuration
resource "google_secret_manager_secret" "db_connection" {
  secret_id = "db-connection-string"

  replication {
    user_managed {
      replicas {
        location = var.region
      }
      replicas {
        location = var.secondary_region
      }
    }
  }
}

resource "google_secret_manager_secret_version" "db_connection_v1" {
  secret = google_secret_manager_secret.db_connection.id
  secret_data = "postgresql://${google_sql_user.ihep_user.name}:${var.db_password}@${google_sql_database_instance.ihep_db.private_ip_address}:5432/${google_sql_database.ihep_database.name}"
}

# Cloud Run Service for Next.js frontend
resource "google_cloud_run_v2_service" "ihep_frontend" {
  name     = "ihep-frontend"
  location = var.region

  template {
    service_account = google_service_account.frontend_sa.email

    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    scaling {
      min_instance_count = 1
      max_instance_count = 100
    }

    containers {
      image = "gcr.io/${var.project_id}/ihep-frontend:latest"

      ports {
        container_port = 3000
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "1Gi"
        }
        cpu_idle = true
      }

      env {
        name  = "NODE_ENV"
        value = "production"
      }

      env {
        name  = "API_BASE_URL"
        value = "https://api.ihep.app"
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Cloud Run Service for Auth API
resource "google_cloud_run_v2_service" "auth_api" {
  name     = "ihep-auth-api"
  location = var.region

  template {
    service_account = google_service_account.auth_api_sa.email

    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    scaling {
      min_instance_count = 2
      max_instance_count = 50
    }

    containers {
      image = "gcr.io/${var.project_id}/ihep-auth-api:latest"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name = "DB_CONNECTION"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_connection.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "REDIS_HOST"
        value = google_redis_instance.ihep_cache.host
      }

      env {
        name  = "REDIS_PORT"
        value = tostring(google_redis_instance.ihep_cache.port)
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Service Accounts with least privilege
resource "google_service_account" "frontend_sa" {
  account_id   = "ihep-frontend"
  display_name = "IHEP Frontend Service Account"
}

resource "google_service_account" "auth_api_sa" {
  account_id   = "ihep-auth-api"
  display_name = "IHEP Auth API Service Account"
}

resource "google_service_account" "health_api_sa" {
  account_id   = "ihep-health-api"
  display_name = "IHEP Health API Service Account"
}

# IAM bindings for Healthcare API access
resource "google_healthcare_fhir_store_iam_member" "health_api_fhir_admin" {
  fhir_store_id = google_healthcare_fhir_store.ihep_fhir.id
  role          = "roles/healthcare.fhirResourceEditor"
  member        = "serviceAccount:${google_service_account.health_api_sa.email}"
}

# Load Balancer
resource "google_compute_global_address" "frontend_ip" {
  name = "ihep-frontend-ip"
}

resource "google_compute_managed_ssl_certificate" "frontend_cert" {
  name = "ihep-frontend-cert"

  managed {
    domains = [var.domain_name]
  }
}

resource "google_compute_backend_service" "frontend_backend" {
  name                  = "ihep-frontend-backend"
  protocol              = "HTTP"
  port_name             = "http"
  timeout_sec           = 30
  enable_cdn            = true
  compression_mode      = "AUTOMATIC"

  backend {
    group = google_compute_region_network_endpoint_group.frontend_neg.id
  }

  cdn_policy {
    cache_mode  = "CACHE_ALL_STATIC"
    default_ttl = 3600
    max_ttl     = 86400
    client_ttl  = 3600

    cache_key_policy {
      include_host         = true
      include_protocol     = true
      include_query_string = false
    }
  }

  security_policy = google_compute_security_policy.cloud_armor.id

  log_config {
    enable      = true
    sample_rate = 1.0
  }
}

resource "google_compute_region_network_endpoint_group" "frontend_neg" {
  name                  = "ihep-frontend-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region

  cloud_run {
    service = google_cloud_run_v2_service.ihep_frontend.name
  }
}

resource "google_compute_url_map" "frontend_lb" {
  name            = "ihep-frontend-lb"
  default_service = google_compute_backend_service.frontend_backend.id

  host_rule {
    hosts        = [var.domain_name]
    path_matcher = "allpaths"
  }

  path_matcher {
    name            = "allpaths"
    default_service = google_compute_backend_service.frontend_backend.id
  }
}

resource "google_compute_target_https_proxy" "frontend_proxy" {
  name             = "ihep-frontend-proxy"
  url_map          = google_compute_url_map.frontend_lb.id
  ssl_certificates = [google_compute_managed_ssl_certificate.frontend_cert.id]
}

resource "google_compute_global_forwarding_rule" "frontend_https" {
  name                  = "ihep-frontend-https"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL"
  port_range            = "443"
  target                = google_compute_target_https_proxy.frontend_proxy.id
  ip_address            = google_compute_global_address.frontend_ip.id
}

# Cloud Armor security policy
resource "google_compute_security_policy" "cloud_armor" {
  name = "ihep-cloud-armor-policy"

  # Rate limiting rule
  rule {
    action   = "rate_based_ban"
    priority = 1000
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
        count        = 100
        interval_sec = 60
      }
      ban_duration_sec = 600
    }
    description = "Rate limit: 100 requests per minute per IP"
  }

  # Block known malicious IPs (OWASP Top 10)
  rule {
    action   = "deny(403)"
    priority = 2000
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('xss-stable')"
      }
    }
    description = "Block XSS attacks"
  }

  rule {
    action   = "deny(403)"
    priority = 2001
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('sqli-stable')"
      }
    }
    description = "Block SQL injection attacks"
  }

  # Default rule
  rule {
    action   = "allow"
    priority = 2147483647
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default allow rule"
  }
}

# VPC Service Controls for data exfiltration prevention
resource "google_access_context_manager_access_policy" "ihep_policy" {
  parent = "organizations/${var.organization_id}"
  title  = "IHEP Access Policy"
}

resource "google_access_context_manager_service_perimeter" "ihep_perimeter" {
  parent = "accessPolicies/${google_access_context_manager_access_policy.ihep_policy.name}"
  name   = "accessPolicies/${google_access_context_manager_access_policy.ihep_policy.name}/servicePerimeters/ihep_perimeter"
  title  = "IHEP Service Perimeter"

  status {
    restricted_services = [
      "healthcare.googleapis.com",
      "bigquery.googleapis.com",
      "storage.googleapis.com",
    ]

    resources = [
      "projects/${var.project_id}",
    ]

    vpc_accessible_services {
      enable_restriction = true
      allowed_services = [
        "healthcare.googleapis.com",
        "bigquery.googleapis.com",
        "storage.googleapis.com",
      ]
    }
  }
}

# Monitoring and Logging
resource "google_monitoring_notification_channel" "email" {
  display_name = "IHEP Ops Team"
  type         = "email"
  labels = {
    email_address = var.ops_email
  }
}

resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "High Error Rate"
  combiner     = "OR"

  conditions {
    display_name = "Error rate above 5%"
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.label.response_code_class=\"5xx\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

resource "google_logging_project_sink" "phi_access_logs" {
  name        = "phi-access-logs"
  destination = "storage.googleapis.com/${google_storage_bucket.audit_logs.name}"

  filter = "resource.type=\"healthcare_fhir_store\" AND protoPayload.methodName=~\".*fhir.*\""

  unique_writer_identity = true
}

resource "google_storage_bucket" "audit_logs" {
  name          = "${var.project_id}-audit-logs"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 2555 # 7 years for HIPAA compliance
    }
    action {
      type = "Delete"
    }
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.application_key.id
  }
}

# Grant storage writer permission to log sink
resource "google_storage_bucket_iam_member" "sink_writer" {
  bucket = google_storage_bucket.audit_logs.name
  role   = "roles/storage.objectCreator"
  member = google_logging_project_sink.phi_access_logs.writer_identity
}

# Outputs
output "frontend_url" {
  value = "https://${var.domain_name}"
}

output "frontend_ip" {
  value = google_compute_global_address.frontend_ip.address
}

output "db_connection_secret" {
  value     = google_secret_manager_secret.db_connection.secret_id
  sensitive = true
}