# Variables for IHEP Healthcare Platform GCP Infrastructure

# ============================================================================
# PROJECT CONFIGURATION
# ============================================================================

variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "gen-lang-client-0928975904"
}

variable "region" {
  description = "GCP Region for resources"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone for zonal resources"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

# ============================================================================
# NETWORKING CONFIGURATION
# ============================================================================

variable "vpc_name" {
  description = "Name of the VPC network"
  type        = string
  default     = "ihep-vpc"
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC flow logs for all subnets"
  type        = bool
  default     = true
}

variable "enable_cloud_nat" {
  description = "Enable Cloud NAT for outbound internet access"
  type        = bool
  default     = true
}

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

variable "db_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-custom-2-8192" # 2 vCPUs, 8 GB RAM

  validation {
    condition     = can(regex("^db-(custom|n1|f1|g1)-", var.db_tier))
    error_message = "Database tier must be a valid Cloud SQL machine type."
  }
}

variable "db_replica_tier" {
  description = "Cloud SQL read replica instance tier"
  type        = string
  default     = "db-custom-1-4096" # 1 vCPU, 4 GB RAM
}

variable "db_backup_enabled" {
  description = "Enable automated backups for Cloud SQL"
  type        = bool
  default     = true
}

variable "db_ha_enabled" {
  description = "Enable high availability for Cloud SQL"
  type        = bool
  default     = true
}

variable "db_disk_size_gb" {
  description = "Initial disk size for Cloud SQL in GB"
  type        = number
  default     = 100

  validation {
    condition     = var.db_disk_size_gb >= 10 && var.db_disk_size_gb <= 65536
    error_message = "Database disk size must be between 10 and 65536 GB."
  }
}

# ============================================================================
# REDIS CONFIGURATION
# ============================================================================

variable "redis_memory_size_gb" {
  description = "Memory size for Memorystore Redis in GB"
  type        = number
  default     = 5

  validation {
    condition     = var.redis_memory_size_gb >= 1 && var.redis_memory_size_gb <= 300
    error_message = "Redis memory size must be between 1 and 300 GB."
  }
}

variable "redis_tier" {
  description = "Redis tier (BASIC or STANDARD_HA)"
  type        = string
  default     = "STANDARD_HA"

  validation {
    condition     = contains(["BASIC", "STANDARD_HA"], var.redis_tier)
    error_message = "Redis tier must be BASIC or STANDARD_HA."
  }
}

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

variable "enable_cloud_armor" {
  description = "Enable Cloud Armor WAF protection"
  type        = bool
  default     = true
}

variable "enable_ssl_policy" {
  description = "Enable SSL policy for HTTPS load balancer"
  type        = bool
  default     = true
}

variable "allowed_ip_ranges" {
  description = "List of allowed IP ranges for admin access"
  type        = list(string)
  default     = []
}

variable "enable_private_ip_only" {
  description = "Use private IP only for Cloud SQL (no public IP)"
  type        = bool
  default     = true
}

# ============================================================================
# MONITORING & LOGGING
# ============================================================================

variable "enable_audit_logs" {
  description = "Enable audit logging (HIPAA requirement)"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Log retention period in days"
  type        = number
  default     = 90

  validation {
    condition     = var.log_retention_days >= 30 && var.log_retention_days <= 3650
    error_message = "Log retention must be between 30 and 3650 days."
  }
}

# ============================================================================
# SCALING CONFIGURATION
# ============================================================================

variable "min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 1
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10
}

variable "cpu_throttling" {
  description = "Enable CPU throttling for Cloud Run"
  type        = bool
  default     = false
}

# ============================================================================
# DOMAIN CONFIGURATION
# ============================================================================

variable "domain_name" {
  description = "Custom domain name for the application"
  type        = string
  default     = "ihep.app"
}

variable "enable_cdn" {
  description = "Enable Cloud CDN for static content"
  type        = bool
  default     = true
}

# ============================================================================
# LABELS & TAGS
# ============================================================================

variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
  default = {
    project     = "ihep"
    managed_by  = "terraform"
    environment = "prod"
    compliance  = "hipaa"
  }
}
