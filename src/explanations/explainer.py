"""
LLM-assisted forecast explanations with safe template fallback.

Design goals:
- Provide useful explanations even without an LLM API key
- Keep outputs business-friendly and structured
- Avoid hallucinations by grounding on computed facts (recent history, promo rate, seasonality flags)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

from src.explanations.llm_client import chat_completion, load_llm_config


@dataclass(frozen=True)
class ExplanationContext:
    sku_id: str
    cutoff_date: pd.Timestamp
    horizon: int
    forecast: List[float]
    forecast_dates: List[pd.Timestamp]
    method: str
    # Optional model interpretation inputs (from Module 5)
    top_drivers: Optional[List[Dict[str, float]]] = None  # e.g., [{"feature":"lag_7","importance":0.12}, ...]


@dataclass(frozen=True)
class ExplanationResult:
    explanation: str
    mode: str  # "llm" or "template"
    bullets: List[str]


def _basic_stats(series: pd.Series) -> Dict[str, float]:
    s = series.astype(float)
    return {
        "mean": float(s.mean()),
        "median": float(s.median()),
        "std": float(s.std(ddof=0)),
        "min": float(s.min()),
        "max": float(s.max()),
        "zeros_pct": float((s == 0).mean() * 100.0),
    }


def _build_template_explanation(ctx: ExplanationContext, history: pd.DataFrame) -> ExplanationResult:
    # History is expected to be a single-SKU dataframe with date + units_sold + optional promo/price
    hist = history.sort_values("date")
    last_28 = hist.tail(28)
    stats_28 = _basic_stats(last_28["units_sold"]) if not last_28.empty else None

    fc = np.asarray(ctx.forecast, dtype=float)
    fc_mean = float(np.mean(fc))
    fc_min = float(np.min(fc))
    fc_max = float(np.max(fc))

    bullets: List[str] = []
    bullets.append(f"Forecast horizon: {ctx.horizon} days starting {ctx.forecast_dates[0].date()}.")
    bullets.append(f"Method: {ctx.method}.")
    bullets.append(f"Forecast range: {fc_min:.1f}–{fc_max:.1f} units/day (avg {fc_mean:.1f}).")

    if stats_28:
        bullets.append(
            "Recent 28-day history: "
            f"avg {stats_28['mean']:.1f}, median {stats_28['median']:.1f}, "
            f"min {stats_28['min']:.1f}, max {stats_28['max']:.1f}, "
            f"zeros {stats_28['zeros_pct']:.1f}%."
        )

    if "promotion_flag" in hist.columns:
        promo_rate = float(hist.tail(28)["promotion_flag"].astype(int).mean() * 100.0)
        bullets.append(f"Recent promo frequency (last 28 days): {promo_rate:.1f}%.")

    if ctx.top_drivers:
        top = ctx.top_drivers[:5]
        bullets.append(
            "Top drivers (from feature importance): "
            + ", ".join([f"{d.get('feature','?')} ({d.get('importance',0):.3f})" for d in top])
        )

    explanation = (
        f"This forecast for SKU {ctx.sku_id} uses the **{ctx.method}** approach and predicts an average of "
        f"**{fc_mean:.1f} units/day** over the next **{ctx.horizon} days**. "
    )
    if stats_28:
        explanation += (
            f"Compared to the last 28 days (avg {stats_28['mean']:.1f}), the forecast is "
            f"{'higher' if fc_mean > stats_28['mean'] else 'lower' if fc_mean < stats_28['mean'] else 'similar'} "
            "and stays within the recent observed range unless the series is volatile."
        )
    else:
        explanation += "Historical context is limited; interpret the forecast cautiously."

    return ExplanationResult(explanation=explanation, mode="template", bullets=bullets)


def _build_llm_prompt(ctx: ExplanationContext, history: pd.DataFrame) -> List[Dict[str, str]]:
    hist = history.sort_values("date").tail(28)
    stats_28 = _basic_stats(hist["units_sold"]) if not hist.empty else None

    payload = {
        "sku_id": ctx.sku_id,
        "method": ctx.method,
        "cutoff_date": str(ctx.cutoff_date.date()),
        "horizon": ctx.horizon,
        "forecast_mean": float(np.mean(ctx.forecast)),
        "forecast_min": float(np.min(ctx.forecast)),
        "forecast_max": float(np.max(ctx.forecast)),
        "recent_28d_stats": stats_28,
        "recent_28d_promo_rate_pct": float(hist["promotion_flag"].astype(int).mean() * 100.0) if "promotion_flag" in hist.columns and not hist.empty else None,
        "top_drivers": ctx.top_drivers,
    }

    system = (
        "You are a forecasting analyst writing concise, business-friendly explanations. "
        "Only use the provided facts. If a field is null, say it's unknown. "
        "Avoid speculation. Provide 3-6 bullet points and a short paragraph."
    )
    user = (
        "Generate a forecast explanation for a business stakeholder. "
        "Return:\n"
        "1) A short paragraph (2-4 sentences)\n"
        "2) 3-6 bullet points\n\n"
        f"Facts (JSON):\n{payload}"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def explain_forecast(ctx: ExplanationContext, history: pd.DataFrame) -> ExplanationResult:
    """
    Produce an explanation using an LLM if configured, otherwise template fallback.
    """
    cfg = load_llm_config()
    if cfg is None:
        return _build_template_explanation(ctx, history)

    try:
        messages = _build_llm_prompt(ctx, history)
        text = chat_completion(cfg, messages)
        # Best-effort bullet extraction (keep simple)
        bullets = []
        for line in text.splitlines():
            s = line.strip()
            if s.startswith(("-", "*")):
                bullets.append(s.lstrip("-* ").strip())
        if not bullets:
            bullets = ["See explanation text (no bullets detected)."]
        return ExplanationResult(explanation=text.strip(), mode="llm", bullets=bullets[:10])
    except Exception:
        # Never fail the API due to LLM issues
        return _build_template_explanation(ctx, history)


