from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MAX_TOKENS = 4096


class ClientError(RuntimeError):
    pass


def call_model(
    *,
    model: str,
    system: str,
    user: str,
    api_key: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    timeout: float = 120.0,
) -> tuple[str, dict[str, int]]:
    body: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": user}],
    }
    if system:
        body["system"] = system

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
        },
    )
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ClientError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ClientError(f"URL error: {exc}") from exc

    duration_ms = int((time.monotonic() - start) * 1000)
    text = "".join(
        block["text"] for block in payload["content"] if block["type"] == "text"
    )
    usage = payload.get("usage", {})
    timing = {
        "duration_ms": duration_ms,
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
    }
    return text, timing
