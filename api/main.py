import os
import json
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Customer 360 Churn API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# load predictions.csv một lần khi startup
PREDICTIONS_PATH = os.getenv("PREDICTIONS_PATH", "/app/predictions.csv")
FEATURE_IMPORTANCE_PATH = os.getenv("FEATURE_IMPORTANCE_PATH", "/app/feature_importance.json")

df_pred = None
feature_importance = None

@app.on_event("startup")
def load_data():
    global df_pred, feature_importance
    df_pred = pd.read_csv(PREDICTIONS_PATH)
    df_pred["risk_level"] = df_pred["risk_level"].astype(str)
    with open(FEATURE_IMPORTANCE_PATH) as f:
        feature_importance = json.load(f)
    print(f"Loaded {len(df_pred):,} predictions")


@app.get("/")
def root():
    return {"status": "ok", "total_customers": len(df_pred)}


@app.get("/customers")
def get_customers(
    risk_level: str = None,
    limit: int = 100,
    offset: int = 0
):
    """Lấy danh sách customers, filter theo risk_level."""
    df = df_pred.copy()
    if risk_level:
        df = df[df["risk_level"] == risk_level]
    total = len(df)
    df    = df.sort_values("churn_probability", ascending=False)
    df    = df.iloc[offset: offset + limit]
    return {
        "total":   total,
        "data":    df.to_dict(orient="records")
    }


@app.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    """Lấy thông tin + prediction của 1 khách hàng."""
    row = df_pred[df_pred["customer_id"] == customer_id]
    if len(row) == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return row.iloc[0].to_dict()


@app.get("/stats")
def get_stats():
    """Thống kê tổng quan cho dashboard."""
    total       = len(df_pred)
    churned     = int(df_pred["is_churned_pred"].sum())
    by_risk     = df_pred["risk_level"].value_counts().to_dict()
    by_state    = df_pred.groupby("customer_state")["is_churned_pred"].mean().round(3).to_dict()

    return {
        "total_customers":   total,
        "predicted_churned": churned,
        "churn_rate":        round(churned / total, 3),
        "by_risk_level":     by_risk,
        "churn_rate_by_state": by_state,
        "top_features":      feature_importance[:10],
    }


@app.get("/feature-importance")
def get_feature_importance():
    return feature_importance