locals {
  web_domains = terraform.workspace == "prod" ? ["ihep.app", "www.ihep.app"] : (
    terraform.workspace == "staging" ? ["staging.ihep.app"] : ["dev.ihep.app"]
  )
}

# Serverless NEG pointing to Cloud Run web service
resource "google_compute_region_network_endpoint_group" "web_neg" {
  name                  = "neg-web-${terraform.workspace}"
  region                = var.region
  network_endpoint_type = "SERVERLESS"

  cloud_run {
    service = google_cloud_run_v2_service.web.name
  }
}

# Backend services: default (no CDN) and static (CDN) both to the same NEG
resource "google_compute_backend_service" "web_backend" {
  name                  = "web-bes-${terraform.workspace}"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  protocol              = "HTTP"
  enable_cdn            = false

  backend {
    group = google_compute_region_network_endpoint_group.web_neg.id
  }
}

resource "google_compute_backend_service" "web_static_backend" {
  name                  = "web-bes-static-${terraform.workspace}"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  protocol              = "HTTP"
  enable_cdn            = true

  backend {
    group = google_compute_region_network_endpoint_group.web_neg.id
  }
}

resource "google_compute_url_map" "web_map" {
  name            = "web-um-${terraform.workspace}"
  default_service = google_compute_backend_service.web_backend.id

  host_rule {
    hosts        = local.web_domains
    path_matcher = "pm"
  }

  path_matcher {
    name            = "pm"
    default_service = google_compute_backend_service.web_backend.id

    path_rule {
      paths   = ["/_next/static/*"]
      service = google_compute_backend_service.web_static_backend.id
    }
  }
}

# Managed SSL certificate (activates after DNS A/AAAA records point to LB IP)
resource "google_compute_managed_ssl_certificate" "web_cert" {
  name = "web-cert-${terraform.workspace}"
  managed {
    domains = local.web_domains
  }
}

resource "google_compute_target_https_proxy" "web_proxy" {
  name             = "web-thp-${terraform.workspace}"
  url_map          = google_compute_url_map.web_map.id
  ssl_certificates = [google_compute_managed_ssl_certificate.web_cert.id]
}

resource "google_compute_global_address" "web_ip" {
  name = "web-ip-${terraform.workspace}"
}

resource "google_compute_global_forwarding_rule" "web_fwd" {
  name                  = "web-fr-443-${terraform.workspace}"
  port_range            = "443"
  ip_protocol           = "TCP"
  target                = google_compute_target_https_proxy.web_proxy.id
  load_balancing_scheme = "EXTERNAL_MANAGED"
  ip_address            = google_compute_global_address.web_ip.address
}

# HTTP -> HTTPS redirect
resource "google_compute_url_map" "web_map_http" {
  name = "web-um-http-${terraform.workspace}"
  default_url_redirect {
    https_redirect = true
    strip_query    = false
  }
}

resource "google_compute_target_http_proxy" "web_proxy_http" {
  name    = "web-thp-http-${terraform.workspace}"
  url_map = google_compute_url_map.web_map_http.id
}

resource "google_compute_global_forwarding_rule" "web_fwd_80" {
  name                  = "web-fr-80-${terraform.workspace}"
  port_range            = "80"
  ip_protocol           = "TCP"
  target                = google_compute_target_http_proxy.web_proxy_http.id
  load_balancing_scheme = "EXTERNAL_MANAGED"
  ip_address            = google_compute_global_address.web_ip.address
}

output "web_lb_ip" {
  value       = google_compute_global_address.web_ip.address
  description = "Global LB IPv4 to use for A records"
}

output "web_cert_self_link" {
  value       = google_compute_managed_ssl_certificate.web_cert.self_link
  description = "Managed SSL cert self link"
}
