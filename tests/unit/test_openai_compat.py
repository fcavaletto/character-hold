"""OpenRouter wiring and secret redaction. No network."""

from __future__ import annotations

from character_hold.providers import get_provider
from character_hold.providers.openai_compat import extract_usage, redact_secrets


def test_openrouter_provider_targets_public_api():
    provider = get_provider("openrouter", model="deepseek/deepseek-v4.1-flash")
    assert provider.name == "openrouter"
    assert provider.model == "deepseek/deepseek-v4.1-flash"
    assert provider.base_url == "https://openrouter.ai/api/v1"
    assert provider.api_key_env == "OPENROUTER_API_KEY"
    assert provider.extra_body == {"reasoning": {"effort": "none"}}
    plain = get_provider("openrouter", model="openai/gpt-4.1-mini")
    assert plain.extra_body is None


def test_redact_secrets_strips_key_shapes():
    raw = "failed sk-or-v1-abcdefghijklmnopqrstuvwxyz012345 and sk-abcdefghijklmnopqrstuvwxyz"
    cleaned = redact_secrets(raw)
    assert "sk-or-v1-" not in cleaned
    assert "sk-abc" not in cleaned
    assert "[REDACTED]" in cleaned


def test_extract_usage_keeps_counts_and_cost():
    class _Usage:
        def model_dump(self):
            return {
                "prompt_tokens": 10,
                "completion_tokens": 4,
                "total_tokens": 14,
                "cost": 0.00012,
                "completion_tokens_details": {"reasoning_tokens": 2},
            }

    class _Resp:
        usage = _Usage()

    usage = extract_usage(_Resp())
    assert usage["prompt_tokens"] == 10
    assert usage["completion_tokens"] == 4
    assert usage["reasoning_tokens"] == 2
    assert usage["cost_usd"] == 0.00012
