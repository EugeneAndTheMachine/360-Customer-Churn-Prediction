-- with orders as (
--     select * from {{ ref('int_order_metrics')}}
-- ),
-- customers as (
--     select * from {{ ref('stg_customers')}}
-- ),
-- sellers as (
--     select * from {{ ref('stg_sellers')}}
-- ),

-- -- metrics tổng hợp theo customer
-- customer_metrics as (
--     select
--         customer_id,

--         -- Recency
--         extract(day from (
--             current_timestamp - max(purchased_at)
--         ))                                  as recency_days,

--         -- Frequency
--         count(order_id)                     as frequency,

--         --Monetary
--         sum(order_value)                    as total_revenue,
--         avg(order_value)                    as avg_order_value,
--         avg(total_freight)                  as avg_feight,

--         -- Basket behavior
--         avg(item_count)                     as avg_item_per_order,
--         avg(distinct_products)              as avg_distinct_products,

--         -- Delivery experience
--         avg(delivery_delay_days)            as avg_delivery_delay,
--         sum(case when delivery_delay_days > 0
--             then 1 else 0 end)              as late_delivery_count,

--         -- Review behavior
--         avg(avg_review_score)               as avg_review_score,
--         max(has_bad_review)                 as has_bad_review,
--         sum(has_perfect_review)             as perfect_review_count,
--         sum(has_comment)                    as review_with_comment_count,

--         -- Payment behavior
--         max(used_voucher)                   as used_voucher,
--         max(used_credit_card)               as used_credit_card,
--         max(used_boleto)                    as used_boleto,
--         max(used_installment)               as used_installment,
--         avg(max_installments)               as avg_installments,

--         -- Category diversity
--         count(distinct order_category)      as category_diversity,
--         mode() within group (
--             order by order_category
--         )                                   as favorite_category,

--         -- Churn label: không mua trong 90 ngày
--         case
--             when extract(day from (
--                 current_timestamp - max(purchased_at)
--             )) > 90
--             then 1 else 0
--         end                                 as is_churned

--     from orders
--     group by customer_id
-- )

-- select
--     -- identifiers
--     c.customer_id,
--     c.customer_unique_id,
--     c.customer_city,
--     c.customer_state,

--     -- RFM
--     m.recency_days,
--     m.frequency,
--     m.total_revenue,
--     m.avg_order_value,
--     m.avg_feight,

--     -- basket
--     m.avg_item_per_order,
--     m.avg_distinct_products,

--     -- delivery
--     m.avg_delivery_delay,
--     m.late_delivery_count,

--     -- review
--     m.avg_review_score,
--     m.has_bad_review,
--     m.perfect_review_count,
--     m.review_with_comment_count,

--     -- payment
--     m.used_voucher,
--     m.used_credit_card,
--     m.used_boleto,
--     m.used_installment,
--     m.avg_installments,

--     -- product
--     m.category_diversity,
--     m.favorite_category,

--     -- target
--     m.is_churned

-- from customers c
-- inner join customer_metrics m using (customer_id)

-- thay thế 2 chỗ dùng current_timestamp bằng cách này
with orders as (
    select * from {{ ref('int_order_metrics') }}
),
customers as (
    select * from {{ ref('stg_customers') }}
),
-- lấy ngày mua hàng cuối cùng trong toàn bộ dataset làm mốc
reference_date as (
    select max(purchased_at) as max_date
    from {{ ref('int_order_metrics') }}
),
customer_metrics as (
    select
        o.customer_id,

        -- Recency: tính từ ngày cuối dataset, không phải hôm nay
        extract(day from (
            r.max_date - max(o.purchased_at)
        ))                                          as recency_days,

        count(o.order_id)                           as frequency,
        sum(o.order_value)                          as total_revenue,
        avg(o.order_value)                          as avg_order_value,
        avg(o.total_freight)                        as avg_freight,
        avg(o.item_count)                           as avg_items_per_order,
        avg(o.distinct_products)                    as avg_distinct_products,
        avg(o.delivery_delay_days)                  as avg_delivery_delay,
        sum(case when o.delivery_delay_days > 0
            then 1 else 0 end)                      as late_delivery_count,
        avg(o.avg_review_score)                     as avg_review_score,
        max(o.has_bad_review)                       as has_bad_review,
        sum(o.has_perfect_review)                   as perfect_review_count,
        sum(o.has_comment)                          as review_with_comment_count,
        max(o.used_voucher)                         as used_voucher,
        max(o.used_credit_card)                     as used_credit_card,
        max(o.used_boleto)                          as used_boleto,
        max(o.used_installment)                     as used_installment,
        avg(o.max_installments)                     as avg_installments,
        count(distinct o.order_category)            as category_diversity,
        mode() within group (
            order by o.order_category
        )                                           as favorite_category,

        -- thời gian từ đơn đầu đến đơn cuối (customer lifetime)
        extract(day from (
            max(o.purchased_at) - min(o.purchased_at)
        ))                                          as customer_lifetime_days,

        -- tốc độ mua hàng trung bình
        case
            when extract(day from (max(o.purchased_at) - min(o.purchased_at))) > 0
            then count(o.order_id)::float /
                 extract(day from (max(o.purchased_at) - min(o.purchased_at)))
            else 0
        end                                         as purchase_rate_per_day,

        -- tỷ lệ đơn giao trễ
        case
            when count(o.order_id) > 0
            then sum(case when o.delivery_delay_days > 0 then 1 else 0 end)::float
                 / count(o.order_id)
            else 0
        end                                         as late_delivery_rate,

        -- tỷ lệ review xấu
        case
            when count(o.order_id) > 0
            then sum(o.has_bad_review)::float / count(o.order_id)
            else 0
        end                                         as bad_review_rate,

        -- Churn label: không mua trong 90 ngày tính từ ngày cuối dataset
        case
            when extract(day from (
                r.max_date - max(o.purchased_at)
            )) > 90
            then 1 else 0
        end                                         as is_churned

    from orders o
    cross join reference_date r
    group by o.customer_id, r.max_date
)

select
    c.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    m.recency_days,
    m.frequency,
    m.total_revenue,
    m.avg_order_value,
    m.avg_freight,
    m.avg_items_per_order,
    m.avg_distinct_products,
    m.avg_delivery_delay,
    m.late_delivery_count,
    m.avg_review_score,
    m.has_bad_review,
    m.perfect_review_count,
    m.review_with_comment_count,
    m.used_voucher,
    m.used_credit_card,
    m.used_boleto,
    m.used_installment,
    m.avg_installments,
    m.category_diversity,
    m.favorite_category,
    m.customer_lifetime_days,
    m.purchase_rate_per_day,
    m.late_delivery_rate,
    m.bad_review_rate,
    m.is_churned

from customers c
inner join customer_metrics m using (customer_id)