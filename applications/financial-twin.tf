# -*- coding: utf-8 -*-
# ==============================================================================
# IHEP Financial Twin Service - Terraform Infrastructure
# ==============================================================================
#
# Production-grade Google Cloud Platform infrastructure for the Financial
# Health Twin microservice with HIPAA compliance and Zero Trust security.
#
# Author: IHEP Technical Architecture Team
# Version: 1.0.0
# ==============================================================================

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "ihep-terraform-state"
    prefix = "financial-twin"
  }
}

# ==============================================================================
# VARIABLES
# ==============================================================================

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region for deployment"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "domain_name" {
  description = "Domain name for the service"
  type        = string
  default     = "financial-twin.ihep.app"
}

variable "min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 2
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 50
}

variable "vpc_connector_name" {
  description = "Name of the VPC Serverless Connector"
  type        = string
  default     = "ihep-vpc-connector"
}

variable "alert_email" {
  description = "Email address for alerting"
  type        = string
}

# ==============================================================================
# LOCAL VALUES
# ==============================================================================

locals {
  service_name = "ihep-financial-twin"
  
  labels = {
    application = "ihep"
    service     = "financial-twin"
    environment = var.environment
    managed_by  = "terraform"
  }
  
  # Database configuration
  db_tier              = var.environment == "production" ? "db-custom-4-16384" : "db-f1-micro"
  db_availability_type = var.environment == "production" ? "REGIONAL" : "ZONAL"
  
  # Redis configuration
  redis_tier   = var.environment == "production" ? "STANDARD_HA" : "BASIC"
  redis_memory = var.environment == "production" ? 4 : 1
}

# ==============================================================================
# DATA SOURCES
# ==============================================================================

data "google_project" "project" {
  project_id = var.project_id
}

data "google_compute_network" "vpc" {
  name    = "ihep-vpc"
  project = var.project_id
}

data "google_compute_subnetwork" "subnet" {
  name    = "ihep-subnet-${var.region}"
  region  = var.region
  project = var.project_id
}

# ==============================================================================
# SERVICE ACCOUNT
# ==============================================================================

resource "google_service_account" "financial_twin" {
  account_id   = "${local.service_name}-sa"
  display_name = "IHEP Financial Twin Service Account"
  description  = "Service account for Financial Twin microservice"
  project      = var.project_id
}

# IAM bindings for service account
resource "google_project_iam_member" "financial_twin_roles" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/redis.editor",
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/cloudtrace.agent",
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.financial_twin.email}"
}

# ==============================================================================
# CLOUD SQL - POSTGRESQL DATABASE
# ==============================================================================

resource "google_sql_database_instance" "financial_twin_db" {
  name             = "${local.service_name}-postgres"
  database_version = "POSTGRES_15"
  region           = var.region
  project          = var.project_id
  
  deletion_protection = var.environment == "production"
  
  settings {
    tier              = local.db_tier
    availability_type = local.db_availability_type
    disk_type         = "PD_SSD"
    disk_size         = var.environment == "production" ? 100 : 20
    disk_autoresize   = true
    
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      start_time                     = "03:00"
      transaction_log_retention_days = 7
      
      backup_retention_settings {
        retained_backups = var.environment == "production" ? 30 : 7
        retention_unit   = "COUNT"
      }
    }
    
    maintenance_window {
      day          = 7  # Sunday
      hour         = 4
      update_track = "stable"
    }
    
    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = data.google_compute_network.vpc.id
      enable_private_path_for_google_cloud_services = true
    }
    
    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }
    
    database_flags {
      name  = "log_connections"
      value = "on"
    }
    
    database_flags {
      name  = "log_disconnections"
      value = "on"
    }
    
    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }
    
    database_flags {
      name  = "log_min_duration_statement"
      value = "1000"  # Log queries > 1 second
    }
    
    insights_config {
      query_insights_enabled  = true
      query_plans_per_minute  = 5
      query_string_length     = 1024
      record_application_tags = true
      record_client_address   = false
    }
    
    user_labels = local.labels
  }
  
  lifecycle {
    prevent_destroy = true
  }
}

resource "google_sql_database" "financial_twin" {
  name     = "financial_twin"
  instance = google_sql_database_instance.financial_twin_db.name
  project  = var.project_id
}

