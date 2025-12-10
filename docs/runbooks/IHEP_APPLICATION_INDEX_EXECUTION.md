<!-- # IHEP Application Index Implementation Runbook -->
ud

| # | Checklist Item | Implementation Notes | Status |
|---|----------------|----------------------|--------|
| 1 | Set environment variables in `.env.local` | Run `./scripts/setup/bootstrap_env.sh` (prompts for OpenAI, SendGrid, Twilio, session secret). Ensures file has `chmod 600`. | Ready |
| 2 | Configure GCP project and enable APIs | Execute `./gcp/setup-project.sh./gcp/setup-project.sh` with optional overrides (`PROJECT_ID`, `REGION`, etc.). Script now enables Cloud KMS, Healthcare API, Cloud SQL Admin, Memorystore, and Service Networking. | Ready |
| 3 | Set up Cloud KMS keyring and crypto key | Handled within `./gcp/setup-project.sh` (`KMS_KEYRING`, `KMS_KEY` variables). | Ready |
| 4 | Create Healthcare API dataset and FHIR store | `./gcp/setup-project.sh` provisions dataset (`HEALTHCARE_DATASET`) and store (`FHIR_STORE`). | Ready |
| 5 | Configure Secret Manager for JWT secret | Export `JWT_SECRET` then rerun `./gcp/setup-project.sh` to add secret version. | Ready |
| 6 | Set up Cloud SQL PostgreSQL instance | `terraform plan -var enable_network=true -var enable_sql=true`; confirm shared VPC host project IDs align before `terraform apply`. | In Progress |
| 7 | Configure Memorystore Redis instance | Populate `terraform/redis.tf` variables (`enable_redis=true`, `redis_authorized_network`) then apply Terraform. | Pending |
| 8 | Update Terraform variables for your project | Review `terraform/cloud-setup.auto.tfvars` and adjust `org_id`, `billing_account`, folder hierarchy. | In Progress |
| 9 | Run security scans: `trivy fs .` | Execute locally or in CI after dependencies installed. | Pending |
|10 | Review and apply Terraform | `terraform plan` / `terraform apply` from `ihep/terraform`. | Pending |
|11 | Configure GitHub Actions secrets | Populate CI secrets (`WIF_PROVIDER`, `GCP_SA_EMAIL`, etc.) in GitHub. Reference `.github/workflows/*.yml`. | Pending |
|12 | Deploy via CI/CD or manual push | Push to appropriate branch or run `./gcp/deploy.sh`. | Pending |
|13 | Run smoke tests on production URLs | Use `./gcp/validate-deployment.sh` and manual curl checks. | Pending |
|14 | Enable monitoring and alerting | Terraform `monitoring.tf` plus manual checks in Cloud Monitoring. | Pending |

## Usage Notes

- Always authenticate with `gcloud auth login` (or impersonation) before running scripts.
- `setup-project.sh` is idempotent; re-running updates existing artifacts.
- For items marked **Pending**, additional Terraform work is required; track progress in the same table.
- Sample `terraform.tfvars` snippet to enable data stores:
	```hcl
	enable_network          = true
	enable_sql              = true
	enable_redis            = true
	redis_authorized_network = "projects/<host-project>/global/networks/<shared-vpc>"
	```
	Replace placeholders with your actual network self link.

## Parking Lot

- Make `ihep/scripts/setup/bootstrap_env.sh` executable (`chmod +x`) and commit for team use.
- Set concrete networking values (`redis_authorized_network`, region overrides) prior to toggling `enable_redis`.
- Provide a `JWT_SECRET` environment variable when running `./gcp/setup-project.sh` to seed the secret. 
