import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests

API_URL = "http://api:8000"

def render_overview_metrics(stats):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng khách hàng",    f"{stats['total_customers']:,}")
    col2.metric("Dự đoán sẽ rời đi",  f"{stats['predicted_churned']:,}")
    col3.metric("Tỷ lệ churn",         f"{stats['churn_rate']:.1%}")
    churned_critical = stats["by_risk_level"].get("critical", 0)
    col4.metric("Nguy cơ critical",    f"{churned_critical:,}", delta="Cần xử lý ngay", delta_color="inverse")

def render_risk_donut(stats):
    risk_data = stats["by_risk_level"]
    labels = list(risk_data.keys())
    values = list(risk_data.values())
    colors = {"critical": "#e74c3c", "high": "#e67e22",
              "medium": "#f1c40f", "low": "#2ecc71", "nan": "#bdc3c7"}

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker_colors=[colors.get(l, "#bdc3c7") for l in labels]
    ))
    fig.update_layout(
        title="Phân bố Risk Level",
        showlegend=True,
        height=350,
        margin=dict(t=40, b=0, l=0, r=0)
    )
    st.plotly_chart(fig, use_container_width=True)

def render_feature_importance(stats):
    features = pd.DataFrame(stats["top_features"])
    
    # tự detect tên column đúng
    feat_col = "features" if "features" in features.columns else "feature"
    
    fig = px.bar(
        features.sort_values("importance"),
        x="importance", y=feat_col,
        orientation="h",
        title="Top 10 Features ảnh hưởng churn",
        color="importance",
        color_continuous_scale="Reds",
    )
    fig.update_layout(height=400, showlegend=False,
                      margin=dict(t=40, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

def render_churn_by_state(stats):
    state_data = pd.DataFrame(
        list(stats["churn_rate_by_state"].items()),
        columns=["state", "churn_rate"]
    ).sort_values("churn_rate", ascending=False).head(15)

    fig = px.bar(
        state_data,
        x="state", y="churn_rate",
        title="Tỷ lệ churn theo bang (Top 15)",
        color="churn_rate",
        color_continuous_scale="Reds",
    )
    fig.update_layout(height=350, margin=dict(t=40, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)