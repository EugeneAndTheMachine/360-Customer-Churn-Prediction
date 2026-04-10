import streamlit as st
import requests

API_URL = "http://api:8000"

RISK_COLOR = {
    "critical": "🔴", "high":   "🟠",
    "medium":   "🟡", "low":    "🟢",
}

def render_customer_detail(customer_id):
    resp = requests.get(f"{API_URL}/customers/{customer_id}")
    if resp.status_code == 404:
        st.error("Customer not found.")
        return

    c    = resp.json()
    risk = str(c.get("risk_level", ""))
    icon = RISK_COLOR.get(risk, "")
    prob = c.get("churn_probability", 0)

    st.subheader(f"{icon} Customer: `{customer_id}`")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Churn Probability", f"{prob:.1%}")
    col2.metric("Risk Level",        risk.upper())
    col3.metric("Total Orders",      int(c.get("frequency", 0)))
    col4.metric("Avg Order Value",   f"R${c.get('avg_order_value', 0):.0f}")

    st.divider()
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("**Customer Info**")
        st.write(f"🏙️ City: {c.get('customer_city', 'N/A')}")
        st.write(f"🗺️ State: {c.get('customer_state', 'N/A')}")
        st.write(f"🛍️ Favorite Category: {c.get('favorite_category', 'N/A')}")
        st.write(f"⭐ Avg Review Score: {c.get('avg_review_score', 0):.2f}")
        st.write(f"👎 Has Bad Review: {'Yes' if c.get('has_bad_review') else 'No'}")

    with col_r:
        st.markdown("**Purchase Behavior**")
        st.write(f"📦 Late Deliveries: {int(c.get('late_delivery_count', 0))}")
        st.write(f"💳 Used Credit Card: {'Yes' if c.get('used_credit_card') else 'No'}")
        st.write(f"🎟️ Used Voucher: {'Yes' if c.get('used_voucher') else 'No'}")
        st.write(f"💰 Total Revenue: R${c.get('total_revenue', 0):.0f}")

    st.divider()
    action = c.get("action", "")
    st.markdown("**🎯 Recommended Action:**")
    if risk in ("critical", "high"):
        st.error(f"**{action}**")
    elif risk == "medium":
        st.warning(f"**{action}**")
    else:
        st.success(f"**{action}**")