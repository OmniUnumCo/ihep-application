module "cs-svc-lifesc-concep-prod-svc-c417" {
  source  = "terraform-google-modules/project-factory/google//modules/svpc_service_project"
  version = "~> 18.0"

  name            = "lifescien-concept-prod-svc"
  project_id      = "lifesc-concep-prod-svc-c417"
  org_id          = var.org_id
  billing_account = var.billing_account
  folder_id       = local.folder_map["LifeSciences/Concept/Production"].id

  shared_vpc = module.cs-vpc-prod-shared.project_id
  shared_vpc_subnets = [
    try(module.cs-vpc-prod-shared.subnets["us-central1/subnet-prod-1"].self_link, ""),
  ]

  domain     = data.google_organization.org.domain
  group_name = module.cs-gg-lifescien-concept-prod-svc.name
  group_role = "roles/viewer"
  depends_on = [
    module.cs-org-policy-compute_skipDefaultNetworkCreation,
  ]
}

module "cs-svc-lifesc-concep-nonprod-svc-c417" {
  source  = "terraform-google-modules/project-factory/google//modules/svpc_service_project"
  version = "~> 18.0"

  name            = "lifescien-concept-nonprod-svc"
  project_id      = "lifesc-concep-nonprod-svc-c417"
  org_id          = var.org_id
  billing_account = var.billing_account
  folder_id       = local.folder_map["LifeSciences/Concept/Testing"].id

  shared_vpc = module.cs-vpc-dev-shared.project_id
  shared_vpc_subnets = [
    try(module.cs-vpc-dev-shared.subnets["us-central1/subnet-dev-1"].self_link, ""),
  ]

  domain     = data.google_organization.org.domain
  group_name = module.cs-gg-lifescien-concept-nonprod-svc.name
  group_role = "roles/viewer"
  depends_on = [
    module.cs-org-policy-compute_skipDefaultNetworkCreation,
  ]
}

module "cs-svc-lifesc-planni-prod-svc-c417" {
  source  = "terraform-google-modules/project-factory/google//modules/svpc_service_project"
  version = "~> 18.0"

  name            = "lifescien-planning-prod-svc"
  project_id      = "lifesc-planni-prod-svc-c417"
  org_id          = var.org_id
  billing_account = var.billing_account
  folder_id       = local.folder_map["LifeSciences/Planning/Production"].id

  shared_vpc = module.cs-vpc-prod-shared.project_id
  shared_vpc_subnets = [
    try(module.cs-vpc-prod-shared.subnets["us-east1/subnet-prod-2"].self_link, ""),
  ]

  domain     = data.google_organization.org.domain
  group_name = module.cs-gg-lifescien-planning-prod-svc.name
  group_role = "roles/viewer"
  depends_on = [
    module.cs-org-policy-compute_skipDefaultNetworkCreation,
  ]
}

module "cs-svc-lifesc-planni-nonprod-svc-c417" {
  source  = "terraform-google-modules/project-factory/google//modules/svpc_service_project"
  version = "~> 18.0"

  name            = "lifescien-planning-nonprod-svc"
  project_id      = "lifesc-planni-nonprod-svc-c417"
  org_id          = var.org_id
  billing_account = var.billing_account
  folder_id       = local.folder_map["LifeSciences/Planning/Testing"].id

  shared_vpc = module.cs-vpc-dev-shared.project_id
  shared_vpc_subnets = [
    try(module.cs-vpc-dev-shared.subnets["us-east1/subnet-dev-2"].self_link, ""),
  ]

  domain     = data.google_organization.org.domain
  group_name = module.cs-gg-lifescien-planning-nonprod-svc.name
  group_role = "roles/viewer"
  depends_on = [
    module.cs-org-policy-compute_skipDefaultNetworkCreation,
  ]
}
