# DNS Configuration for ihep.app domain

# DNS managed zone
resource "google_dns_managed_zone" "ihep_app_zone" {
  name        = "ihep-app-zone"
  dns_name    = "ihep.app."
  description = "DNS zone for Health Insight Ventures production domain"

  dnssec_config {
    state = "on"
  }
}

# A record for root domain pointing to primary load balancer
resource "google_dns_record_set" "root_a" {
  name         = google_dns_managed_zone.ihep_app_zone.dns_name
  managed_zone = google_dns_managed_zone.ihep_app_zone.name
  type         = "A"
  ttl          = 300

  rrdatas = [google_compute_global_forwarding_rule.web_lb_primary.ip_address]
}

# A record for www subdomain
resource "google_dns_record_set" "www_a" {
  name         = "www.${google_dns_managed_zone.ihep_app_zone.dns_name}"
  managed_zone = google_dns_managed_zone.ihep_app_zone.name
  type         = "A"
  ttl          = 300

  rrdatas = [google_compute_global_forwarding_rule.web_lb_primary.ip_address]
}

# A record for API subdomain
resource "google_dns_record_set" "api_a" {
  name         = "api.${google_dns_managed_zone.ihep_app_zone.dns_name}"
  managed_zone = google_dns_managed_zone.ihep_app_zone.name
  type         = "A"
  ttl          = 300

  rrdatas = [google_compute_global_forwarding_rule.web_lb_primary.ip_address]
}

# AAAA record for IPv6 support (if needed)
resource "google_dns_record_set" "root_aaaa" {
  name         = google_dns_managed_zone.ihep_app_zone.dns_name
  managed_zone = google_dns_managed_zone.ihep_app_zone.name
  type         = "AAAA"
  ttl          = 300

  rrdatas = [google_compute_global_forwarding_rule.web_lb_primary_https.ip_address]
}

# MX records for email (optional)
resource "google_dns_record_set" "mx" {
  name         = google_dns_managed_zone.ihep_app_zone.dns_name
  managed_zone = google_dns_managed_zone.ihep_app_zone.name
  type         = "MX"
  ttl          = 3600

  rrdatas = [
    "1 aspmx.l.google.com.",
    "5 alt1.aspmx.l.google.com.",
    "5 alt2.aspmx.l.google.com.",
    "10 alt3.aspmx.l.google.com.",
    "10 alt4.aspmx.l.google.com."
  ]
}

# TXT record for domain verification
resource "google_dns_record_set" "txt_verification" {
  name         = google_dns_managed_zone.ihep_app_zone.dns_name
  managed_zone = google_dns_managed_zone.ihep_app_zone.name
  type         = "TXT"
  ttl          = 300

  rrdatas = ["google-site-verification=your-verification-code"]
}

# CNAME for secondary load balancer (backup)
resource "google_dns_record_set" "backup_cname" {
  name         = "backup.${google_dns_managed_zone.ihep_app_zone.dns_name}"
  managed_zone = google_dns_managed_zone.ihep_app_zone.name
  type         = "A"
  ttl          = 300

  rrdatas = [google_compute_global_forwarding_rule.web_lb_secondary.ip_address]
}

# Output DNS nameservers
output "dns_nameservers" {
  value       = google_dns_managed_zone.ihep_app_zone.name_servers
  description = "Name servers for ihep.app domain - configure these with your domain registrar"
}