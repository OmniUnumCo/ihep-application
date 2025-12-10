variable "enable_firestore" {
  description = "Create Firestore in Native mode (project-wide, run once in prod)"
  type        = bool
  default     = false
}

resource "google_firestore_database" "default" {
  count       = var.enable_firestore && terraform.workspace == "prod" ? 1 : 0
  project     = var.project_id
  name        = "(default)"
  location_id = "nam5" # North America multi-region
  type        = "FIRESTORE_NATIVE"
}

output "firestore_database_id" {
  value       = var.enable_firestore && terraform.workspace == "prod" ? google_firestore_database.default[0].name : null
  description = "Firestore database resource name"
}

