# main.tf for GCP resources
resource "google_storage_bucket" "app_data" {
  name     = "${var.project_id}-data"
  location = var.region
}
