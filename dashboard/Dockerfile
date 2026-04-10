FROM python:3.11-slim
WORKDIR /app
RUN pip install streamlit plotly pandas requests
COPY dashboard/app.py           /app/app.py
COPY dashboard/components/      /app/components/
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", "--server.address=0.0.0.0"]