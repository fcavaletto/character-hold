"""Anthropic Messages API provider."""

from __future__ import annotations

import os
from typing import Any

from character_hold.providers.base import ChatMessage, CompletionResult, Provider


class AnthropicProvider(Provider):
    name = "anthropic"

    def __init__(
        self,
        *,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Missing API key: set environment variable ANTHROPIC_API_KEY "
                "(value never logged)."
            )
        from anthropic import Anthropic

        self._client = Anthropic(api_key=api_key)
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
        payload = [{"role": m.role, "content": m.content} for m in messages]
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": payload,
            "temperature": self.temperature if temperature is None else temperature,
            "max_tokens": self.max_tokens if max_tokens is None else max_tokens,
        }
        if system:
            kwargs["system"] = system
        resp = client.messages.create(**kwargs)
        parts = []
        for block in getattr(resp, "content", []) or []:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        text = "".join(parts)
        raw = resp.model_dump() if hasattr(resp, "model_dump") else {"id": getattr(resp, "id", None)}
        return CompletionResult(text=text, raw=raw)
