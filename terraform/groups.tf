# In order to create google groups, the calling identity should have at least the
# Group Admin role in Google Admin. More info: https://support.google.com/a/answer/2405986

module "cs-gg-lifescien-concept-prod-svc" {
  source  = "terraform-google-modules/group/google"
  version = "~> 0.6"

  id           = "lifescien-concept-prod-svc@jarmacz.com"
  display_name = "lifescien-concept-prod-svc"
  customer_id  = data.google_organization.org.directory_customer_id
  owners = [
    "webmaster@jarmacz.com",
  ]
  types = [
    "default",
    "security",
  ]
}

module "cs-gg-lifescien-concept-nonprod-svc" {
  source  = "terraform-google-modules/group/google"
  version = "~> 0.6"

  id           = "lifescien-concept-nonprod-svc@jarmacz.com"
  display_name = "lifescien-concept-nonprod-svc"
  customer_id  = data.google_organization.org.directory_customer_id
  owners = [
    "webmaster@jarmacz.com",
  ]
  types = [
    "default",
    "security",
  ]
}

module "cs-gg-lifescien-planning-prod-svc" {
  source  = "terraform-google-modules/group/google"
  version = "~> 0.6"

  id           = "lifescien-planning-prod-svc@jarmacz.com"
  display_name = "lifescien-planning-prod-svc"
  customer_id  = data.google_organization.org.directory_customer_id
  owners = [
    "root@jarmacz.com",
  ]
  managers = [
    "jason@jarmacz.com",
  ]
  types = [
    "default",
    "security",
  ]
}

module "cs-gg-lifescien-planning-nonprod-svc" {
  source  = "terraform-google-modules/group/google"
  version = "~> 0.6"

  id           = "lifescien-planning-nonprod-svc@jarmacz.com"
  display_name = "lifescien-planning-nonprod-svc"
  customer_id  = data.google_organization.org.directory_customer_id
  owners = [
    "root@jarmacz.com",
    "jason@jarmacz.com",
  ]
  types = [
    "default",
    "security",
  ]
}
