terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.30"
    }
  }
}
provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = file(var.credentials)
}
resource "google_storage_bucket" "data_lake" {
  name                        = "${var.project_id}-data-lake"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true
}
resource "google_bigquery_dataset" "raw" { dataset_id = "raw" location = var.region }
resource "google_bigquery_dataset" "staging" { dataset_id = "freight_staging" location = var.region }
resource "google_bigquery_dataset" "mart" { dataset_id = "freight_mart" location = var.region }
