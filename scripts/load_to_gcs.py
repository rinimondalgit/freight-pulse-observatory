from google.cloud import storage
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    "keys/freight-key.json"
)

client = storage.Client(
    credentials=credentials,
    project="freight-pulse-observatory"
)

bucket_name = "freight-pulse-bucket-rini"
source_file = "data/raw/shipments_sample.csv"
destination_blob = "raw/shipments_sample.csv"

bucket = client.bucket(bucket_name)
blob = bucket.blob(destination_blob)

blob.upload_from_filename(source_file)

print("File uploaded to GCS successfully.")