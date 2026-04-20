FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY docker/ /app/
COPY ingestion/ /app/ingestion/
CMD ["python", "verify.py"]
