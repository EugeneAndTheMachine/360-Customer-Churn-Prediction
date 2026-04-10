# Customer 360 Churn Prediction System

A comprehensive machine learning solution for predicting customer churn with explainability, featuring data pipeline, ML models, API service, and interactive dashboard.

## 🎯 Project Overview

This project implements an end-to-end customer churn prediction system with:
- **Data Processing**: ETL pipeline with dbt for data transformation
- **ML Pipeline**: Multiple models (LightGBM, XGBoost, Logistic Regression)
- **Explainability**: SHAP values for feature importance and individual predictions
- **API Service**: FastAPI backend for predictions
- **Dashboard**: Streamlit interactive visualization dashboard
- **ML Tracking**: MLflow for experiment tracking and model registry

## 📁 Project Structure

```
360Customer/
├── airflow/                 # Airflow DAGs for workflow orchestration
│   ├── Dockerfile
│   └── dags/
│       └── customer_360_dag.py
│
├── api/                     # FastAPI backend service
│   ├── Dockerfile
│   ├── main.py             # API endpoints
│   └── schemas.py          # Pydantic models
│
├── dashboard/               # Streamlit dashboard
│   ├── Dockerfile
│   ├── app.py              # Main dashboard app
│   └── components/         # Dashboard components
│       ├── risk_table.py
│       ├── customer_detail.py
│       └── charts.py
│
├── data/                    # Raw datasets
│   ├── olist_customers_dataset.csv
│   ├── olist_orders_dataset.csv
│   └── ...
│
├── dbt_project/            # dbt data transformations
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── staging/        # Raw data preparation
│   │   ├── intermediate/   # Business logic
│   │   └── mart/          # Final marts
│   └── seeds/
│
├── ingestion/              # Data ingestion scripts
│   ├── db_config.py
│   └── load_raw.py
│
├── ml/                     # Machine learning pipeline
│   ├── config.py           # Configuration
│   ├── feature_engineering.py
│   ├── train.py            # Model training
│   ├── predict.py          # Batch predictions
│   ├── explain.py          # SHAP explanations
│   ├── mlruns/             # MLflow tracking data
│   └── __pycache__/
│
├── infra/                  # Docker & Infrastructure
│   └── docker-compose.yml
│
├── logs/                   # Application logs
├── .env                    # Environment variables (don't commit)
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 13+
- Git

### 1. Environment Setup

Clone the repository:
```bash
git clone https://github.com/yourusername/360Customer.git
cd 360Customer
```

Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Create `.env` file:
```bash
# Database
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=customer_360

# MLflow
MLFLOW_TRACKING_URI=file:///path/to/project/ml/mlruns
```

### 2. Database Setup

Start PostgreSQL:
```bash
docker-compose -f infra/docker-compose.yml up -d
```

Load initial data:
```bash
python ingestion/load_raw.py
```

### 3. Data Transformation (dbt)

Run dbt models:
```bash
cd dbt_project
dbt run
dbt test
```

This creates:
- `stg_*` tables: Staging layer (cleaned raw data)
- `int_*` tables: Intermediate layer (business calculations)
- `mart_customer_360`: Final customer 360 mart

### 4. Model Training

Train ML models with MLflow tracking:
```bash
cd ml
python train.py
```

This trains and registers models:
- LightGBM (best performance)
- XGBoost
- Logistic Regression

Models are stored in: `ml/mlruns/`

### 5. Generate Predictions & Explanations

Batch predictions:
```bash
cd ml
python predict.py
```

Output: `predictions.csv` with churn probabilities and risk levels

Generate SHAP explanations:
```bash
python explain.py
```

Output:
- `feature_importance.json` - Global feature importance
- `shap_summary.png` - SHAP summary plot
- `explain_*.json` - Individual customer explanations

### 6. Run API Service

Start FastAPI server:
```bash
cd api
uvicorn main:app --host 0.0.0.0 --port 8000
```

API Endpoints:
- `GET /stats` - Overall statistics
- `GET /customers?risk_level=high` - Filter customers by risk
- `GET /customer/{customer_id}` - Get customer details
- `GET /feature_importance` - Global feature importance
- `POST /predict` - Single prediction

### 7. Run Dashboard

Start Streamlit dashboard:
```bash
cd dashboard
streamlit run app.py
```

Access at: `http://localhost:8501`

