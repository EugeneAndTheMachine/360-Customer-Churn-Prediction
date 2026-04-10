from pydantic import BaseModel
from typing import Optional

class CustomerPrediction(BaseModel):
    customer_id:        str
    customer_city:      Optional[str]
    customer_state:     Optional[str]
    churn_probability:  float
    is_churned_pred:    int
    risk_level:         str
    action:             str
    frequency:          Optional[float]
    avg_order_value:    Optional[float]
    avg_review_score:   Optional[float]
    has_bad_review:     Optional[int]
    late_delivery_count: Optional[float]
    favorite_category:  Optional[str]

class PredictResponse(BaseModel):
    customer_id:       str
    churn_probability: float
    risk_level:        str
    action:            str
    top_reason:        str