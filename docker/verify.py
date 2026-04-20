import os
from google.cloud import bigquery

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-gcp-project")
TABLES = [f"{PROJECT_ID}.raw.raw_shipments_partitioned", f"{PROJECT_ID}.raw.raw_carriers_partitioned"]

if __name__ == "__main__":
    client = bigquery.Client(project=PROJECT_ID)
    for table in TABLES:
        rows = list(client.query(f"SELECT COUNT(*) AS row_count FROM `{table}`").result())
        print(f"{table}: {rows[0].row_count} rows")
