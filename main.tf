provider "google" {
  project = "ihep-production-2025"
  region  = "us-central1"
}

# --- VPC & Networking (Layer 2) ---
resource "google_compute_network" "vpc_network" {
  name                    = "ihep-vpc-secure"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "serverless_connector" {
  name          = "serverless-subnet"
  ip_cidr_range = "10.0.0.0/28"
  network       = google_compute_network.vpc_network.id
  region        = "us-central1"
}

# --- Cloud SQL for User Data (Postgres) ---
resource "google_sql_database_instance" "master" {
  name             = "ihep-db-primary"
  database_version = "POSTGRES_15"
  region           = "us-central1"
  settings {
    tier = "db-custom-2-7680" # Scalable
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc_network.id
    }
    backup_configuration {
      enabled = true
      binary_log_enabled = true
    }
  }
}

# --- Google Healthcare API (PHI Storage) ---
resource "google_healthcare_dataset" "dataset" {
  name      = "ihep-phi-dataset"
  location  = "us-central1"
}

resource "google_healthcare_fhir_store" "default" {
  name    = "ihep-fhir-store"
  dataset = google_healthcare_dataset.dataset.id
  version = "R4"
  
  # Stream changes to Pub/Sub for Digital Twin processing
  notification_config {
    pubsub_topic = google_pubsub_topic.twin_updates.id
  }
}

# --- Cloud Run (Frontend - Next.js) ---
resource "google_cloud_run_service" "frontend" {
  name     = "ihep-frontend"
  location = "us-central1"

  template {
    spec {
      containers {
        image = "gcr.io/ihep-production-2025/frontend:latest"
        env {
          name  = "NEXT_PUBLIC_API_URL"
          value = "https://api.ihep.app"
        }
      }
    }
  }
}

# --- Cloud Armor (Layer 1 Security) ---
resource "google_compute_security_policy" "policy" {
  name = "ihep-armor-policy"

  rule {
    action   = "deny(403)"
    priority = "1000"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"] # Deny all by default, allow specific regions/IPs in higher priority rules
      }
    }
    description = "Default deny"
  }
  
  # Add OWASP Top 10 rules here...
}