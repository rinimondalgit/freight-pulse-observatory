import os
from pathlib import Path
from google.cloud import storage, bigquery

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-gcp-project")
BUCKET_NAME = os.getenv("GCS_BUCKET", f"{PROJECT_ID}-data-lake")
LOCAL_CSV = Path(os.getenv("LOCAL_CSV", "/app/ingestion/shipments.csv"))
GCS_BLOB = os.getenv("GCS_CSV_PATH", "raw/shipments/shipments.csv")
BQ_TABLE = os.getenv("BQ_TABLE", f"{PROJECT_ID}.raw.raw_shipments")

def upload_to_gcs():
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    bucket.blob(GCS_BLOB).upload_from_filename(str(LOCAL_CSV))
    print(f"Uploaded {LOCAL_CSV} to gs://{BUCKET_NAME}/{GCS_BLOB}")

def load_to_bigquery():
    client = bigquery.Client(project=PROJECT_ID)
    job_config = bigquery.LoadJobConfig(source_format=bigquery.SourceFormat.CSV, skip_leading_rows=1, autodetect=True, write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
    uri = f"gs://{BUCKET_NAME}/{GCS_BLOB}"
    client.load_table_from_uri(uri, BQ_TABLE, job_config=job_config).result()
    print(f"Loaded {BQ_TABLE} from {uri}")

if __name__ == "__main__":
    upload_to_gcs()
    load_to_bigquery()
