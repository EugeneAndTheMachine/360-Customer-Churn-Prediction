import mlflow
import mlflow.sklearn
import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, roc_auc_score,
    f1_score, precision_score, recall_score
)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.linear_model import LogisticRegression
from imblearn.over_sampling import SMOTE

from config import DB_URL, FEATURE_COLS, TARGET_COL, MLFLOW_TRACKING_URI
from feature_engineering import load_data, prepare_features

from sklearn.metrics import precision_recall_curve
import numpy as np

def find_best_threshold(y_test, y_proba):
    precisions, recalls, thresholds = precision_recall_curve(y_test, y_proba)
    f1_scores = 2 * precisions * recalls / (precisions + recalls + 1e-8)
    best_idx = np.argmax(f1_scores)
    return thresholds[best_idx], f1_scores[best_idx]

def train():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("churn_prediction")

    # load data
    df = load_data()
    X, y, _ = prepare_features(df)

    # train/ test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # SMOTE for oversample class 0, balance the dataset
    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
    print(f"After SMOTE: {y_train_res.value_counts().to_dict()}")

    # List of models to find the most optimal one
    models = {
        "xgboost": XGBClassifier(
            scale_pos_weight=4,
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            random_state=42,
            eval_metric="logloss",
        ),
        "lightgbm": LGBMClassifier(
            class_weight="balanced",
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            min_child_samples=5,   # giảm từ 20 → 5
            random_state=42,
        ),
    }

    for model_name, model in models.items():
        with mlflow.start_run(run_name=model_name):
            #train
            model.fit(X_train_res, y_train_res)

            #predict
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]

            # tìm threshold tối ưu thay vì dùng mặc định 0.5
            best_thresh, best_f1 = find_best_threshold(y_test, y_proba)
            y_pred_tuned = (y_proba >= best_thresh).astype(int)

            print(f"Best threshold: {best_thresh:.3f}")
            print(classification_report(y_test, y_pred_tuned))

            mlflow.log_metric("best_threshold", best_thresh)
            mlflow.log_metric("f1_tuned", best_f1)

            #metrics
            auc = roc_auc_score(y_test, y_proba)
            f1 = f1_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)

            # log into MLflow
            mlflow.log_param("model", model_name)
            mlflow.log_param("smote", True)
            mlflow.log_metric("auc_roc", auc)
            mlflow.log_metric("f1", f1)
            mlflow.log_metric("precision", precision)
            mlflow.log_metric("recall", recall)
            mlflow.sklearn.log_model(
                model,
                artifact_path="model",
                registered_model_name=f"churn_{model_name}"
            )

            print(f"\n{'='*40}")
            print(f"Model: {model_name}")
            print(f"AUC-ROC:   {auc:.4f}")
            print(f"F1:        {f1:.4f}")
            print(f"Precision: {precision:.4f}")
            print(f"Recall:    {recall:.4f}")
            print(classification_report(y_test, y_pred))

if __name__ == "__main__":
    train()
