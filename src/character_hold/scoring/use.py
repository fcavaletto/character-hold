"""Deterministic USE-item scoring: require CHOICE: A|B."""

from __future__ import annotations

import re
from typing import Any

from character_hold.schema import ChoiceLabel, UseItem

_CHOICE_RE = re.compile(r"\bCHOICE\s*:\s*([ABab])\b")


def extract_choice(response: str) -> ChoiceLabel | None:
    m = _CHOICE_RE.search(response or "")
    if not m:
        return None
    return ChoiceLabel(m.group(1).upper())


def score_use(item: UseItem, response: str) -> dict[str, Any]:
    choice = extract_choice(response)
    passed = choice == item.correct_choice if choice is not None else False
    return {
        "passed": passed,
        "correct_choice": item.correct_choice.value,
        "extracted_choice": choice.value if choice else None,
        "method": "deterministic_choice_parse",
    }
