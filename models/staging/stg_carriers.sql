select
    carrier,
    carrier_type,
    cast(fleet_size as int64) as fleet_size,
    service_regions,
    digital_maturity,
    status
from `{{ env_var("DBT_GCP_PROJECT", "your-gcp-project") }}.raw.raw_carriers_partitioned`
where carrier is not null
