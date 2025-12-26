# Main infrastructure configuration for IHEP Healthcare Platform
# This file contains core resources: APIs, BigQuery, Storage, and Secrets

# Get current GCP client config
data "google_client_config" "current" {}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "cloudfunctions.googleapis.com",
    "bigquery.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudbuild.googleapis.com",
    "storage.googleapis.com",
    "firebase.googleapis.com",
    "firestore.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "compute.googleapis.com",
    "servicenetworking.googleapis.com",
    "vpcaccess.googleapis.com",
    "redis.googleapis.com",
    "sqladmin.googleapis.com",
    "healthcare.googleapis.com",
    "pubsub.googleapis.com",
    "run.googleapis.com",
    "dns.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com"
  ])

  service = each.value
  project = var.project_id

  disable_dependent_services = true
}

# BigQuery dataset
resource "google_bigquery_dataset" "health_insight_platform" {
  dataset_id    = "health_insight_platform"
  friendly_name = "Health Insight Ventures Platform Data"
  description   = "Healthcare platform data for HIV patient management and support"
  location      = "US"

  default_table_expiration_ms = null

  access {
    role          = "OWNER"
    user_by_email = data.google_client_config.current.access_token
  }

  depends_on = [google_project_service.required_apis]
}

# Cloud Storage bucket for static assets and frontend hosting
resource "google_storage_bucket" "frontend_bucket" {
  name          = "${var.project_id}-health-insight-frontend"
  location      = "US"
  force_destroy = true

  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  depends_on = [google_project_service.required_apis]
}

# Make bucket publicly readable
resource "google_storage_bucket_iam_member" "frontend_bucket_public" {
  bucket = google_storage_bucket.frontend_bucket.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# Cloud Storage bucket for backend assets
resource "google_storage_bucket" "backend_assets" {
  name          = "${var.project_id}-health-insight-assets"
  location      = "US"
  force_destroy = true

  depends_on = [google_project_service.required_apis]
}

# Secret Manager secrets
resource "google_secret_manager_secret" "database_url" {
  secret_id = "DATABASE_URL"

  replication {
    automatic = true
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "database_url" {
  secret      = google_secret_manager_secret.database_url.id
  secret_data = "bigquery://${var.project_id}/health_insight_platform"
}

# Placeholder secrets (to be updated manually)
resource "google_secret_manager_secret" "openai_api_key" {
  secret_id = "OPENAI_API_KEY"

  replication {
    automatic = true
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret" "sendgrid_api_key" {
  secret_id = "SENDGRID_API_KEY"

  replication {
    automatic = true
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret" "twilio_account_sid" {
  secret_id = "TWILIO_ACCOUNT_SID"

  replication {
    automatic = true
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret" "twilio_auth_token" {
  secret_id = "TWILIO_AUTH_TOKEN"

  replication {
    automatic = true
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret" "twilio_phone_number" {
  secret_id = "TWILIO_PHONE_NUMBER"

  replication {
    automatic = true
  }

  depends_on = [google_project_service.required_apis]
}

# NextAuth secret (required for authentication)
resource "google_secret_manager_secret" "nextauth_secret" {
  secret_id = "NEXTAUTH_SECRET"

  replication {
    automatic = true
  }

  depends_on = [google_project_service.required_apis]
}

# Cloud Run Service for Next.js Application
resource "google_cloud_run_v2_service" "ihep_web" {
  name     = "ihep-web"
  location = var.region

  template {
    containers {
      image = "gcr.io/${var.project_id}/ihep-web:latest"

      ports {
        container_port = 5000
      }

      env {
        name  = "NODE_ENV"
        value = "production"
      }

      env {
        name  = "PORT"
        value = "5000"
      }

      env {
        name = "NEXTAUTH_SECRET"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.nextauth_secret.secret_id
            version = "latest"
          }
        }
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "1Gi"
        }
      }

      startup_probe {
        http_get {
          path = "/api/health"
          port = 5000
        }
        initial_delay_seconds = 0
        period_seconds        = 5
        failure_threshold     = 30
        timeout_seconds       = 3
      }

      liveness_probe {
        http_get {
          path = "/api/health"
          port = 5000
        }
        period_seconds    = 15
        timeout_seconds   = 5
        failure_threshold = 3
      }
    }

    scaling {
      min_instance_count = 1
      max_instance_count = 100
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_project_service.required_apis,
    google_secret_manager_secret.nextauth_secret
  ]
}

# Allow unauthenticated access to Cloud Run service
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.ihep_web.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "bigquery_dataset_id" {
  value = google_bigquery_dataset.health_insight_platform.dataset_id
}

output "frontend_bucket_url" {
  value = "https://storage.googleapis.com/${google_storage_bucket.frontend_bucket.name}/index.html"
}

output "assets_bucket_name" {
  value = google_storage_bucket.backend_assets.name
}

output "project_id" {
  value = var.project_id
}

output "cloud_run_url" {
  value       = google_cloud_run_v2_service.ihep_web.uri
  description = "URL of the deployed Next.js application"
}