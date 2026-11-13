"""LLM provider adapters."""

from __future__ import annotations

from character_hold.providers.anthropic import AnthropicProvider
from character_hold.providers.base import Provider
from character_hold.providers.mock import MockProvider
from character_hold.providers.openai_compat import OpenAICompatProvider


def get_provider(
    name: str,
    *,
    model: str,
    temperature: float = 0.0,
    max_tokens: int = 512,
    seed: int | None = None,
) -> Provider:
    key = name.lower().strip()
    if key == "mock":
        return MockProvider(model=model, temperature=temperature, max_tokens=max_tokens, seed=seed)
    if key == "openai":
        return OpenAICompatProvider(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key_env="OPENAI_API_KEY",
            base_url=None,
            provider_name="openai",
        )
    if key == "openrouter":
        # DeepSeek V4 Flash spends the max_tokens budget on hidden reasoning and
        # can return empty content when that budget is 512. Ask OpenRouter for no
        # reasoning so the configured cap applies to the visible reply.
        extra_body = None
        if "deepseek" in model.lower():
            extra_body = {"reasoning": {"effort": "none"}}
        return OpenAICompatProvider(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            provider_name="openrouter",
            extra_body=extra_body,
        )
    if key == "anthropic":
        return AnthropicProvider(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    raise ValueError(f"Unknown provider: {name!r}")


__all__ = [
    "Provider",
    "MockProvider",
    "OpenAICompatProvider",
    "AnthropicProvider",
    "get_provider",
]
