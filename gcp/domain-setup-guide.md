# Domain Setup Guide for ihep.app

## Step 1: Configure DNS in Google Cloud

The Terraform configuration will automatically create the DNS zone and records:

```bash
# Deploy DNS configuration
cd gcp/terraform
terraform apply -target=google_dns_managed_zone.ihep_app_zone -var="project_id=ihep-app"
terraform apply -target=google_dns_record_set.root_a -var="project_id=ihep-app"
terraform apply -target=google_dns_record_set.www_a -var="project_id=ihep-app"
terraform apply -target=google_dns_record_set.api_a -var="project_id=ihep-app"

# Get the nameservers
terraform output dns_nameservers
```

## Step 2: Configure Domain Registrar

You'll need to configure these nameservers with your domain registrar where you purchased `ihep.app`:

1. **Login to your domain registrar** (e.g., Namecheap, GoDaddy, Google Domains)
2. **Navigate to DNS settings** for `ihep.app`
3. **Change nameservers** to the ones output from Terraform (typically 4 Google nameservers like):
   - `ns-cloud-a1.googledomains.com.`
   - `ns-cloud-a2.googledomains.com.`
   - `ns-cloud-a3.googledomains.com.`
   - `ns-cloud-a4.googledomains.com.`

## Step 3: Verify DNS Propagation

```bash
# Check DNS propagation (may take 24-48 hours)
dig ihep.app
dig www.ihep.app
dig api.ihep.app

# Verify all point to your load balancer IP
nslookup ihep.app
```

## Step 4: SSL Certificate Verification

Google will automatically provision SSL certificates for:
- `ihep.app`
- `www.ihep.app`
- `api.ihep.app`

This process can take 10-60 minutes after DNS propagation is complete.

## Step 5: Test Production URLs

Once DNS is propagated and SSL certificates are provisioned:

```bash
# Test all endpoints
curl -I https://ihep.app
curl -I https://www.ihep.app
curl -I https://api.ihep.app
curl -I https://backup.ihep.app

# Test SSL certificates
curl -vI https://ihep.app 2>&1 | grep -i "subject\|issuer"
```

## Expected Timeline

1. **DNS Zone Creation**: Immediate
2. **Nameserver Update**: 5-10 minutes
3. **DNS Propagation**: 24-48 hours globally
4. **SSL Certificate**: 10-60 minutes after DNS propagation

## Production URLs After Setup

- **Main Website**: https://ihep.app
- **API Endpoint**: https://api.ihep.app
- **Backup/Secondary**: https://backup.ihep.app

## Troubleshooting

### DNS Not Resolving
```bash
# Check nameservers are updated
dig NS ihep.app

# Force DNS refresh
sudo systemctl flush-dns  # Linux
sudo dscacheutil -flushcache  # macOS
```

### SSL Certificate Issues
```bash
# Check certificate status
gcloud compute ssl-certificates describe web-ssl-cert --global

# Check certificate provisioning logs
gcloud logging read "resource.type=gce_ssl_certificate"
```

### Load Balancer Issues
```bash
# Check load balancer health
gcloud compute backend-services get-health web-backend-primary --global
```

All production URLs will be fully functional once DNS propagation is complete!