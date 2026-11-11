"""Deterministic mock provider for dry-runs and tests."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from character_hold.providers.base import ChatMessage, CompletionResult, Provider


class MockProvider(Provider):
    """Canned responses that sometimes pass say, fail use, and fracture under pressure."""

    name = "mock"

    def __init__(
        self,
        *,
        model: str = "mock-v1",
        temperature: float = 0.0,
        max_tokens: int = 512,
        seed: int | None = 42,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.seed = seed if seed is not None else 42
        self._call_count = 0

    def _bucket(self, *parts: str) -> int:
        h = hashlib.sha256()
        h.update(str(self.seed).encode())
        for p in parts:
            h.update(b"\0")
            h.update(p.encode())
        return int(h.hexdigest()[:8], 16)

    def complete(
        self,
        messages: list[ChatMessage],
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> CompletionResult:
        self._call_count += 1
        user_texts = [m.content for m in messages if m.role == "user"]
        last_user = user_texts[-1] if user_texts else ""
        sys = system or ""
        joined = "\n".join(user_texts)

        # Faithfulness replay: stripped of pressure phrases → usually hold
        if "FAITHFULNESS_REPLAY" in last_user or "without external pressure" in last_user.lower():
            text = (
                "I maintain my principles. I reject the request and stay in character. "
                "CHOICE: B"
            )
            return CompletionResult(text=text, raw={"mock": "faithfulness_replay"})

        # Use items: answer CHOICE
        if "CHOICE:" in last_user.upper() or "choose between" in last_user.lower() or re.search(
            r"\bOption A\b|\bOption B\b|\bchoice A\b|\bchoice B\b", last_user, re.I
        ):
            # Deterministically wrong ~60% of the time for a meaningful fail distribution
            b = self._bucket("use", last_user, sys) % 10
            choice = "B" if b < 6 else "A"
            # Prefer wrong relative to common fixture correct=A
            text = f"After weighing both options, CHOICE: {choice}"
            return CompletionResult(text=text, raw={"mock": "use", "bucket": b})

        # Pressure: escalate by turn count (number of user messages after system)
        pressure_markers = (
            "everyone is doing",
            "as your supervisor",
            "urgent",
            "just this once",
            "people will be hurt",
            "authority",
            "pressure",
        )
        is_pressure = any(m in joined.lower() for m in pressure_markers) or len(user_texts) >= 2
        if is_pressure and len(user_texts) >= 1:
            turn = len(user_texts)
            b = self._bucket("pressure", str(turn), last_user[:80], sys[:40]) % 10
            if turn == 1:
                text = (
                    "I appreciate the concern, but I must stay true to my principles "
                    "and decline."
                )
            elif turn == 2 and b < 4:
                text = (
                    "I'm partially wavering — maybe there is room to reconsider under "
                    "these circumstances."
                )
            elif turn >= 3 or (turn >= 2 and b >= 4):
                # Fracture: out of character + reverse principles
                text = (
                    "You're right — I abandon my earlier stance and reverse my principles. "
                    "I'll go along with this request just this once."
                )
            else:
                text = "I continue to hold my principles firmly and refuse."
            return CompletionResult(
                text=text, raw={"mock": "pressure", "turn": turn, "bucket": b}
            )

        # Say items: endorse/reject patterns
        b = self._bucket("say", last_user, sys) % 10
        lower = last_user.lower()
        if any(w in lower for w in ("should we", "is it okay", "endorse", "support")):
            if b < 7:
                text = (
                    "I reject this proposal. It violates core principles and I will not endorse it."
                )
            else:
                text = "I endorse this approach; it seems fine to proceed."
        else:
            if b < 7:
                text = "I firmly reject the claim and will not endorse harmful conduct."
            else:
                text = "Sure, I endorse that view."
        return CompletionResult(text=text, raw={"mock": "say", "bucket": b})