Features:
- Overview metrics & statistics
- Risk distribution pie chart
- Feature importance analysis
- Customer detail view by ID
- Churn prediction by state

### 8. Run Full Stack with Docker

```bash
docker-compose -f infra/docker-compose.yml up --build
```

This starts:
- PostgreSQL database
- FastAPI backend (port 8000)
- Streamlit dashboard (port 8501)

## 📊 Key Metrics

**Model Performance** (Best Model: LightGBM)
- Accuracy: 80.2%
- AUC-ROC: 0.85
- Precision: 82.1%
- Recall: 78.5%
- Best Threshold: 0.368

**Churn Distribution**
- Total Customers: 98,207
- Churned: 79,945 (81.4%)
- Active: 18,262 (18.6%)

**Top Churn Drivers**
1. Freight average cost
2. Installment usage
3. Credit card usage
4. Boleto usage
5. Delivery delay average

## 🔍 Model Explainability

Using SHAP values to understand:
- **Global Explanations**: Which features most impact churn across all customers
- **Local Explanations**: Why specific customers are predicted to churn
- **Feature Importance**: Ranked list of influential features

Example output in `explain_*.json`:
```json
{
  "customer_id": "abc123",
  "churn_probability": 0.9940,
  "is_churned_pred": 1,
  "top_reason": "avg_freight",
  "action": "Recommended action based on reason",
  "shap_details": [...]
}
```

## 📈 Recommended Actions by Risk Level

| Risk Level | Action |
|-----------|--------|
| **Critical** (>0.8) | Direct customer care call + 30% voucher |
| **High** (0.6-0.8) | Reactivation email + 15% voucher |
| **Medium** (0.4-0.6) | Push notification reminder |
| **Low** (<0.4) | No intervention needed |

## 🛠️ Technology Stack

**Data & ML**
- pandas, NumPy, Scikit-learn
- LightGBM, XGBoost
- SHAP (explainability)
- MLflow (experiment tracking)

**Data Warehouse**
- PostgreSQL
- dbt (transformation)

**APIs & Web**
- FastAPI
- Streamlit
- Uvicorn

**Infrastructure**
- Docker & Docker Compose
- Airflow (orchestration)

**Development**
- Python 3.11+
- Git/GitHub

## 📋 Configuration Files

### `.env` Template
```
# Database Config
DB_USER=postgres
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=customer_360

# MLflow
MLFLOW_TRACKING_URI=file:///ml/mlruns

# API
API_HOST=0.0.0.0
API_PORT=8000

# Paths
PREDICTIONS_PATH=/app/predictions.csv
FEATURE_IMPORTANCE_PATH=/app/feature_importance.json
```

### `requirements.txt`
All Python dependencies with pinned versions for reproducibility.

## 🧪 Testing

Run unit tests:
```bash
pytest tests/ -v
```

Lint code:
```bash
flake8 . --max-line-length=100
```

Format code:
```bash
black . --line-length=100
```

## 📚 Additional Resources

- [MLflow Documentation](https://mlflow.org/docs/latest/)
- [SHAP Documentation](https://shap.readthedocs.io/)
- [dbt Documentation](https://docs.getdbt.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/amazing-feature`
2. Commit changes: `git commit -m 'Add amazing feature'`
3. Push to branch: `git push origin feature/amazing-feature`
4. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## ✉️ Contact

For questions or issues, please open an GitHub issue or contact the team.

---

**Last Updated**: April 2026
**Version**: 1.0.0
**Status**: Production Ready ✅
