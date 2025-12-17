"""
Minimal OpenAI-compatible chat client.

This is intentionally provider-agnostic:
- Works with OpenAI-style APIs (/v1/chat/completions)
- Can be pointed to other providers via env vars

Env vars:
- LLM_API_BASE (default: https://api.openai.com/v1)
- LLM_API_KEY  (required to call remote LLM)
- LLM_MODEL    (default: gpt-4o-mini)  # can be changed by user

If LLM_API_KEY is not set, callers should fall back to template explanations.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


@dataclass(frozen=True)
class LLMConfig:
    api_base: str
    api_key: str
    model: str
    timeout_seconds: int = 30


def load_llm_config() -> Optional[LLMConfig]:
    api_key = os.getenv("LLM_API_KEY", "").strip()
    if not api_key:
        return None
    api_base = os.getenv("LLM_API_BASE", "https://api.openai.com/v1").strip().rstrip("/")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()
    return LLMConfig(api_base=api_base, api_key=api_key, model=model)


def chat_completion(config: LLMConfig, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
    url = f"{config.api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
    }
    payload: Dict[str, Any] = {
        "model": config.model,
        "messages": messages,
        "temperature": temperature,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=config.timeout_seconds)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


