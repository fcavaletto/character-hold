"""OpenAI-compatible chat completions (OpenAI + OpenRouter via base_url)."""

from __future__ import annotations

import os
import re
import time
from typing import Any

from character_hold.providers.base import ChatMessage, CompletionResult, Provider

# Never log or re-raise an API key. OpenRouter keys look like sk-or-v1-…;
# OpenAI keys look like sk-….
_SECRET_RE = re.compile(r"\bsk-(?:or-v1-)?[A-Za-z0-9_\-]{8,}\b")
_RETRY_STATUS = {408, 409, 429, 500, 502, 503, 504}
_MAX_ATTEMPTS = 5


def redact_secrets(text: str) -> str:
    """Strip credential-shaped substrings from error text."""
    return _SECRET_RE.sub("[REDACTED]", text or "")


def _status_code(exc: BaseException) -> int | None:
    status = getattr(exc, "status_code", None)
    if isinstance(status, int):
        return status
    response = getattr(exc, "response", None)
    status = getattr(response, "status_code", None)
    return status if isinstance(status, int) else None


def _retryable(exc: BaseException) -> bool:
    status = _status_code(exc)
    if status in _RETRY_STATUS:
        return True
    name = type(exc).__name__
    if status is None and name in {
        "APIConnectionError",
        "APITimeoutError",
        "RateLimitError",
        "InternalServerError",
        "ConnectError",
        "ReadTimeout",
        "WriteTimeout",
        "RemoteProtocolError",
    }:
        return True
    return False


def extract_usage(resp: Any) -> dict[str, Any]:
    """Pull token counts and provider-reported cost. Omits request ids and headers."""
    usage = getattr(resp, "usage", None)
    if usage is None:
        return {}
    data = usage.model_dump() if hasattr(usage, "model_dump") else {}
    if not isinstance(data, dict):
        return {}
    details = data.get("completion_tokens_details") or {}
    if not isinstance(details, dict):
        details = {}
    out: dict[str, Any] = {
        "prompt_tokens": int(data.get("prompt_tokens") or 0),
        "completion_tokens": int(data.get("completion_tokens") or 0),
        "total_tokens": int(data.get("total_tokens") or 0),
        "reasoning_tokens": int(details.get("reasoning_tokens") or 0),
    }
    cost = data.get("cost")
    if cost is not None:
        try:
            out["cost_usd"] = float(cost)
        except (TypeError, ValueError):
            pass
    return out


class OpenAICompatProvider(Provider):
    def __init__(
        self,
        *,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
        api_key_env: str = "OPENAI_API_KEY",
        base_url: str | None = None,
        provider_name: str = "openai",
        extra_body: dict[str, Any] | None = None,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key_env = api_key_env
        self.base_url = base_url
        self.name = provider_name
        self.extra_body = extra_body
        self._client: Any = None
        self.upstream_model: str | None = None
        self.usage_totals: dict[str, float | int] = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "reasoning_tokens": 0,
            "cost_usd": 0.0,
            "n_calls": 0,
            "n_length_truncated": 0,
        }

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"Missing API key: set environment variable {self.api_key_env} "
                f"(value never logged)."
            )
        from openai import OpenAI

        kwargs: dict[str, Any] = {
            "api_key": api_key,
            "timeout": 180.0,
            # Retries are handled here so error text can be redacted.
            "max_retries": 0,
        }
        if self.base_url:
            kwargs["base_url"] = self.base_url
        # OpenRouter attributes optional HTTP-Referer / X-Title. They are not
        # credentials. A probe against /api/v1 succeeded with bearer auth alone;
        # the headers are still sent because OpenRouter documents them.
        if self.name == "openrouter":
            kwargs["default_headers"] = {
                "HTTP-Referer": "https://github.com/fcavaletto/character-hold",
                "X-Title": "character-hold",
            }
        self._client = OpenAI(**kwargs)
        return self._client

    def _account(self, resp: Any) -> dict[str, Any]:
        usage = extract_usage(resp)
        finish = None
        if getattr(resp, "choices", None):
            finish = getattr(resp.choices[0], "finish_reason", None)
        self.usage_totals["n_calls"] = int(self.usage_totals["n_calls"]) + 1
        for key in ("prompt_tokens", "completion_tokens", "total_tokens", "reasoning_tokens"):
            self.usage_totals[key] = int(self.usage_totals[key]) + int(usage.get(key) or 0)
        if "cost_usd" in usage:
            self.usage_totals["cost_usd"] = float(self.usage_totals["cost_usd"]) + float(usage["cost_usd"])
        if finish == "length":
            self.usage_totals["n_length_truncated"] = int(self.usage_totals["n_length_truncated"]) + 1
        echoed = getattr(resp, "model", None)
        if isinstance(echoed, str) and echoed:
            self.upstream_model = echoed
        usage["finish_reason"] = finish
        return usage

    def complete(
        self,
        messages: list[ChatMessage],
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> CompletionResult:
        client = self._get_client()
        payload: list[dict[str, str]] = []
        if system:
            payload.append({"role": "system", "content": system})
        for m in messages:
            payload.append({"role": m.role, "content": m.content})
        create_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": payload,
            "temperature": self.temperature if temperature is None else temperature,
            "max_tokens": self.max_tokens if max_tokens is None else max_tokens,
        }
        if self.extra_body:
            create_kwargs["extra_body"] = self.extra_body
        resp: Any = None
        for attempt in range(_MAX_ATTEMPTS):
            try:
                resp = client.chat.completions.create(**create_kwargs)
                break
            except Exception as exc:
                if not _retryable(exc) or attempt + 1 >= _MAX_ATTEMPTS:
                    safe = redact_secrets(f"{type(exc).__name__}: {exc}")
                    raise RuntimeError(
                        f"OpenAI-compatible completion failed ({self.name}, model={self.model}): {safe[:500]}"
                    ) from None
                time.sleep(min(2**attempt, 20))
        if resp is None:
            raise RuntimeError(f"OpenAI-compatible completion failed ({self.name}, model={self.model})")
        text = (resp.choices[0].message.content or "") if resp.choices else ""
        usage = self._account(resp)
        # Persist usage counts only. Drop the raw payload so logs cannot grow
        # request echoes or provider metadata that is not needed for scoring.
        return CompletionResult(text=text, raw={"usage": usage, "model": self.upstream_model})
