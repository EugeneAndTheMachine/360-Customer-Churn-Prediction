import shap
import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

from config import FEATURE_COLS, MLFLOW_TRACKING_URI
from feature_engineering import load_data, prepare_features

BEST_THREADSHOLD = 0.368

def load_model():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    return mlflow.sklearn.load_model(
        model_uri="models:/churn_lightgbm/latest"
    )

def explain_global(model, X):
    "SHAP global - feature importance whole dataset"
    print("Computing SHAP values (global)...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    # Light GBM binary, shap_values is list with two values [class0, class1]
    if isinstance(shap_values, list):
        shap_values = shap_values[1]

    # mean absolute SHAP pervalue
    importance = pd.DataFrame({
        "features":     FEATURE_COLS,
        "importance":   np.abs(shap_values).mean(axis=0)
    }).sort_values("importance", ascending=False)

    print("\nTop features that impact to the churn:")
    print(importance.head(10).to_string(index=False))

    # Storing into JSON for dashboard visualization
    importance.to_json("feature_importance.json", orient="records", indent=2)
    print("\nSaved feature_importance.json")

    # Plot
    shap.summary_plot(
        shap_values, X,
        feature_names=FEATURE_COLS,
        show=False
    )
    plt.tight_layout()
    plt.savefig("shap_summary.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved shap_summary.png")

    return shap_values, importance


def explain_single(model, X, ids, customer_id):
    "SHAP - explain the reason of a specific customer"
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    if isinstance(shap_values, list):
        shap_values = shap_values[1]

    # query the index of the customer
    idx = ids[ids["customer_id"] == customer_id].index
    if len(idx) == 0:
        print(f"Customer {customer_id} is not founded!")
        return None
    
    idx         = idx[0]
    local_shap = shap_values[idx]
    local_X     = X.iloc[idx]
    y_proba     = model.predict_proba(X.iloc[[idx]])[:, 1][0]
    is_churned  = int(y_proba >= BEST_THREADSHOLD)

    print(f"\nCustomer: {customer_id}")
    print(f"Churn probability: {y_proba:.3f}")
    print(f"Predicted churned: {'Yes' if is_churned else 'No'}")

    # Top 5 reason
    local_df = pd.DataFrame({
        "feature": FEATURE_COLS,
        "value": local_X.values,
        "shap": local_shap
    }).sort_values("shap", ascending=False)

    print("\nTop 5 feature that lead customer to churn:")
    print(local_df[local_df["shap"] > 0].head(5).to_string(index=False))

    print("\nTop 5 feature that lead customer to stay:")
    print(local_df[local_df["shap"] < 0].tail(5).to_string(index=False))

    # recommendation based on top reasons
    top_reason = local_df.iloc[0]["feature"]
    action_map = {
        "frequency"             : "Not many products for a shopping - send recommendation based on their favorite_category",
        "avg_review_score"      : "Low review - prior customer service/ support, focus on customer shopping experience",
        "has_bad_review"        : "Has a bad review/ experience - contact for support + gifting/ voucher",
        "late_delivery_count"   : "Delivery latency - escalate on logistic team",
        "avg_order_value"       : "Bill price is low - bundle deal recommendation",
        "total_revenue"         : "Low income - gift loyalty points",
        "bad_review_rate"       : "High rate of bad reviews - rechecking the quality of the product",
        "late_delivery_rate"    : "High rate of late delivery - change the delivery team",
        "purchase_rate_per_day" : "Low shopping frequency rate - Open reactivation campaign",
    }
    action = action_map.get(top_reason, "Gifting voucher 10% for the next shopping")
    print(f"\nRecommendation Action: {action}")

    # Storing result
    result = {
        "customer_id":       customer_id,
        "churn_probability": round(y_proba, 4),
        "is_churned_pred":   is_churned,
        "top_reason":        top_reason,
        "action":            action,
        "shap_details":      local_df.to_dict(orient="records")
    }
    with open(f"explain_{customer_id}.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"Saved explain_{customer_id}.json")

    return result

def run_explain():
    df = load_data()
    X, y, ids = prepare_features(df)
    model = load_model()

    # Global explanation
    shap_values, importance = explain_global(model, X)

    # Local explaination - Example with 1 customer
    y_proba = model.predict_proba(X)[:, 1]
    top_idx = np.argmax(y_proba)
    top_customer = ids.iloc[top_idx]["customer_id"]
    print(f"\nExplaination for the customer with highest risk: {top_customer}")
    explain_single(model, X, ids, top_customer)   

if __name__ == "__main__":
    run_explain()