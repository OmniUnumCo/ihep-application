module "cs-folders-iam-0-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Concept/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-0-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Concept/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-1-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Planning/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-1-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Planning/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-2-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-2-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-3-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Project/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-3-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Project/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-4-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-4-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-5-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-5-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-6-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Concept/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-6-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Concept/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-7-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Planning/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-7-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Planning/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-8-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-8-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-9-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Project/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-9-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Project/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-10-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-10-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-11-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-11-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-12-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Concept/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-12-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Concept/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-13-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Planning/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-13-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Planning/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-14-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-14-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-15-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Project/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-15-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Project/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-16-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-16-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-17-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-17-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-18-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Concept/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-18-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Concept/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-19-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Planning/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-19-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Planning/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-20-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-20-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-21-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Project/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-21-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Project/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-22-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-22-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-23-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-23-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-24-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Concept/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-24-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Concept/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-25-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Planning/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-25-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Planning/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-26-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-26-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-27-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Project/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-27-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Project/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-28-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-28-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-29-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-29-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-30-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Concept/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-30-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Concept/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-31-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Planning/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-31-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Planning/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-32-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-32-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-33-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Project/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-33-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Project/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-34-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-34-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-35-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-35-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-36-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Concept/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-36-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Concept/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-37-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Planning/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-37-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Planning/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-38-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-38-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-39-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Project/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-39-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Project/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-40-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-40-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-41-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-41-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-42-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Concept/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-42-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Concept/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-43-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Planning/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-43-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Planning/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-44-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-44-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-45-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Project/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-45-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Project/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-46-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-46-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-47-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-47-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-48-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Concept/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-48-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Concept/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-49-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Planning/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-49-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Planning/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-50-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-50-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-51-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Project/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-51-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Project/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-52-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-52-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-53-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-53-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-54-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Concept/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-54-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Concept/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-55-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Planning/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-55-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Planning/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-56-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-56-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-57-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Project/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-57-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Project/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-58-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-58-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-59-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-59-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-60-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Concept/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-60-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Concept/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-61-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Planning/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-61-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Planning/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-62-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-62-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Resourcing/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-63-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Project/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-63-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Project/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-64-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-64-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Sanitation/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-65-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-65-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Maintenance/Testing"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-66-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Concept/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-66-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Concept/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-67-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Planning/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-67-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Planning/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-68-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-68-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-69-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Project/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-69-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Project/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-70-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-70-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-71-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-71-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["LifeSciences/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-72-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Concept/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-72-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Concept/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-73-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Planning/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-73-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Planning/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-74-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-74-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-75-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Project/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-75-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Project/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-76-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-76-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-77-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-77-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Technologies/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-78-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Concept/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-78-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Concept/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-79-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Planning/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-79-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Planning/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-80-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-80-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-81-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Project/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-81-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Project/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-82-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-82-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-83-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-83-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Entertainment/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-84-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Concept/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-84-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Concept/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-85-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Planning/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-85-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Planning/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-86-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-86-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-87-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Project/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-87-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Project/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-88-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-88-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-89-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-89-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Governmental/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-90-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Concept/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-90-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Concept/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-91-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Planning/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-91-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Planning/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-92-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-92-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-93-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Project/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-93-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Project/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-94-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-94-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-95-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-95-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Creative/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-96-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Concept/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-96-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Concept/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-97-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Planning/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-97-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Planning/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-98-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-98-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-99-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Project/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-99-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Project/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-100-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-100-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-101-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-101-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["B2B/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-102-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Concept/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-102-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Concept/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-103-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Planning/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-103-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Planning/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-104-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-104-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-105-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Project/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-105-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Project/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-106-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-106-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-107-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-107-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Commerce/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-108-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Concept/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-108-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Concept/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-109-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Planning/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-109-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Planning/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-110-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-110-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-111-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Project/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-111-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Project/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-112-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-112-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-113-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-113-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Financial/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-114-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Concept/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-114-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Concept/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-115-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Planning/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-115-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Planning/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-116-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-116-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-117-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Project/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-117-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Project/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-118-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-118-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-119-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-119-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Logistics/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-120-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Concept/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-120-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Concept/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-121-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Planning/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-121-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Planning/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-122-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-122-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-123-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Project/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-123-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Project/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-124-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-124-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-125-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-125-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["Procurement/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-126-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Concept/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-126-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Concept/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-127-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Planning/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-127-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Planning/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-128-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-128-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Resourcing/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-129-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Project/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-129-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Project/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-130-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-130-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Sanitation/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-131-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-folders-iam-131-containeradmin" {
  source  = "terraform-google-modules/iam/google//modules/folders_iam"
  version = "~> 8.0"

  folders = [
    local.folder_map["PartnerNet/Maintenance/Development"].id,
  ]
  bindings = {
    "roles/container.admin" = [
      "group:gcp-developers@jarmacz.com",
    ]
  }
}

module "cs-projects-iam-132-loggingviewer" {
  source  = "terraform-google-modules/iam/google//modules/projects_iam"
  version = "~> 8.0"

  projects = [
    module.cs-project-logging-monitoring.project_id,
  ]
  bindings = {
    "roles/logging.viewer" = [
      "group:gcp-logging-monitoring-viewers@jarmacz.com",
    ]
  }
}

module "cs-projects-iam-132-loggingprivateLogViewer" {
  source  = "terraform-google-modules/iam/google//modules/projects_iam"
  version = "~> 8.0"

  projects = [
    module.cs-project-logging-monitoring.project_id,
  ]
  bindings = {
    "roles/logging.privateLogViewer" = [
      "group:gcp-logging-monitoring-viewers@jarmacz.com",
    ]
  }
}

module "cs-projects-iam-132-bigquerydataViewer" {
  source  = "terraform-google-modules/iam/google//modules/projects_iam"
  version = "~> 8.0"

  projects = [
    module.cs-project-logging-monitoring.project_id,
  ]
  bindings = {
    "roles/bigquery.dataViewer" = [
      "group:gcp-logging-monitoring-viewers@jarmacz.com",
    ]
  }
}

module "cs-projects-iam-132-pubsubviewer" {
  source  = "terraform-google-modules/iam/google//modules/projects_iam"
  version = "~> 8.0"

  projects = [
    module.cs-project-logging-monitoring.project_id,
  ]
  bindings = {
    "roles/pubsub.viewer" = [
      "group:gcp-logging-monitoring-viewers@jarmacz.com",
    ]
  }
}

module "cs-projects-iam-132-monitoringviewer" {
  source  = "terraform-google-modules/iam/google//modules/projects_iam"
  version = "~> 8.0"

  projects = [
    module.cs-project-logging-monitoring.project_id,
  ]
  bindings = {
    "roles/monitoring.viewer" = [
      "group:gcp-logging-monitoring-viewers@jarmacz.com",
    ]
  }
}

module "cs-projects-iam-133-bigquerydataViewer" {
  source  = "terraform-google-modules/iam/google//modules/projects_iam"
  version = "~> 8.0"

  projects = [
    module.cs-project-logging-monitoring.project_id,
  ]
  bindings = {
    "roles/bigquery.dataViewer" = [
      "group:gcp-security-admins@jarmacz.com",
    ]
  }
}

module "cs-projects-iam-133-pubsubviewer" {
  source  = "terraform-google-modules/iam/google//modules/projects_iam"
  version = "~> 8.0"

  projects = [
    module.cs-project-logging-monitoring.project_id,
  ]
  bindings = {
    "roles/pubsub.viewer" = [
      "group:gcp-security-admins@jarmacz.com",
    ]
  }
}

module "cs-service-projects-iam-134-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/projects_iam"
  version = "~> 8.0"

  projects = [
    module.cs-svc-lifesc-concep-prod-svc-c417.project_id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:${module.cs-gg-lifescien-concept-prod-svc.id}",
    ]
  }
}

module "cs-service-projects-iam-135-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/projects_iam"
  version = "~> 8.0"

  projects = [
    module.cs-svc-lifesc-concep-nonprod-svc-c417.project_id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:${module.cs-gg-lifescien-concept-nonprod-svc.id}",
    ]
  }
}

module "cs-service-projects-iam-136-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/projects_iam"
  version = "~> 8.0"

  projects = [
    module.cs-svc-lifesc-planni-prod-svc-c417.project_id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:${module.cs-gg-lifescien-planning-prod-svc.id}",
    ]
  }
}

module "cs-service-projects-iam-137-computeinstanceAdminv1" {
  source  = "terraform-google-modules/iam/google//modules/projects_iam"
  version = "~> 8.0"

  projects = [
    module.cs-svc-lifesc-planni-nonprod-svc-c417.project_id,
  ]
  bindings = {
    "roles/compute.instanceAdmin.v1" = [
      "group:${module.cs-gg-lifescien-planning-nonprod-svc.id}",
    ]
  }
}
