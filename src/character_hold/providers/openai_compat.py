"""OpenAI-compatible chat completions (OpenAI + OpenRouter via base_url)."""

from __future__ import annotations

import os
from typing import Any

from character_hold.providers.base import ChatMessage, CompletionResult, Provider


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
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key_env = api_key_env
        self.base_url = base_url
        self.name = provider_name
        self._client: Any = None

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

        kwargs: dict[str, Any] = {"api_key": api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        self._client = OpenAI(**kwargs)
        return self._client

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
        resp = client.chat.completions.create(
            model=self.model,
            messages=payload,
            temperature=self.temperature if temperature is None else temperature,
            max_tokens=self.max_tokens if max_tokens is None else max_tokens,
        )
        text = (resp.choices[0].message.content or "") if resp.choices else ""
        raw = resp.model_dump() if hasattr(resp, "model_dump") else {"id": getattr(resp, "id", None)}
        return CompletionResult(text=text, raw=raw)
