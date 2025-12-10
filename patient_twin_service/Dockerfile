# Dockerfile for Patient Twin Service
FROM python:3.9-slim

WORKDIR /app

COPY patient_twin_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY patient_twin_service/ .
RUN mkdir -p models

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
