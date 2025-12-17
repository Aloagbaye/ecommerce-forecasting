# Streamlit App Tutorial (LLM Forecast Explanations UI)

This repo includes a Streamlit UI that calls the FastAPI endpoint:
- `POST /explain`

File:
- `streamlit_app.py`

---

## ✅ 1) Install dependencies

From repo root:

```bash
pip install -r requirements.txt
```

---

## ✅ 2) Start the FastAPI service

From repo root:

```bash
pip install -r api/requirements.txt
uvicorn api.app:app --reload --port 8000
```

Health check:
- `GET http://localhost:8000/health`

---

## ✅ 3) Start Streamlit

In a second terminal (repo root):

```bash
streamlit run streamlit_app.py
```

The app will open in your browser.

---

## ⚙️ Configure the API URL (optional)

By default, Streamlit calls:
- `http://localhost:8000`

To change it:

### Option A: environment variable

```bash
set FORECAST_API_URL=http://localhost:8000
```

### Option B: in the Streamlit sidebar

Edit the “FastAPI base URL” field.

---

## 🤖 Enable LLM mode (optional)

The API will use template explanations unless you set:
- `LLM_API_KEY`

Example (PowerShell):

```powershell
$env:LLM_API_KEY = "YOUR_KEY"
$env:LLM_MODEL = "gpt-4o-mini"
```

Then restart the API server.

---

## 🧪 Troubleshooting

### “API error 500: Forecast data not found”
Ensure the file exists:
- `data/raw/sample_sales.csv`

Generate it if needed:

```bash
python scripts/generate_sample_data.py --output data/raw/sample_sales.csv --days 730 --skus 100
```

### “Connection refused”
Make sure FastAPI is running and the Streamlit sidebar URL matches:
- `http://localhost:8000`

---


