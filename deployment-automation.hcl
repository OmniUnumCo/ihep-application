# IHEP Production Infrastructure
terraform {
  required_version = ">= 1.5.0"
  
  backend "gcs" {
    bucket = "ihep-terraform-state"
    prefix = "production"
  }
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Cloud SQL PostgreSQL (PHI metadata)
resource "google_sql_database_instance" "ihep_primary" {
  name             = "ihep-primary-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region
  
  settings {
    tier      = "db-custom-4-16384"  # 4 vCPU, 16GB RAM
    disk_size = 100
    disk_type = "PD_SSD"
    
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
    }
    
    ip_configuration {
      ipv4_enabled    = false  # Private IP only
      private_network = google_compute_network.ihep_vpc.id
      require_ssl     = true
    }
    
    database_flags {
      name  = "max_connections"
      value = "200"
    }
  }
  
  deletion_protection = true  # Prevent accidental deletion
}

# Cloud Memorystore Redis (caching)
resource "google_redis_instance" "ihep_cache" {
  name               = "ihep-cache-${var.environment}"
  tier               = "STANDARD_HA"  # High availability
  memory_size_gb     = 5
  region             = var.region
  redis_version      = "REDIS_7_0"
  
  authorized_network = google_compute_network.ihep_vpc.id
  
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 3
        minutes = 0
      }
    }
  }
}

# Cloud Run Services (Microservices)
resource "google_cloud_run_service" "iam_service" {
  name     = "iam-service"
  location = var.region
  
  template {
    spec {
      service_account_name = google_service_account.iam_sa.email
      
      containers {
        image = "gcr.io/${var.project_id}/iam-service:${var.image_tag}"
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
        
        env {
          name  = "FIRESTORE_PROJECT"
          value = var.project_id
        }
        
        env {
          name = "JWT_SECRET"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.jwt_secret.secret_id
              key  = "latest"
            }
          }
        }
      }
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "2"
        "autoscaling.knative.dev/maxScale" = "100"
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Cloud Armor Security Policy
resource "google_compute_security_policy" "ihep_waf" {
  name = "ihep-waf-policy"
  
  # Block common attack patterns
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
  
  rule {
    action   = "deny(403)"
    priority = "1100"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('xss-stable')"
      }
    }
    description = "Block XSS attempts"
  }
  
  # Rate limiting
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
      
      rate_limit_threshold {
        count        = 100
        interval_sec = 60
      }
      
      ban_duration_sec = 600
    }
    description = "Rate limit: 100 req/min per IP"
  }
  
  # Default rule: allow
  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default allow"
  }
}