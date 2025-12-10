variable "web_cpu" {
  type    = string
  default = "1"
}
variable "web_memory" {
  type    = string
  default = "512Mi"
}
variable "web_min_instances" {
  type    = number
  default = 0
}
variable "web_max_instances" {
  type    = number
  default = 10
}

resource "google_cloud_run_v2_service" "web" {
  name     = "web-${terraform.workspace}"
  location = var.region

  template {
    containers {
      image = "us-docker.pkg.dev/${var.project_id}/ihep/web:latest"
      resources {
        cpu_idle = true
        limits = {
          cpu    = var.web_cpu
          memory = var.web_memory
        }
      }
      env {
        name  = "NODE_ENV"
        value = terraform.workspace == "prod" ? "production" : terraform.workspace
      }
    }
    scaling {
      min_instance_count = var.web_min_instances
      max_instance_count = var.web_max_instances
    }
  }

  ingress = "INGRESS_TRAFFIC_ALL"

  lifecycle {
    # Allow CI deployments to change the image without Terraform trying to revert it
    ignore_changes = [
      template[0].containers[0].image
    ]
  }
}

# Allow public access (LB or direct) – enforce app-level auth for PHI
resource "google_cloud_run_v2_service_iam_member" "web_invoker" {
  project  = google_cloud_run_v2_service.web.project
  location = google_cloud_run_v2_service.web.location
  name     = google_cloud_run_v2_service.web.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "web_service_name" {
  value       = google_cloud_run_v2_service.web.name
  description = "Cloud Run web service name for this workspace"
}

output "web_service_uri" {
  value       = google_cloud_run_v2_service.web.uri
  description = "Cloud Run web service HTTPS URL (temporary until LB)"
}
