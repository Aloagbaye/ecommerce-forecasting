FROM python:3.11-slim

WORKDIR /app

# Install API deps
COPY api/requirements.txt /app/api-requirements.txt
RUN pip install --no-cache-dir -r /app/api-requirements.txt

# Copy repo code needed for forecasting logic
COPY src /app/src
COPY api /app/api
COPY data /app/data

ENV FORECAST_DATA_PATH="data/raw/sample_sales.csv"
EXPOSE 8000

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]


