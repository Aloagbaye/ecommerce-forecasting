from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests
import streamlit as st


DEFAULT_API_URL = os.getenv("FORECAST_API_URL", "http://localhost:8000").rstrip("/")


def call_explain(
    api_url: str,
    payload: Dict[str, Any],
    timeout: int = 30,
) -> Dict[str, Any]:
    url = f"{api_url}/explain"
    r = requests.post(url, json=payload, timeout=timeout)
    # Let Streamlit show API error content nicely
    if r.status_code >= 400:
        raise RuntimeError(f"API error {r.status_code}: {r.text}")
    return r.json()


st.set_page_config(page_title="Forecast Explanations", layout="wide")

st.title("LLM-assisted Forecast Explanations")
st.caption("UI for `POST /explain` (FastAPI). Works in template mode or LLM mode depending on API env vars.")

with st.sidebar:
    st.header("API Connection")
    api_url = st.text_input("FastAPI base URL", value=DEFAULT_API_URL)
    st.caption("Example: http://localhost:8000")

    st.header("Forecast Inputs")
    sku_id = st.text_input("SKU ID", value="SKU001")
    horizon = st.number_input("Horizon (days)", min_value=1, max_value=365, value=14, step=1)
    method = st.selectbox("Method", options=["moving_average", "naive", "ses"], index=0)

    ma_window = st.number_input("MA window", min_value=1, max_value=365, value=7, step=1)
    ses_alpha = st.slider("SES alpha", min_value=0.01, max_value=1.0, value=0.30, step=0.01)
    cutoff_date = st.text_input("Cutoff date (optional, YYYY-MM-DD)", value="")

    run_btn = st.button("Generate explanation", type="primary", use_container_width=True)

payload: Dict[str, Any] = {
    "sku_id": sku_id.strip(),
    "horizon": int(horizon),
    "method": method,
    "ma_window": int(ma_window),
    "ses_alpha": float(ses_alpha),
    "cutoff_date": cutoff_date.strip() or None,
}

if run_btn:
    if not payload["sku_id"]:
        st.error("SKU ID is required.")
    else:
        with st.spinner("Calling API..."):
            try:
                resp = call_explain(api_url, payload)
            except Exception as e:
                st.error(str(e))
                st.stop()

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Explanation")
            st.write(resp.get("explanation", ""))

            bullets = resp.get("bullets") or []
            if bullets:
                st.subheader("Key points")
                for b in bullets:
                    st.markdown(f"- {b}")

        with col2:
            st.subheader("Metadata")
            st.write(
                {
                    "sku_id": resp.get("sku_id"),
                    "method": resp.get("method"),
                    "horizon": resp.get("horizon"),
                    "cutoff_date": resp.get("cutoff_date"),
                    "explanation_mode": resp.get("explanation_mode"),
                }
            )

        st.subheader("Raw response")
        st.json(resp)

else:
    st.info("Enter inputs in the sidebar and click **Generate explanation**.")


