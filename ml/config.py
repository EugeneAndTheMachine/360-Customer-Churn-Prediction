import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

MLFLOW_TRACKING_URI = "file:///D:/Project/360Customer/ml/mlruns"

TARGET_COL = "is_churned"
ID_COLS    = ["customer_id", "customer_unique_id"]
CAT_COLS   = ["customer_city", "customer_state", "favorite_category"]

FEATURE_COLS  = [
    "frequency", "total_revenue", "avg_order_value",
    "avg_freight", "avg_items_per_order", "avg_distinct_products",
    "avg_delivery_delay", "late_delivery_count",
    "avg_review_score", "has_bad_review", "perfect_review_count",
    "review_with_comment_count", "used_voucher", "used_credit_card",
    "used_boleto", "used_installment", "avg_installments",
    "category_diversity",
    # features mới
    "customer_lifetime_days",
    "purchase_rate_per_day",
    "late_delivery_rate",
    "bad_review_rate",
]