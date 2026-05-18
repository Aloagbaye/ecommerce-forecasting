FROM python:3.11-slim

WORKDIR /app

# Install API deps
COPY api/requirements.txt /app/api-requirements.txt
RUN pip install --no-cache-dir -r /app/api-requirements.txt

# Copy repo code needed for forecasting logic
COPY src /app/src
COPY api /app/api

# Create the data directory tree so a volume can be mounted at runtime.
# Data is never baked into the image — mount it with:
#   docker run -v /path/to/your/data:/app/data ...
RUN mkdir -p /app/data/raw /app/data/processed /app/data/external

ENV FORECAST_DATA_PATH="data/raw/sample_sales.csv"
EXPOSE 8000

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]


