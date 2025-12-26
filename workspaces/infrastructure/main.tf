terraform {
  required_version = ">= 1.6.0"
  
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
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (staging or production)"
  type        = string
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudkms.googleapis.com",
    "healthcare.googleapis.com",
    "aiplatform.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
  ])
  
  service = each.value
  disable_on_destroy = false
}

# VPC Network
resource "google_compute_network" "vpc_network" {
  name                    = "ihep-${var.environment}-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "ihep-${var.environment}-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc_network.id
  
  private_ip_google_access = true
}

# Cloud KMS for envelope encryption
resource "google_kms_key_ring" "ihep_keyring" {
  name     = "ihep-${var.environment}-keyring"
  location = var.region
}

resource "google_kms_crypto_key" "dek_wrapper_key" {
  name            = "dek-wrapper-key"
  key_ring        = google_kms_key_ring.ihep_keyring.id
  rotation_period = "7776000s"  # 90 days
  
  lifecycle {
    prevent_destroy = true
  }
}

# Healthcare API Dataset
resource "google_healthcare_dataset" "ihep_dataset" {
  name     = "ihep-${var.environment}-dataset"
  location = var.region
}

resource "google_healthcare_fhir_store" "fhir_store" {
  name    = "ihep-fhir-store"
  dataset = google_healthcare_dataset.ihep_dataset.id
  version = "R4"
  
  enable_update_create = true
  disable_referential_integrity = false
  
  notification_config {
    pubsub_topic = google_pubsub_topic.fhir_updates.id
  }
}

resource "google_pubsub_topic" "fhir_updates" {
  name = "ihep-${var.environment}-fhir-updates"
}

# Cloud SQL PostgreSQL
resource "google_sql_database_instance" "postgres" {
  name             = "ihep-${var.environment}-db"
  database_version = "POSTGRES_15"
  region           = var.region
  
  settings {
    tier = var.environment == "production" ? "db-custom-4-16384" : "db-f1-micro"
    
    backup_configuration {
      enabled = true
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
      }
    }
    
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc_network.id
    }
    
    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }
    
    database_flags {
      name  = "log_connections"
      value = "on"
    }
  }
  
  deletion_protection = var.environment == "production"
}

resource "google_sql_database" "ihep_db" {
  name     = "ihep"
  instance = google_sql_database_instance.postgres.name
}

# Memorystore Redis
resource "google_redis_instance" "cache" {
  name           = "ihep-${var.environment}-cache"
  tier           = var.environment == "production" ? "STANDARD_HA" : "BASIC"
  memory_size_gb = var.environment == "production" ? 5 : 1
  region         = var.region
  
  redis_version     = "REDIS_7_0"
  authorized_network = google_compute_network.vpc_network.id
}

# Secret Manager
resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "jwt-secret"
  
  replication {
    automatic = true
  }
}

# Cloud Run Services
resource "google_cloud_run_v2_service" "healthcare_api" {
  name     = "ihep-healthcare-api-${var.environment}"
  location = var.region
  
  template {
    containers {
      image = "gcr.io/${var.project_id}/healthcare-api:latest"
      
      ports {
        container_port = 8080
      }
      
      env {
        name  = "GCP_PROJECT"
        value = var.project_id
      }
      
      env {
        name  = "GCP_LOCATION"
        value = var.region
      }
      
      env {
        name  = "HEALTHCARE_DATASET"
        value = google_healthcare_dataset.ihep_dataset.name
      }
      
      env {
        name  = "FHIR_STORE"
        value = google_healthcare_fhir_store.fhir_store.name
      }
      
      env {
        name  = "KMS_KEY_RING"
        value = google_kms_key_ring.ihep_keyring.name
      }
      
      env {
        name  = "KMS_CRYPTO_KEY"
        value = google_kms_crypto_key.dek_wrapper_key.name
      }
      
      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
        cpu_idle = true
      }
    }
    
    scaling {
      min_instance_count = var.environment == "production" ? 2 : 0
      max_instance_count = var.environment == "production" ? 100 : 10
    }
  }
  
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

resource "google_cloud_run_v2_service" "auth_service" {
  name     = "ihep-auth-service-${var.environment}"
  location = var.region
  
  template {
    containers {
      image = "gcr.io/${var.project_id}/auth-service:latest"
      
      ports {
        container_port = 8081
      }
      
      env {
        name  = "GCP_PROJECT"
        value = var.project_id
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
        name  = "REDIS_HOST"
        value = google_redis_instance.cache.host
      }
      
      env {
        name  = "REDIS_PORT"
        value = tostring(google_redis_instance.cache.port)
      }
      
      resources {
        limits = {
          cpu    = "1"
          memory = "2Gi"
        }
        cpu_idle = true
      }
    }
    
    scaling {
      min_instance_count = var.environment == "production" ? 2 : 0
      max_instance_count = var.environment == "production" ? 50 : 10
    }
  }
  
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

resource "google_cloud_run_v2_service" "frontend" {
  name     = "ihep-frontend-${var.environment}"
  location = var.region
  
  template {
    containers {
      image = "gcr.io/${var.project_id}/frontend:latest"
      
      ports {
        container_port = 3000
      }
      
      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = google_cloud_run_v2_service.healthcare_api.uri
      }
      
      env {
        name  = "NEXT_PUBLIC_GCP_PROJECT"
        value = var.project_id
      }
      
      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
        cpu_idle = true
      }
    }
    
    scaling {
      min_instance_count = var.environment == "production" ? 2 : 0
      max_instance_count = var.environment == "production" ? 100 : 10
    }
  }
  
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# IAM for Cloud Run
resource "google_cloud_run_service_iam_member" "frontend_public_access" {
  location = google_cloud_run_v2_service.frontend.location
  service  = google_cloud_run_v2_service.frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "healthcare_api_url" {
  value = google_cloud_run_v2_service.healthcare_api.uri
}

output "auth_service_url" {
  value = google_cloud_run_v2_service.auth_service.uri
}

output "frontend_url" {
  value = google_cloud_run_v2_service.frontend.uri
}

output "database_connection_name" {
  value = google_sql_database_instance.postgres.connection_name
}
