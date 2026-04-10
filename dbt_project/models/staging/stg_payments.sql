select
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value,
    case when payment_type = 'voucher' then 1 else 0 end as used_voucher,
    case when payment_type = 'credit_card' then 1 else 0 end as used_credit_card,
    case when payment_type = 'boleto' then 1 else 0 end as used_boleto,
    case when payment_installments > 1 then 1 else 0 end as used_installment
from {{ source('olist', 'raw_order_payments') }}