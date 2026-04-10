--- Mục đích của phần này là để join orders với items, reviews
--- tạo thành một bảng mới

with orders as (
    select * from {{ ref('stg_orders') }}
),
items as (
    select
        order_id,
        count(order_item_id)                as item_count,
        sum(price)                          as total_price,
        sum(freight_value)                  as total_freight,
        sum(total_item_value)               as order_value,
        count(distinct product_id)          as distinct_products,
        count(distinct seller_id)           as distinct_sellers
    from {{ ref('stg_orders_items') }}
    group by order_id
),
products as (
    select
        oi.order_id,
        -- category phổ biến nhất trong đơn
        mode() within group (order by p.category) as order_category
    from {{ ref('stg_orders_items') }} oi
    left join {{ ref('stg_products') }} p using (product_id)
    group by oi.order_id
),
reviews as (
    select 
        order_id,
        avg(review_score)                   as avg_review_score,
        max(is_bad_review)                  as has_bad_review,
        max(is_perfect_review)              as has_perfect_review,
        max(has_comment)                    as has_comment
    from {{ ref('stg_reviews') }}
    group by order_id
),
payments as (
    select 
        order_id,
        sum(payment_value)                  as total_payment,
        max(payment_installments)           as max_installments,
        max(used_voucher)                   as used_voucher,
        max(used_credit_card)               as used_credit_card,
        max(used_boleto)                    as used_boleto,
        max(used_installment)               as used_installment
    from {{ ref('stg_payments') }}
    group by order_id
)

select
    o.order_id,
    o.customer_id,
    o.purchased_at,
    o.delivered_at,
    o.delivery_delay_days,

    --item metrics (coaleasce return the first non-null value in a list)
    coalesce(i.item_count, 0)               as item_count,
    coalesce(i.order_value, 0)              as order_value,
    coalesce(i.total_freight, 0)            as total_freight,
    coalesce(i.distinct_products, 0)        as distinct_products,
    coalesce(i.distinct_sellers, 0)         as distinct_sellers,

    -- product category
    coalesce(pr.order_category, 'unknown')  as order_category,

    -- review metrics
    coalesce(r.avg_review_score, 3)         as avg_review_score,
    coalesce(r.has_bad_review, 0)           as has_bad_review,
    coalesce(r.has_perfect_review, 0)       as has_perfect_review,
    coalesce(r.has_comment, 0)              as has_comment,

    -- payment metrics
    coalesce(p.total_payment, 0)            as total_payment,
    coalesce(p.max_installments, 1)         as max_installments,
    coalesce(p.used_voucher, 0)             as used_voucher,
    coalesce(p.used_credit_card, 0)         as used_credit_card,
    coalesce(p.used_boleto, 0)              as used_boleto,
    coalesce(p.used_installment, 0)         as used_installment

from orders o
left join items         i   using (order_id)
left join products      pr  using (order_id)
left join reviews       r   using (order_id)
left join payments      p   using (order_id)