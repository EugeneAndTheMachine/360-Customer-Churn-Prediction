with translation as (
    select
        product_category_name,
        product_category_name_english
    from {{ source('olist', 'raw_product_category_name_translation') }}
)

select
    p.product_id,
    coalesce(t.product_category_name_english, 'unknown')       as category,
    p.product_name_lenght                                      as product_name_length,
    p.product_description_lenght                               as product_description_length,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
from {{ source('olist', 'raw_products') }} p
left join translation t using (product_category_name)