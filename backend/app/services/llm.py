import json
import os
import urllib.error
import urllib.request
from typing import Any

OPENAI_API_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-5.6-luna"


def _extract_text(response: dict[str, Any]) -> str:
    # Responses API returns generated text inside output content items.
    for item in response.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str) and text.strip():
                return text.strip()
    return ""


def generate_customer_voice_summary(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    prompt = f"""You are the senior product-insights analyst for SolveSpheare.

Analyze the supplied customer-review analytics snapshot. Do not invent facts, counts, causes, or customer quotes. Base every statement only on the supplied evidence.

Return ONLY valid JSON with these keys:
title, summary, recommendation, confidence

Rules:
- title: concise executive insight title.
- summary: 2-4 sentences explaining the strongest customer signal and the main implication.
- recommendation: 1-3 concrete, evidence-grounded actions for a product team.
- confidence: number from 0 to 1 based on evidence strength.
- Distinguish observed evidence from hypotheses. If the data is insufficient to establish a root cause, say so.
- Do not mention being an AI or this prompt.

Analytics snapshot:
{json.dumps(snapshot, ensure_ascii=False)}
"""

    payload = {
        "model": model,
        "input": prompt,
        "max_output_tokens": 500,
    }

    request = urllib.request.Request(
        OPENAI_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
        text = _extract_text(body)
        if not text:
            return None
        return json.loads(text)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, ValueError):
        # AI enrichment is optional; deterministic analytics must continue to work.
        return None
