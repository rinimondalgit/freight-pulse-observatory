select
    ship_month,
    carrier,
    origin_state,
    destination_state,
    count(*) as total_shipments,
    sum(case when delayed_flag = 1 then 1 else 0 end) as delayed_shipments,
    round(avg(actual_days), 2) as avg_actual_days,
    round(avg(promised_days), 2) as avg_promised_days,
    round(avg(shipping_cost), 2) as avg_shipping_cost,
    round(sum(shipping_cost), 2) as total_shipping_cost
from {{ ref('stg_shipments') }}
group by 1,2,3,4
