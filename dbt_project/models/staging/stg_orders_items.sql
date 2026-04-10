select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    price,
    freight_value,
    price + freight_value       as total_item_value
from {{ source('olist', 'raw_order_items') }}