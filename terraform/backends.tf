terraform {
  backend "gcs" {
    bucket = "cs-tfstate-us-central1-02eee3f5840c4c5b914a339bf318e5d7"
    prefix = "terraform"
  }
}
