# Module 9: Deployment (Forecast as a Service) — FastAPI + Docker + GitHub Actions

This module turns forecasting into a **service** you can call from other systems (frontend, ERP, dashboards).

We deploy:
- a **FastAPI** service (`api/app.py`)
- a **Docker** image (`api/Dockerfile`)
- a **GitHub Actions** workflow that builds and pushes the image to **GHCR**

---

## ✅ What You Get

### API endpoints
- `GET /health` → health check
- `POST /forecast` → generate forecast for a SKU

### Forecast request

```json
{
  "sku_id": "SKU001",
  "horizon": 14,
  "method": "moving_average",
  "ma_window": 7
}
```

### Forecast response

```json
{
  "sku_id": "SKU001",
  "horizon": 14,
  "method": "moving_average",
  "cutoff_date": "2025-12-15",
  "forecast_dates": ["2025-12-16", "..."],
  "forecast": [12.3, "..."]
}
```

---

## 🏃 Run Locally (No Docker)

From repo root:

```bash
pip install -r api/requirements.txt
uvicorn api.app:app --reload --port 8000
```

Test:
- `GET http://localhost:8000/health`

---

## 🐳 Run with Docker

Build:

```bash
docker build -f api/Dockerfile -t forecast-api:local .
```

Run:

```bash
docker run --rm -p 8000:8000 forecast-api:local
```

Optional: point to a different dataset via env var:

```bash
docker run --rm -p 8000:8000 -e FORECAST_DATA_PATH=data/raw/sample_sales.csv forecast-api:local
```

---

## 🧪 Call the API

Example (PowerShell):

```powershell
$body = @{ sku_id = \"SKU001\"; horizon = 14; method = \"moving_average\"; ma_window = 7 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:8000/forecast -ContentType \"application/json\" -Body $body
```

---

## 🤖 GitHub Actions: Build + Push to GHCR

Workflow file:
- `.github/workflows/docker.yml`

What it does:
- runs `pytest`
- builds the Docker image
- pushes to **GitHub Container Registry (GHCR)** on pushes to `main` and tags like `v1.0.0`

### Image name

The workflow publishes:

- `ghcr.io/<owner>/<repo>/forecast-api:<tag>`

Examples:
- `:main`
- `:sha-<...>`
- `:v1.0.0`

### Enable packages

In GitHub repo settings, ensure:
- Packages are enabled
- `GITHUB_TOKEN` can write packages (workflow already requests `packages: write`)

---

## 🚀 Deploying the Image (Where to run it)

Once your image is in GHCR, you can run it on:
- a VM (Docker)
- Kubernetes
- any container host (Render/Fly.io/Cloud Run/etc.)

VM example:

```bash
docker login ghcr.io
docker pull ghcr.io/<owner>/<repo>/forecast-api:main
docker run -d -p 8000:8000 ghcr.io/<owner>/<repo>/forecast-api:main
```

---

## 🔒 Notes on Production Hardening (Next Iteration)

This tutorial deployment is intentionally minimal. Next steps typically include:
- model artifact storage (not reading raw CSV on every request)
- caching (avoid reloading data)
- auth (API keys/JWT)
- request throttling
- structured logging
- monitoring (Module 10)

### ✅ Caching added (in this repo)

This repo now includes a simple in-memory dataset cache in `api/app.py`:
- the dataset is loaded once and reused across requests
- it reloads automatically if the source file’s mtime changes
- optional TTL via `FORECAST_CACHE_TTL_SECONDS`

Optional admin reload endpoint (token-guarded):
- `POST /admin/reload`
- env: `FORECAST_ADMIN_TOKEN`
- header: `X-Admin-Token: <token>`


