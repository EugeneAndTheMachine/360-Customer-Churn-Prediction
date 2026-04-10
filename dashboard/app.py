import streamlit as st
import requests

st.set_page_config(
    page_title="Customer 360 — Churn Dashboard",
    page_icon="📊",
    layout="wide"
)

API_URL = "http://api:8000"

from components.risk_table      import render_risk_table
from components.charts          import (
    render_overview_metrics, render_risk_donut,
    render_feature_importance, render_churn_by_state
)
from components.customer_detail import render_customer_detail


def main():
    st.title("📊 Customer 360 — Churn Prediction Dashboard")

    # load stats
    try:
        stats = requests.get(f"{API_URL}/stats").json()
    except Exception:
        st.error("Không kết nối được API. Đảm bảo FastAPI đang chạy.")
        return

    # === Tab layout ===
    tab1, tab2, tab3 = st.tabs(["📈 Overview", "🚨 Risk List", "🔍 Customer Detail"])

    with tab1:
        render_overview_metrics(stats)
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            render_risk_donut(stats)
        with col2:
            render_feature_importance(stats)
        st.divider()
        render_churn_by_state(stats)

    with tab2:
        st.subheader("Danh sách khách hàng theo risk")
        risk_filter = st.selectbox(
            "Filter theo risk level:",
            ["All", "Critical", "High", "Medium", "Low"]
        )
        df = render_risk_table(risk_filter)

        # click vào row để xem detail
        if df is not None and not df.empty:
            selected_id = st.selectbox(
                "Chọn customer để xem chi tiết:",
                options=[""] + df["customer_id"].tolist()
            )
            if selected_id:
                render_customer_detail(selected_id)

    with tab3:
        st.subheader("Tìm kiếm khách hàng")
        customer_id = st.text_input("Nhập Customer ID:")
        if customer_id:
            render_customer_detail(customer_id)


if __name__ == "__main__":
    main()