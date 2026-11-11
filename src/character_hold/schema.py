"""Shared pydantic schema contract for specimens and scenario items."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, field_validator


class ExpectedStance(str, Enum):
    ENDORSE = "endorse"
    REJECT = "reject"


class ChoiceLabel(str, Enum):
    A = "A"
    B = "B"


class PressureType(str, Enum):
    SOCIAL_PROOF = "social_proof"
    AUTHORITY = "authority"
    URGENCY = "urgency"
    EMOTIONAL = "emotional"
    JUST_ONCE = "just_once"


class IdentityScore(str, Enum):
    IN_CHARACTER = "in_character"
    PARTIAL = "partial"
    OUT = "out"


class PrincipleScore(str, Enum):
    HOLDS = "holds"
    HEDGES = "hedges"
    REVERSES = "reverses"


class FaithfulnessVerdict(str, Enum):
    FAITHFUL = "faithful"
    UNFAITHFUL = "unfaithful"
    TRANSPARENT = "transparent"


class FractureOn(str, Enum):
    OUT = "out"
    REVERSES = "reverses"
    PARTIAL = "partial"
    HEDGES = "hedges"


class Specimen(BaseModel):
    id: str
    name: str
    version: str
    system_prompt: str
    principles: list[str] = Field(default_factory=list)
    positive_behaviors: list[str] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)
    scoring_hints: dict[str, Any] = Field(default_factory=dict)


class AdversaryTurn(BaseModel):
    turn: int
    pressure_type: PressureType
    content: str


class SayItem(BaseModel):
    id: str
    type: Literal["say"] = "say"
    specimen_id: str
    prompt: str
    expected_stance: ExpectedStance
    pass_patterns: list[str] = Field(default_factory=list)
    fail_patterns: list[str] = Field(default_factory=list)
    rubric_notes: str | None = None


class UseItem(BaseModel):
    id: str
    type: Literal["use"] = "use"
    specimen_id: str
    prompt: str
    correct_choice: ChoiceLabel
    choice_a_summary: str
    choice_b_summary: str
    rubric_notes: str | None = None


class PressureItem(BaseModel):
    id: str
    type: Literal["pressure"] = "pressure"
    specimen_id: str
    max_turns: int
    fracture_on: list[FractureOn] = Field(
        default_factory=lambda: [FractureOn.OUT, FractureOn.REVERSES]
    )
    adversary_turns: list[AdversaryTurn]
    scoring_notes: str | None = None

    @field_validator("adversary_turns")
    @classmethod
    def _sorted_turns(cls, v: list[AdversaryTurn]) -> list[AdversaryTurn]:
        return sorted(v, key=lambda t: t.turn)


ScenarioItem = Annotated[
    Union[SayItem, UseItem, PressureItem],
    Field(discriminator="type"),
]


class ScenarioFile(BaseModel):
    """Optional wrapper when a YAML file contains a list or named suite."""

    items: list[ScenarioItem] = Field(default_factory=list)


class RunConfig(BaseModel):
    specimens_dir: str = "specimens"
    scenarios_dir: str = "scenarios"
    results_dir: str = "results"
    provider: str = "mock"
    model: str = "mock-v1"
    temperature: float = 0.0
    max_tokens: int = 512
    seed: int | None = 42
    specimen_ids: list[str] | None = None
    suites: list[str] | None = Field(default_factory=lambda: ["say", "use", "pressure"])
    run_faithfulness: bool = True
    fracture_on: list[FractureOn] = Field(
        default_factory=lambda: [FractureOn.OUT, FractureOn.REVERSES]
    )
    use_llm_judge: bool = False


class TurnRecord(BaseModel):
    turn: int
    role: str
    content: str
    identity: IdentityScore | None = None
    principle: PrincipleScore | None = None


class ItemResult(BaseModel):
    item_id: str
    item_type: str
    specimen_id: str
    passed: bool | None = None
    score_detail: dict[str, Any] = Field(default_factory=dict)
    raw_response: str | None = None
    turns: list[TurnRecord] = Field(default_factory=list)
    break_turn: int | None = None
    fractured: bool | None = None
    faithfulness: FaithfulnessVerdict | None = None
    model: str | None = None
    provider: str | None = None
