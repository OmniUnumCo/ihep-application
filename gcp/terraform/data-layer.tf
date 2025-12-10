# Data Layer Configuration for IHEP Healthcare Platform
# Cloud SQL PostgreSQL, Memorystore Redis, and data services

# ============================================================================
# CLOUD SQL - PostgreSQL Instance
# ============================================================================

# Cloud SQL PostgreSQL instance with high availability
resource "google_sql_database_instance" "ihep_postgres" {
  name             = "ihep-postgres-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = var.db_tier
    availability_type = "REGIONAL" # High availability with failover replica
    disk_type         = "PD_SSD"
    disk_size         = 100 # GB
    disk_autoresize   = true

    # Backup configuration - HIPAA requirement
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
        retention_unit   = "COUNT"
      }
    }

    # IP configuration - Private IP only for security
    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = google_compute_network.ihep_vpc.id
      enable_private_path_for_google_cloud_services = true
      require_ssl                                   = true
    }

    # Maintenance window
    maintenance_window {
      day          = 7 # Sunday
      hour         = 3 # 3 AM
      update_track = "stable"
    }

    # Database flags for security and performance
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
      name  = "cloudsql.enable_pgaudit"
      value = "on"
    }

    # Insights configuration for monitoring
    insights_config {
      query_insights_enabled  = true
      query_plans_per_minute  = 5
      query_string_length     = 1024
      record_application_tags = true
    }
  }

  deletion_protection = true

  depends_on = [
    google_service_networking_connection.private_vpc_connection,
    google_project_service.required_apis
  ]
}

# Create database
resource "google_sql_database" "ihep_db" {
  name     = "ihep"
  instance = google_sql_database_instance.ihep_postgres.name
}

# Create read replica for analytics workloads
resource "google_sql_database_instance" "ihep_postgres_replica" {
  name                 = "ihep-postgres-replica-${var.environment}"
  database_version     = "POSTGRES_15"
  region               = var.region
  master_instance_name = google_sql_database_instance.ihep_postgres.name

  replica_configuration {
    failover_target = false
  }

  settings {
    tier              = var.db_replica_tier
    availability_type = "ZONAL"
    disk_type         = "PD_SSD"
    disk_size         = 100

    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = google_compute_network.ihep_vpc.id
      enable_private_path_for_google_cloud_services = true
      require_ssl                                   = true
    }
  }

  deletion_protection = false

  depends_on = [google_sql_database_instance.ihep_postgres]
}

# Create database user
resource "google_sql_user" "ihep_user" {
  name     = "ihep_app"
  instance = google_sql_database_instance.ihep_postgres.name
  password = random_password.db_password.result
}

