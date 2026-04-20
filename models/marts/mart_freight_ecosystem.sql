with shipment_metrics as (
    select
        carrier,
        count(*) as total_shipments,
        sum(case when delayed_flag = 1 then 1 else 0 end) as delayed_shipments,
        round(100 * safe_divide(sum(case when delayed_flag = 1 then 1 else 0 end), count(*)), 2) as delay_rate_pct,
        round(avg(actual_days), 2) as avg_transit_days,
        round(avg(shipping_cost), 2) as avg_shipping_cost
    from {{ ref('stg_shipments') }}
    group by 1
)
select
    s.carrier,
    c.carrier_type,
    c.fleet_size,
    c.service_regions,
    c.digital_maturity,
    c.status,
    s.total_shipments,
    s.delayed_shipments,
    s.delay_rate_pct,
    s.avg_transit_days,
    s.avg_shipping_cost,
    round(safe_divide(s.total_shipments, nullif(c.fleet_size, 0)) * 1000, 4) as shipments_per_1000_fleet
from shipment_metrics s
left join {{ ref('stg_carriers') }} c on s.carrier = c.carrier
