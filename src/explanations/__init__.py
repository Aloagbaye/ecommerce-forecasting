"""
Forecast explanation utilities (LLM-assisted + template fallback).
"""

from .explainer import explain_forecast, ExplanationContext, ExplanationResult

__all__ = ["explain_forecast", "ExplanationContext", "ExplanationResult"]


