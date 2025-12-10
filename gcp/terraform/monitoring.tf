# Monitoring and Alerting Configuration

# Uptime checks for load balancers
resource "google_monitoring_uptime_check_config" "primary_lb_check" {
  display_name = "Primary Load Balancer Health Check"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path         = "/health"
    port         = "80"
    request_method = "GET"
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = google_compute_global_forwarding_rule.web_lb_primary.ip_address
    }
  }

  content_matchers {
    content = "healthy"
  }
}

resource "google_monitoring_uptime_check_config" "secondary_lb_check" {
  display_name = "Secondary Load Balancer Health Check"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path         = "/health"
    port         = "8080"
    request_method = "GET"
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = google_compute_global_forwarding_rule.web_lb_secondary.ip_address
    }
  }

  content_matchers {
    content = "healthy"
  }
}

# Alert policies
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "High Error Rate"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "HTTP 5xx error rate"

    condition_threshold {
      filter          = "resource.type=\"gce_instance\" AND metric.type=\"compute.googleapis.com/instance/up\""
      duration        = "300s"
      comparison      = "COMPARISON_LESS_THAN"
      threshold_value = 0.9

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.email.name
  ]

  alert_strategy {
    auto_close = "86400s"
  }
}

resource "google_monitoring_alert_policy" "database_connection_failure" {
  display_name = "Database Connection Failure"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "Database connection failure"

    condition_threshold {
      filter          = "resource.type=\"cloudsql_database\" AND metric.type=\"cloudsql.googleapis.com/database/state\""
      duration        = "300s"
      comparison      = "COMPARISON_EQUAL"
      threshold_value = 0

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.email.name
  ]
}

resource "google_monitoring_alert_policy" "instance_group_size" {
  display_name = "Instance Group Below Minimum Size"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "Web server group size"

    condition_threshold {
      filter          = "resource.type=\"gce_instance_group\" AND metric.type=\"compute.googleapis.com/instance_group/size\""
      duration        = "300s"
      comparison      = "COMPARISON_LESS_THAN"
      threshold_value = 2

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.email.name
  ]
}

# Notification channel
resource "google_monitoring_notification_channel" "email" {
  display_name = "Health Insight Alert Email"
  type         = "email"

  labels = {
    email_address = "alerts@healthinsightventures.com"
  }
}

# Custom dashboard
resource "google_monitoring_dashboard" "health_insight_dashboard" {
  dashboard_json = jsonencode({
    displayName = "Health Insight Ventures Dashboard"
    mosaicLayout = {
      tiles = [
        {
          width = 6
          height = 4
          widget = {
            title = "Web Server Instances"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"gce_instance\" AND resource.label.instance_name=~\"web-server.*\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_MEAN"
                        crossSeriesReducer = "REDUCE_SUM"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          width = 6
          height = 4
          xPos = 6
          widget = {
            title = "Application Server Response Time"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"gce_instance\" AND resource.label.instance_name=~\"app-server.*\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_MEAN"
                        crossSeriesReducer = "REDUCE_MEAN"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          width = 12
          height = 4
          yPos = 4
          widget = {
            title = "Database Connections"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloudsql_database\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_MEAN"
                        crossSeriesReducer = "REDUCE_SUM"
                      }
                    }
                  }
                }
              ]
            }
          }
        }
      ]
    }
  })
}