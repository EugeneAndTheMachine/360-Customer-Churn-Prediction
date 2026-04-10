FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn pandas sqlalchemy \
    psycopg2-binary python-dotenv
COPY ml/predictions.csv         /app/predictions.csv
COPY ml/feature_importance.json /app/feature_importance.json
COPY api/main.py                /app/main.py
COPY api/schemas.py             /app/schemas.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]