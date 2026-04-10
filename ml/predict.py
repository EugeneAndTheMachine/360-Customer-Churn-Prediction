import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from config import DB_URL, FEATURE_COLS, TARGET_COL, MLFLOW_TRACKING_URI
from feature_engineering import load_data, prepare_features

BEST_THREADSHOLD = 0.368

def load_model():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    model = mlflow.sklearn.load_model(
        model_uri="models:/churn_lightgbm/latest"
    )
    print("Model loaded: churn_lightgbm (latest)")
    return model

def predict(model, X, ids):
    y_proba = model.predict_proba(X)[:, 1]
    y_pred = (y_proba >= BEST_THREADSHOLD).astype(int)

    result = ids.copy()
    result["churn_probability"] = y_proba
    result["is_churned_pred"] = y_pred
    result["risk_level"] = pd.cut(
        y_proba,
        bins=[0,0.4,0.6,0.8,1.0],
        labels=["low", "medium", "high", "critical"]
    )
    return result

def recommend_action(row):
    prob = row["churn_probability"]
    level = row["risk_level"]

    if level == "critical":
        return "Contact for shopping experience support and 30% voucher gift for next shopping"
    elif level == "high":
        return "Send email and 15% voucher gift for next shopping"
    elif level == "medium":
        return "Push notification for customer to notice"
    else:
        return "Ignore"

def run_prediction():
    # load data + model
    df = load_data()
    X, y, ids = prepare_features(df)
    model = load_model()

    # prediction
    result = predict(model, X, ids)
    result["action"] = result.apply(recommend_action, axis=1)

    # join with the other infomation for visualization
    extra_cols = [
        "customer_id", "customer_city", "customer_state",
        "frequency", "avg_order_value", "avg_review_score",
        "has_bad_review", "late_delivery_count", "favorite_category"
    ]

    df_extra = df[extra_cols]
    result = result.merge(df_extra, on="customer_id", how="left")

    # sort based on the highest risk
    result = result.sort_values("churn_probability", ascending=False)

    # storing the result into files for the dashboard
    result.to_csv("predictions.csv", index=False)
    print(f"Saved {len(result):,} predictions to predictions.csv")

    # list of 10 customers with highest risk
    print("Top 10 customer with highest churn:")
    print(result[[
        "customer_id", "churn_probability", "risk_level",
        "frequency", "avg_review_score", "action"
    ]].head(10).to_string(index=False))

    return result

if __name__ == "__main__":
    run_prediction()