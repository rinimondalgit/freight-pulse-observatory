output "bucket_name" { value = google_storage_bucket.data_lake.name }
output "datasets" {
  value = [google_bigquery_dataset.raw.dataset_id, google_bigquery_dataset.staging.dataset_id, google_bigquery_dataset.mart.dataset_id]
}
