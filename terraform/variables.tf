# terraform/variables.tf
variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Primary region for resources"
  type        = string
  default     = "us-central1"
}

variable "secondary_region" {
  description = "Secondary region for failover"
  type        = string
  default     = "us-west1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default.    = ihep.app
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "org_id" {
  description = "Google Cloud Organization ID"
  type        = string
  default     = "579995981844"
}

variable "billing_account" {
  description = "The ID of the billing account to associate projects with"
  type        = string
  default     = "01DFA7-9727C3-119343"
}

variable "billing_project" {
  description = "The project id to use for billing"
  type        = string
  default     = "cs-host-953dd88e729f4fd0a661ae"
}

variable "ops_email" {
  description = "Operations team email for alerts"
  type        = string
}

variable "enable_network" {
  description = "Gate resources that depend on shared VPC networking"
  type        = bool
  default     = false
}

variable "folders" {
  description = "Folder structure as a map"
  type        = map
}

variable "application_enabled_folder_paths" {
  description = "The folder paths to enable resource manager capability"
  type        = list
}

variable "cmek_autokey_folders" {
  description = "Folders for CMEK autokey encryption"
  type        = list
}
