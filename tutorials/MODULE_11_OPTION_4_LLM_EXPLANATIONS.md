# Module 11 (Option 4): LLM-Assisted Forecast Explanations

This module adds a user-facing layer on top of forecasts: **natural language explanations**.

Goal: make forecasts easier to trust and act on by answering:
- *What is the forecast saying?*
- *What changed vs recent history?*
- *What factors likely drove this forecast?*
- *What should I watch out for?*

---

## ✅ What’s Implemented in This Repo

### Explanation engine
- `src/explanations/explainer.py`
  - **Template fallback** (works with no external dependencies)
  - **LLM mode** (OpenAI-compatible API) when configured
- `src/explanations/llm_client.py`
  - Minimal OpenAI-style chat client
  - Provider-agnostic via environment variables

### API endpoint
- `POST /explain` in `api/app.py`
  - Generates a forecast + explanation for a SKU
  - Uses cached dataset (Module 9 caching)

---

## 🧠 Explanation Strategy (How to Avoid Hallucinations)

LLMs are great at writing, but they can hallucinate.

We reduce risk by:
- grounding the prompt on computed facts (recent 28-day stats, forecast stats)
- instructing the LLM to only use provided facts
- falling back to a template explanation if the LLM fails

---

## ⚙️ Configure LLM Mode (Optional)

If you do nothing, explanations run in **template** mode.

To enable LLM mode set:

- `LLM_API_KEY` (required)
- `LLM_API_BASE` (optional, default `https://api.openai.com/v1`)
- `LLM_MODEL` (optional, default `gpt-4o-mini`)

Example (PowerShell):

```powershell
$env:LLM_API_KEY = \"YOUR_KEY\"
$env:LLM_MODEL = \"gpt-4o-mini\"
```

---

## 🚀 Run the API and Explain a Forecast

Start the API:

```bash
pip install -r api/requirements.txt
uvicorn api.app:app --reload --port 8000
```

Call explanation endpoint (PowerShell):

```powershell
$body = @{ sku_id = \"SKU001\"; horizon = 14; method = \"moving_average\"; ma_window = 7 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:8000/explain -ContentType \"application/json\" -Body $body
```

Response includes:
- `explanation_mode`: `template` or `llm`
- `explanation`: paragraph text
- `bullets`: key takeaways

---

## 🧩 Next Improvements (Capstone Quality)

To make explanations more accurate and actionable:

1. **Add feature importance**
   - Use ML model feature importance from Module 5
   - Pass top drivers into `ExplanationContext.top_drivers`

2. **Add event awareness**
   - holiday calendar
   - promo calendar (planned promos)

3. **Add uncertainty**
   - prediction intervals
   - “confidence” or “risk” framing

4. **Add guardrails**
   - forbid ungrounded claims
   - structured JSON output from LLM
   - automatic verification checks


