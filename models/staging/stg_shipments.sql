select
    shipment_id,
    cast(ship_date as date) as ship_date,
    cast(delivery_date as date) as delivery_date,
    carrier,
    mode,
    origin_city,
    origin_state,
    destination_city,
    destination_state,
    cast(distance_miles as int64) as distance_miles,
    cast(promised_days as int64) as promised_days,
    cast(actual_days as int64) as actual_days,
    cast(delayed_flag as int64) as delayed_flag,
    cast(shipping_cost as numeric) as shipping_cost,
    customer_segment,
    date_trunc(cast(ship_date as date), month) as ship_month
from `{{ env_var("DBT_GCP_PROJECT", "your-gcp-project") }}.raw.raw_shipments_partitioned`
where ship_date is not null and delivery_date is not null and distance_miles > 0
