select
    review_id,
    order_id,
    review_score,
    case when review_score <= 2 then 1 else 0 end   as is_bad_review,
    case when review_score >= 4 then 1 else 0 end   as is_perfect_review,
    case
        when review_comment_message is not null
        and length(trim(review_comment_message)) > 0 
        then 1 else 0
    end                                             as has_comment,
    review_creation_date::timestamp                 as created_at
from {{ source('olist', 'raw_order_reviews') }}