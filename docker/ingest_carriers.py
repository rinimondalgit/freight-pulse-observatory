import os, json
from pathlib import Path
from google.cloud import storage, bigquery

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-gcp-project")
BUCKET_NAME = os.getenv("GCS_BUCKET", f"{PROJECT_ID}-data-lake")
LOCAL_JSON = Path(os.getenv("LOCAL_JSON", "/app/ingestion/carrier_reference_sample.json"))
GCS_BLOB = os.getenv("GCS_JSON_PATH", "raw/carriers/carrier_reference_sample.json")
BQ_TABLE = os.getenv("BQ_TABLE", f"{PROJECT_ID}.raw.raw_carriers")

def upload_to_gcs():
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    bucket.blob(GCS_BLOB).upload_from_filename(str(LOCAL_JSON))
    print(f"Uploaded {LOCAL_JSON} to gs://{BUCKET_NAME}/{GCS_BLOB}")

def load_to_bigquery():
    client = bigquery.Client(project=PROJECT_ID)
    schema = [
        bigquery.SchemaField("carrier", "STRING"),
        bigquery.SchemaField("carrier_type", "STRING"),
        bigquery.SchemaField("fleet_size", "INTEGER"),
        bigquery.SchemaField("service_regions", "STRING"),
        bigquery.SchemaField("digital_maturity", "STRING"),
        bigquery.SchemaField("status", "STRING"),
    ]
    client.delete_table(BQ_TABLE, not_found_ok=True)
    table = bigquery.Table(BQ_TABLE, schema=schema)
    client.create_table(table, exists_ok=True)
    rows = json.loads(LOCAL_JSON.read_text())
    errors = client.insert_rows_json(BQ_TABLE, rows)
    if errors:
        raise RuntimeError(errors)
    print(f"Inserted {len(rows)} rows into {BQ_TABLE}")

if __name__ == "__main__":
    upload_to_gcs()
    load_to_bigquery()
