org_id          = "579995981844"
billing_account = "01DFA7-9727C3-119343"

/*
The folder map is limited to three levels
The environment names are "Production", "Non Production" and "Development"
they are potentially referenced in iam.tf, service_projects.tf, and projects.tf
if you rename, e.g. "Production" to "Prod", you will need to find references like
module.cs-folders-level-1["Team 1/Production"].ids["Production"] and rename to
module.cs-folders-level-1["Team 1/Prod"].ids["Prod"]
*/
folders = {
  "LifeSciences" : {
    "Concept" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Planning" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Resourcing" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Project" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Sanitation" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Maintenance" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
  },
  "Technologies" : {
    "Concept" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Planning" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Resourcing" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Project" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Sanitation" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Maintenance" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
  },
  "Entertainment" : {
    "Concept" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Planning" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Resourcing" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Project" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Sanitation" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Maintenance" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
  },
  "Governmental" : {
    "Concept" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Planning" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Resourcing" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Project" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Sanitation" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Maintenance" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
  },
  "Creative" : {
    "Concept" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Planning" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Resourcing" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Project" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Sanitation" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Maintenance" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
  },
  "B2B" : {
    "Concept" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Planning" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Resourcing" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Project" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Sanitation" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Maintenance" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
  },
  "Commerce" : {
    "Concept" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Planning" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Resourcing" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Project" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Sanitation" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Maintenance" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
  },
  "Financial" : {
    "Concept" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Planning" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Resourcing" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Project" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Sanitation" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Maintenance" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
  },
  "Logistics" : {
    "Concept" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Planning" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Resourcing" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Project" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Sanitation" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Maintenance" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
  },
  "Procurement" : {
    "Concept" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Planning" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Resourcing" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Project" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Sanitation" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Maintenance" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
  },
  "PartnerNet" : {
    "Concept" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Planning" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Resourcing" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Project" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Sanitation" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
    "Maintenance" : {
      "Production" : {},
      "Testing" : {},
      "Development" : {},
    },
  },
}
cmek_autokey_folders = [
  {
    "folder_path" : "LifeSciences/Concept/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Concept/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Concept/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Planning/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Planning/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Planning/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Resourcing/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Resourcing/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Resourcing/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Project/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Project/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Project/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Sanitation/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Sanitation/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Sanitation/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Maintenance/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Maintenance/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "LifeSciences/Maintenance/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Concept/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Concept/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Concept/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Planning/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Planning/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Planning/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Resourcing/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Resourcing/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Resourcing/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Project/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Project/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Project/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Sanitation/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Sanitation/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Sanitation/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Maintenance/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Maintenance/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Technologies/Maintenance/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Concept/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Concept/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Concept/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Planning/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Planning/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Planning/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Resourcing/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Resourcing/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Resourcing/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Project/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Project/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Project/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Sanitation/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Sanitation/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Sanitation/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Maintenance/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Maintenance/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Entertainment/Maintenance/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Concept/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Concept/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Concept/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Planning/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Planning/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Planning/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Resourcing/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Resourcing/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Resourcing/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Project/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Project/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Project/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Sanitation/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Sanitation/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Sanitation/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Maintenance/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Maintenance/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Governmental/Maintenance/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Concept/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Concept/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Concept/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Planning/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Planning/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Planning/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Resourcing/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Resourcing/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Resourcing/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Project/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Project/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Project/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Sanitation/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Sanitation/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Sanitation/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Maintenance/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Maintenance/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Creative/Maintenance/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Concept/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Concept/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Concept/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Planning/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Planning/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Planning/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Resourcing/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Resourcing/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Resourcing/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Project/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Project/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Project/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Sanitation/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Sanitation/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Sanitation/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Maintenance/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Maintenance/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "B2B/Maintenance/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Concept/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Concept/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Concept/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Planning/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Planning/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Planning/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Resourcing/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Resourcing/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Resourcing/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Project/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Project/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Project/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Sanitation/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Sanitation/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Sanitation/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Maintenance/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Maintenance/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Commerce/Maintenance/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Concept/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Concept/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Concept/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Planning/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Planning/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Planning/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Resourcing/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Resourcing/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Resourcing/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Project/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Project/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Project/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Sanitation/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Sanitation/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Sanitation/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Maintenance/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Maintenance/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Financial/Maintenance/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Concept/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Concept/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Concept/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Planning/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Planning/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Planning/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Resourcing/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Resourcing/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Resourcing/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Project/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Project/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Project/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Sanitation/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Sanitation/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Sanitation/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Maintenance/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Maintenance/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Logistics/Maintenance/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Concept/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Concept/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Concept/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Planning/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Planning/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Planning/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Resourcing/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Resourcing/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Resourcing/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Project/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Project/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Project/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Sanitation/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Sanitation/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Sanitation/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Maintenance/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Maintenance/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "Procurement/Maintenance/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Concept/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Concept/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Concept/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Planning/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Planning/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Planning/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Resourcing/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Resourcing/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Resourcing/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Project/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Project/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Project/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Sanitation/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Sanitation/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Sanitation/Development",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Maintenance/Production",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Maintenance/Testing",
    "key_project_name" : "kms-key-project",
  },
  {
    "folder_path" : "PartnerNet/Maintenance/Development",
    "key_project_name" : "kms-key-project",
  },
]
application_enabled_folder_paths = [
  "LifeSciences/Concept/Production",
  "LifeSciences/Concept/Testing",
  "LifeSciences/Concept/Development",
  "LifeSciences/Planning/Production",
  "LifeSciences/Planning/Testing",
  "LifeSciences/Planning/Development",
  "LifeSciences/Resourcing/Production",
  "LifeSciences/Resourcing/Testing",
  "LifeSciences/Resourcing/Development",
  "LifeSciences/Project/Production",
  "LifeSciences/Project/Testing",
  "LifeSciences/Project/Development",
  "LifeSciences/Sanitation/Production",
  "LifeSciences/Sanitation/Testing",
  "LifeSciences/Sanitation/Development",
  "LifeSciences/Maintenance/Production",
  "LifeSciences/Maintenance/Testing",
  "LifeSciences/Maintenance/Development",
  "Technologies/Concept/Production",
  "Technologies/Concept/Testing",
  "Technologies/Concept/Development",
  "Technologies/Planning/Production",
  "Technologies/Planning/Testing",
  "Technologies/Planning/Development",
  "Technologies/Resourcing/Production",
  "Technologies/Resourcing/Testing",
  "Technologies/Resourcing/Development",
  "Technologies/Project/Production",
  "Technologies/Project/Testing",
  "Technologies/Project/Development",
  "Technologies/Sanitation/Production",
  "Technologies/Sanitation/Testing",
  "Technologies/Sanitation/Development",
  "Technologies/Maintenance/Production",
  "Technologies/Maintenance/Testing",
  "Technologies/Maintenance/Development",
  "Entertainment/Concept/Production",
  "Entertainment/Concept/Testing",
  "Entertainment/Concept/Development",
  "Entertainment/Planning/Production",
  "Entertainment/Planning/Testing",
  "Entertainment/Planning/Development",
  "Entertainment/Resourcing/Production",
  "Entertainment/Resourcing/Testing",
  "Entertainment/Resourcing/Development",
  "Entertainment/Project/Production",
  "Entertainment/Project/Testing",
  "Entertainment/Project/Development",
  "Entertainment/Sanitation/Production",
  "Entertainment/Sanitation/Testing",
  "Entertainment/Sanitation/Development",
  "Entertainment/Maintenance/Production",
  "Entertainment/Maintenance/Testing",
  "Entertainment/Maintenance/Development",
  "Governmental/Concept/Production",
  "Governmental/Concept/Testing",
  "Governmental/Concept/Development",
  "Governmental/Planning/Production",
  "Governmental/Planning/Testing",
  "Governmental/Planning/Development",
  "Governmental/Resourcing/Production",
  "Governmental/Resourcing/Testing",
  "Governmental/Resourcing/Development",
  "Governmental/Project/Production",
  "Governmental/Project/Testing",
  "Governmental/Project/Development",
  "Governmental/Sanitation/Production",
  "Governmental/Sanitation/Testing",
  "Governmental/Sanitation/Development",
  "Governmental/Maintenance/Production",
  "Governmental/Maintenance/Testing",
  "Governmental/Maintenance/Development",
  "Creative/Concept/Production",
  "Creative/Concept/Testing",
  "Creative/Concept/Development",
  "Creative/Planning/Production",
  "Creative/Planning/Testing",
  "Creative/Planning/Development",
  "Creative/Resourcing/Production",
  "Creative/Resourcing/Testing",
  "Creative/Resourcing/Development",
  "Creative/Project/Production",
  "Creative/Project/Testing",
  "Creative/Project/Development",
  "Creative/Sanitation/Production",
  "Creative/Sanitation/Testing",
  "Creative/Sanitation/Development",
  "Creative/Maintenance/Production",
  "Creative/Maintenance/Testing",
  "Creative/Maintenance/Development",
  "B2B/Concept/Production",
  "B2B/Concept/Testing",
  "B2B/Concept/Development",
  "B2B/Planning/Production",
  "B2B/Planning/Testing",
  "B2B/Planning/Development",
  "B2B/Resourcing/Production",
  "B2B/Resourcing/Testing",
  "B2B/Resourcing/Development",
  "B2B/Project/Production",
  "B2B/Project/Testing",
  "B2B/Project/Development",
  "B2B/Sanitation/Production",
  "B2B/Sanitation/Testing",
  "B2B/Sanitation/Development",
  "B2B/Maintenance/Production",
  "B2B/Maintenance/Testing",
  "B2B/Maintenance/Development",
  "Commerce/Concept/Production",
  "Commerce/Concept/Testing",
  "Commerce/Concept/Development",
  "Commerce/Planning/Production",
  "Commerce/Planning/Testing",
  "Commerce/Planning/Development",
  "Commerce/Resourcing/Production",
  "Commerce/Resourcing/Testing",
  "Commerce/Resourcing/Development",
  "Commerce/Project/Production",
  "Commerce/Project/Testing",
  "Commerce/Project/Development",
  "Commerce/Sanitation/Production",
  "Commerce/Sanitation/Testing",
  "Commerce/Sanitation/Development",
  "Commerce/Maintenance/Production",
  "Commerce/Maintenance/Testing",
  "Commerce/Maintenance/Development",
  "Financial/Concept/Production",
  "Financial/Concept/Testing",
  "Financial/Concept/Development",
  "Financial/Planning/Production",
  "Financial/Planning/Testing",
  "Financial/Planning/Development",
  "Financial/Resourcing/Production",
  "Financial/Resourcing/Testing",
  "Financial/Resourcing/Development",
  "Financial/Project/Production",
  "Financial/Project/Testing",
  "Financial/Project/Development",
  "Financial/Sanitation/Production",
  "Financial/Sanitation/Testing",
  "Financial/Sanitation/Development",
  "Financial/Maintenance/Production",
  "Financial/Maintenance/Testing",
  "Financial/Maintenance/Development",
  "Logistics/Concept/Production",
  "Logistics/Concept/Testing",
  "Logistics/Concept/Development",
  "Logistics/Planning/Production",
  "Logistics/Planning/Testing",
  "Logistics/Planning/Development",
  "Logistics/Resourcing/Production",
  "Logistics/Resourcing/Testing",
  "Logistics/Resourcing/Development",
  "Logistics/Project/Production",
  "Logistics/Project/Testing",
  "Logistics/Project/Development",
  "Logistics/Sanitation/Production",
  "Logistics/Sanitation/Testing",
  "Logistics/Sanitation/Development",
  "Logistics/Maintenance/Production",
  "Logistics/Maintenance/Testing",
  "Logistics/Maintenance/Development",
  "Procurement/Concept/Production",
  "Procurement/Concept/Testing",
  "Procurement/Concept/Development",
  "Procurement/Planning/Production",
  "Procurement/Planning/Testing",
  "Procurement/Planning/Development",
  "Procurement/Resourcing/Production",
  "Procurement/Resourcing/Testing",
  "Procurement/Resourcing/Development",
  "Procurement/Project/Production",
  "Procurement/Project/Testing",
  "Procurement/Project/Development",
  "Procurement/Sanitation/Production",
  "Procurement/Sanitation/Testing",
  "Procurement/Sanitation/Development",
  "Procurement/Maintenance/Production",
  "Procurement/Maintenance/Testing",
  "Procurement/Maintenance/Development",
  "PartnerNet/Concept/Production",
  "PartnerNet/Concept/Testing",
  "PartnerNet/Concept/Development",
  "PartnerNet/Planning/Production",
  "PartnerNet/Planning/Testing",
  "PartnerNet/Planning/Development",
  "PartnerNet/Resourcing/Production",
  "PartnerNet/Resourcing/Testing",
  "PartnerNet/Resourcing/Development",
  "PartnerNet/Project/Production",
  "PartnerNet/Project/Testing",
  "PartnerNet/Project/Development",
  "PartnerNet/Sanitation/Production",
  "PartnerNet/Sanitation/Testing",
  "PartnerNet/Sanitation/Development",
  "PartnerNet/Maintenance/Production",
  "PartnerNet/Maintenance/Testing",
  "PartnerNet/Maintenance/Development",
]
