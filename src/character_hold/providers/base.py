"""Provider base interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class CompletionResult:
    text: str
    raw: dict[str, Any] = field(default_factory=dict)


class Provider(ABC):
    name: str
    model: str

    @abstractmethod
    def complete(
        self,
        messages: list[ChatMessage],
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> CompletionResult:
        """Return a single assistant completion."""
