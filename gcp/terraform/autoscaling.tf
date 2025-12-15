# Auto-scaling Configuration

# Web server autoscaler
resource "google_compute_region_autoscaler" "web_server_autoscaler" {
  name   = "web-server-autoscaler"
  region = var.region
  target = google_compute_region_instance_group_manager.web_server_group.id

  autoscaling_policy {
    max_replicas    = 10
    min_replicas    = 4
    cooldown_period = 300

    cpu_utilization {
      target = 0.7
    }

    load_balancing_utilization {
      target = 0.8
    }

    metric {
      name   = "compute.googleapis.com/instance/network/received_bytes_count"
      type   = "GAUGE"
      target = 1000000
    }

    scale_in_control {
      max_scaled_in_replicas {
        fixed = 2
      }
      time_window_sec = 300
    }
  }
}

# Application server autoscaler
resource "google_compute_region_autoscaler" "app_server_autoscaler" {
  name   = "app-server-autoscaler"
  region = var.region
  target = google_compute_region_instance_group_manager.app_server_group.id

  autoscaling_policy {
    max_replicas    = 15
    min_replicas    = 6
    cooldown_period = 300

    cpu_utilization {
      target = 0.6
    }

    load_balancing_utilization {
      target = 0.7
    }

    metric {
      name   = "compute.googleapis.com/instance/memory/utilization"
      type   = "GAUGE"
      target = 0.8
    }

    scale_in_control {
      max_scaled_in_replicas {
        fixed = 3
      }
      time_window_sec = 600
    }
  }
}

# Custom scaling metrics
resource "google_monitoring_metric_descriptor" "app_response_time" {
  display_name = "Application Response Time"
  description  = "Average response time for API endpoints"
  metric_kind  = "GAUGE"
  value_type   = "DOUBLE"
  type         = "custom.googleapis.com/health_insight/response_time"

  labels {
    key         = "endpoint"
    value_type  = "STRING"
    description = "API endpoint path"
  }
}

resource "google_monitoring_metric_descriptor" "active_users" {
  display_name = "Active Users"
  description  = "Number of active users in the system"
  metric_kind  = "GAUGE"
  value_type   = "INT64"
  type         = "custom.googleapis.com/health_insight/active_users"
}

# Preemptible instance group for cost optimization
resource "google_compute_region_instance_group_manager" "app_server_preemptible" {
  name = "app-server-preemptible"

  base_instance_name = "app-server-preemptible"
  region             = var.region

  version {
    instance_template = google_compute_instance_template.app_server_preemptible_template.id
  }

  target_size = 2

  distribution_policy_zones = [
    "${var.region}-a",
    "${var.region}-b"
  ]

  named_port {
    name = "app"
    port = 3000
  }

  auto_healing_policies {
    health_check      = google_compute_health_check.app_health_check.id
    initial_delay_sec = 300
  }
}

resource "google_compute_instance_template" "app_server_preemptible_template" {
  name         = "app-server-preemptible-template"
  machine_type = "e2-standard-2"

  disk {
    source_image = "ubuntu-os-cloud/ubuntu-2204-lts"
    auto_delete  = true
    boot         = true
    disk_size_gb = 20
  }

  network_interface {
    network    = google_compute_network.vpc_network.id
    subnetwork = google_compute_subnetwork.app_subnet_us_central1_a.id
  }

  tags = ["app-server", "preemptible"]

  metadata_startup_script = file("${path.module}/../scripts/app-server-startup.sh")

  scheduling {
    preemptible = true
  }

  service_account {
    email = google_service_account.app_server_sa.email
    scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

# Autoscaler for preemptible instances
resource "google_compute_region_autoscaler" "app_server_preemptible_autoscaler" {
  name   = "app-server-preemptible-autoscaler"
  region = var.region
  target = google_compute_region_instance_group_manager.app_server_preemptible.id

  autoscaling_policy {
    max_replicas    = 8
    min_replicas    = 2
    cooldown_period = 180

    cpu_utilization {
      target = 0.5
    }

    scale_in_control {
      max_scaled_in_replicas {
        percent = 50
      }
      time_window_sec = 180
    }
  }
}