resource "google_sql_user" "financial_twin" {
  name     = "financial_twin_user"
  instance = google_sql_database_instance.financial_twin_db.name
  project  = var.project_id
  
  password = random_password.db_password.result
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

# ==============================================================================
# MEMORYSTORE - REDIS CACHE
# ==============================================================================

resource "google_redis_instance" "financial_twin_cache" {
  name               = "${local.service_name}-redis"
  tier               = local.redis_tier
  memory_size_gb     = local.redis_memory
  region             = var.region
  project            = var.project_id
  
  authorized_network = data.google_compute_network.vpc.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"
  
  redis_version = "REDIS_7_0"
  
  auth_enabled            = true
  transit_encryption_mode = "SERVER_AUTHENTICATION"
  
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 4
        minutes = 0
      }
    }
  }
  
  labels = local.labels
}

# ==============================================================================
# SECRET MANAGER
# ==============================================================================

resource "google_secret_manager_secret" "db_connection" {
  secret_id = "${local.service_name}-db-connection"
  project   = var.project_id
  
  replication {
    auto {}
  }
  
  labels = local.labels
}

resource "google_secret_manager_secret_version" "db_connection" {
  secret = google_secret_manager_secret.db_connection.id
  
  secret_data = "postgresql://${google_sql_user.financial_twin.name}:${random_password.db_password.result}@/financial_twin?host=/cloudsql/${google_sql_database_instance.financial_twin_db.connection_name}"
}

resource "google_secret_manager_secret" "redis_auth" {
  secret_id = "${local.service_name}-redis-auth"
  project   = var.project_id
  
  replication {
    auto {}
  }
  
  labels = local.labels
}

resource "google_secret_manager_secret_version" "redis_auth" {
  secret      = google_secret_manager_secret.redis_auth.id
  secret_data = google_redis_instance.financial_twin_cache.auth_string
}

resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "${local.service_name}-jwt-secret"
  project   = var.project_id
  
  replication {
    auto {}
  }
  
  labels = local.labels
}

resource "google_secret_manager_secret_version" "jwt_secret" {
  secret      = google_secret_manager_secret.jwt_secret.id
  secret_data = random_password.jwt_secret.result
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = false
}

# ==============================================================================
# CLOUD RUN SERVICE
# ==============================================================================

resource "google_cloud_run_v2_service" "financial_twin" {
  name     = local.service_name
  location = var.region
  project  = var.project_id
  
  template {
    service_account = google_service_account.financial_twin.email
    
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }
    
    vpc_access {
      connector = "projects/${var.project_id}/locations/${var.region}/connectors/${var.vpc_connector_name}"
      egress    = "PRIVATE_RANGES_ONLY"
    }
    
    containers {
      image = "gcr.io/${var.project_id}/${local.service_name}:latest"
      
      ports {
        container_port = 8080
      }
      
      resources {
        limits = {
          cpu    = "2"
          memory = "1Gi"
        }
        cpu_idle = true
      }
      
      # Environment variables
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
      
      env {
        name  = "REDIS_HOST"
        value = google_redis_instance.financial_twin_cache.host
      }
      
      env {
        name  = "REDIS_PORT"
        value = tostring(google_redis_instance.financial_twin_cache.port)
      }
      
      # Secrets
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_connection.secret_id
            version = "latest"
          }
        }
      }
      
      env {
        name = "JWT_SECRET"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.jwt_secret.secret_id
            version = "latest"
          }
        }
      }
      
      env {
        name = "REDIS_AUTH"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.redis_auth.secret_id
            version = "latest"
          }
        }
      }
      
      # Liveness and readiness probes
      liveness_probe {
        http_get {
          path = "/health"
        }
        initial_delay_seconds = 10
        period_seconds        = 30
      }
      
      startup_probe {
        http_get {
          path = "/health"
        }
        initial_delay_seconds = 5
        period_seconds        = 10
        failure_threshold     = 5
      }
    }
    
    # Cloud SQL proxy
    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.financial_twin_db.connection_name]
      }
    }
    
    labels = local.labels
  }
  
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
  
  depends_on = [
    google_project_iam_member.financial_twin_roles
  ]
}

