select
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp::timestamp                          as purchased_at,
    order_approved_at::timestamp                                as approved_at,
    order_delivered_carrier_date::timestamp                     as shipped_at,
    order_delivered_customer_date::timestamp                    as delivered_at,
    order_estimated_delivery_date::timestamp                    as estimated_delivery_at,

    -- số ngày giao thực tế so với dự kiến (âm = giao sớm, dương = giao trễ)
    extract(day from (
        order_delivered_customer_date::timestamp
        - order_estimated_delivery_date::timestamp
    ))                                                          as delivery_delay_days

from {{ source('olist', 'raw_orders') }}
where order_status not in ('unavailable', 'canceled')