# Generate random password for database
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store database password in Secret Manager
resource "google_secret_manager_secret" "db_password" {
  secret_id = "IHEP_DB_PASSWORD"

  replication {
    automatic = true
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

# Store database connection string in Secret Manager
resource "google_secret_manager_secret" "db_connection_string" {
  secret_id = "IHEP_DB_CONNECTION_STRING"

  replication {
    automatic = true
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "db_connection_string" {
  secret = google_secret_manager_secret.db_connection_string.id
  secret_data = format(
    "postgresql://%s:%s@%s/%s",
    google_sql_user.ihep_user.name,
    random_password.db_password.result,
    google_sql_database_instance.ihep_postgres.private_ip_address,
    google_sql_database.ihep_db.name
  )
}

# ============================================================================
# MEMORYSTORE - Redis Instance
# ============================================================================

# Memorystore Redis instance for caching and session management
resource "google_redis_instance" "ihep_redis" {
  name               = "ihep-redis-${var.environment}"
  tier               = "STANDARD_HA" # High availability with automatic failover
  memory_size_gb     = var.redis_memory_size_gb
  region             = var.region
  redis_version      = "REDIS_7_0"
  authorized_network = google_compute_network.ihep_vpc.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  # Redis configuration
  redis_configs = {
    maxmemory-policy = "allkeys-lru"
    notify-keyspace-events = "Ex"
  }

  # Maintenance window
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 3
        minutes = 0
      }
    }
  }

  # Enable auth for security
  auth_enabled = true

  # Enable transit encryption
  transit_encryption_mode = "SERVER_AUTHENTICATION"

  depends_on = [
    google_service_networking_connection.private_vpc_connection,
    google_project_service.required_apis
  ]
}

# Store Redis auth string in Secret Manager
resource "google_secret_manager_secret" "redis_auth" {
  secret_id = "IHEP_REDIS_AUTH"

  replication {
    automatic = true
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "redis_auth" {
  secret      = google_secret_manager_secret.redis_auth.id
  secret_data = google_redis_instance.ihep_redis.auth_string
}

# Store Redis connection string in Secret Manager
resource "google_secret_manager_secret" "redis_connection_string" {
  secret_id = "IHEP_REDIS_CONNECTION_STRING"

  replication {
    automatic = true
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "redis_connection_string" {
  secret = google_secret_manager_secret.redis_connection_string.id
  secret_data = format(
    "redis://:%s@%s:%d",
    google_redis_instance.ihep_redis.auth_string,
    google_redis_instance.ihep_redis.host,
    google_redis_instance.ihep_redis.port
  )
}

# ============================================================================
# HEALTHCARE API DATASET
# ============================================================================

# Healthcare API dataset for FHIR resources
resource "google_healthcare_dataset" "ihep_healthcare_dataset" {
  name     = "ihep-healthcare-dataset"
  location = var.region

  depends_on = [google_project_service.required_apis]
}

# FHIR store for patient data (HIPAA compliant)
resource "google_healthcare_fhir_store" "ihep_fhir_store" {
  name    = "ihep-fhir-store"
  dataset = google_healthcare_dataset.ihep_healthcare_dataset.id
  version = "R4"

  enable_update_create          = true
  disable_referential_integrity = false
  disable_resource_versioning   = false
  enable_history_import         = false

  # Notification configuration for real-time updates
  notification_configs {
    pubsub_topic = google_pubsub_topic.fhir_notifications.id
  }

  # Stream configuration for BigQuery analytics
  stream_configs {
    bigquery_destination {
      dataset_uri = "bq://${var.project_id}.${google_bigquery_dataset.health_insight_platform.dataset_id}"
      schema_config {
        recursive_structure_depth = 3
      }
    }
  }
}

# ============================================================================
# PUB/SUB - Event Streaming
# ============================================================================

# Pub/Sub topic for FHIR notifications
resource "google_pubsub_topic" "fhir_notifications" {
  name = "ihep-fhir-notifications"

  message_retention_duration = "604800s" # 7 days

  depends_on = [google_project_service.required_apis]
}

# Pub/Sub subscription for backend services
resource "google_pubsub_subscription" "fhir_notifications_sub" {
  name  = "ihep-fhir-notifications-sub"
  topic = google_pubsub_topic.fhir_notifications.name

  ack_deadline_seconds = 20

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  expiration_policy {
    ttl = "2678400s" # 31 days
  }
}

# ============================================================================
# OUTPUTS
# ============================================================================

output "postgres_instance_connection_name" {
  description = "Connection name for Cloud SQL PostgreSQL instance"
  value       = google_sql_database_instance.ihep_postgres.connection_name
}

output "postgres_private_ip" {
  description = "Private IP address of Cloud SQL PostgreSQL instance"
  value       = google_sql_database_instance.ihep_postgres.private_ip_address
}

output "postgres_replica_connection_name" {
  description = "Connection name for Cloud SQL PostgreSQL read replica"
  value       = google_sql_database_instance.ihep_postgres_replica.connection_name
}

output "redis_host" {
  description = "Host address of Memorystore Redis instance"
  value       = google_redis_instance.ihep_redis.host
}

output "redis_port" {
  description = "Port of Memorystore Redis instance"
  value       = google_redis_instance.ihep_redis.port
}

output "fhir_store_id" {
  description = "ID of the FHIR store"
  value       = google_healthcare_fhir_store.ihep_fhir_store.id
}

output "fhir_notifications_topic" {
  description = "Pub/Sub topic for FHIR notifications"
  value       = google_pubsub_topic.fhir_notifications.name
}
