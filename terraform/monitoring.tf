resource "google_monitoring_monitored_project" "cs-monitored-projects" {
  for_each = toset([
    module.cs-project-vpc-host-prod.project_id,
    module.cs-project-vpc-host-nonprod.project_id,
    module.cs-svc-lifesc-concep-prod-svc-c417.project_id,
    module.cs-svc-lifesc-concep-nonprod-svc-c417.project_id,
    module.cs-svc-lifesc-planni-prod-svc-c417.project_id,
    module.cs-svc-lifesc-planni-nonprod-svc-c417.project_id,
  ])
  metrics_scope = "locations/global/metricsScopes/${module.cs-project-logging-monitoring.project_id}"
  name          = each.value
}

resource "google_monitoring_monitored_project" "cs-monitored-autokey-projects" {
  for_each      = { for i, p in values(module.cs-kms-projects) : "${p.project_name}-${i}" => p.project_id }
  metrics_scope = "locations/global/metricsScopes/${module.cs-project-logging-monitoring.project_id}"
  name          = each.value
}