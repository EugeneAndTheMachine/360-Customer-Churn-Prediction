import streamlit as st
import pandas as pd
import requests

API_URL = "http://api:8000"

RISK_COLOR = {
    "critical": "🔴",
    "high":     "🟠",
    "medium":   "🟡",
    "low":      "🟢",
}

def render_risk_table(risk_filter=None):
    params = {"limit": 200}
    if risk_filter and risk_filter != "All":
        params["risk_level"] = risk_filter.lower()

    resp = requests.get(f"{API_URL}/customers", params=params)
    data = resp.json()

    df = pd.DataFrame(data["data"])
    st.caption(f"Tổng: {data['total']:,} khách hàng")

    if df.empty:
        st.info("Không có dữ liệu.")
        return df

    # format hiển thị
    display_df = df[[
        "customer_id", "customer_city", "customer_state",
        "churn_probability", "risk_level", "frequency",
        "avg_review_score", "action"
    ]].copy()

    display_df["risk_level"]        = display_df["risk_level"].map(
        lambda x: f"{RISK_COLOR.get(x, '')} {x}"
    )
    display_df["churn_probability"] = display_df["churn_probability"].map(
        lambda x: f"{x:.1%}"
    )
    display_df.columns = [
        "Customer ID", "City", "State",
        "Churn Prob", "Risk", "Orders",
        "Avg Review", "Action"
    ]

    st.dataframe(display_df, use_container_width=True, height=400)
    return df