# Allow unauthenticated access (handled by API Gateway)
resource "google_cloud_run_service_iam_member" "noauth" {
  location = google_cloud_run_v2_service.financial_twin.location
  project  = var.project_id
  service  = google_cloud_run_v2_service.financial_twin.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ==============================================================================
# PUB/SUB FOR EVENT-DRIVEN ARCHITECTURE
# ==============================================================================

resource "google_pubsub_topic" "financial_events" {
  name    = "${local.service_name}-events"
  project = var.project_id
  
  message_retention_duration = "86400s"  # 24 hours
  
  labels = local.labels
}

resource "google_pubsub_subscription" "financial_events_sub" {
  name    = "${local.service_name}-events-sub"
  topic   = google_pubsub_topic.financial_events.name
  project = var.project_id
  
  ack_deadline_seconds       = 60
  message_retention_duration = "604800s"  # 7 days
  
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
  
  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.financial_events_dlq.id
    max_delivery_attempts = 5
  }
  
  labels = local.labels
}

resource "google_pubsub_topic" "financial_events_dlq" {
  name    = "${local.service_name}-events-dlq"
  project = var.project_id
  
  labels = local.labels
}

# ==============================================================================
# MONITORING AND ALERTING
# ==============================================================================

resource "google_monitoring_notification_channel" "email" {
  display_name = "IHEP Financial Twin Ops Team"
  type         = "email"
  project      = var.project_id
  
  labels = {
    email_address = var.alert_email
  }
}

# High error rate alert
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "${local.service_name} - High Error Rate"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate > 5%"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${local.service_name}\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class=\"5xx\""
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
  
  alert_strategy {
    auto_close = "604800s"  # 7 days
  }
}

# High latency alert
resource "google_monitoring_alert_policy" "high_latency" {
  display_name = "${local.service_name} - High Latency"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "P95 latency > 2s"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${local.service_name}\" AND metric.type=\"run.googleapis.com/request_latencies\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 2000  # 2 seconds in ms
      
      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_PERCENTILE_95"
        cross_series_reducer = "REDUCE_MAX"
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.email.id]
}

# Database connection alert
resource "google_monitoring_alert_policy" "db_connections" {
  display_name = "${local.service_name} - Database Connection Pool"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Connection pool > 80%"
    
    condition_threshold {
      filter          = "resource.type=\"cloudsql_database\" AND resource.labels.database_id=\"${var.project_id}:${google_sql_database_instance.financial_twin_db.name}\" AND metric.type=\"cloudsql.googleapis.com/database/postgresql/num_backends\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 80
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MAX"
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.email.id]
}

# ==============================================================================
# CLOUD LOGGING - AUDIT SINK
# ==============================================================================

resource "google_logging_project_sink" "financial_audit_logs" {
  name        = "${local.service_name}-audit-sink"
  project     = var.project_id
  destination = "storage.googleapis.com/${google_storage_bucket.audit_logs.name}"
  
  filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${local.service_name}\" AND jsonPayload.labels.type=\"financial_access\""
  
  unique_writer_identity = true
}

resource "google_storage_bucket" "audit_logs" {
  name          = "${var.project_id}-${local.service_name}-audit-logs"
  location      = var.region
  project       = var.project_id
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 2555  # 7 years for HIPAA compliance
    }
    action {
      type = "Delete"
    }
  }
  
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
  
  labels = local.labels
}

resource "google_storage_bucket_iam_member" "audit_logs_writer" {
  bucket = google_storage_bucket.audit_logs.name
  role   = "roles/storage.objectCreator"
  member = google_logging_project_sink.financial_audit_logs.writer_identity
}

# ==============================================================================
# OUTPUTS
# ==============================================================================

output "service_url" {
  description = "URL of the deployed Financial Twin service"
  value       = google_cloud_run_v2_service.financial_twin.uri
}

output "database_connection_name" {
  description = "Cloud SQL instance connection name"
  value       = google_sql_database_instance.financial_twin_db.connection_name
}

output "redis_host" {
  description = "Redis instance host"
  value       = google_redis_instance.financial_twin_cache.host
}

output "service_account_email" {
  description = "Service account email"
  value       = google_service_account.financial_twin.email
}

output "audit_logs_bucket" {
  description = "GCS bucket for audit logs"
  value       = google_storage_bucket.audit_logs.name
}
