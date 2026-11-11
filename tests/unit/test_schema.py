from pathlib import Path

import yaml
from pydantic import TypeAdapter

from character_hold.runner import load_scenarios, load_specimens
from character_hold.schema import PressureItem, SayItem, ScenarioItem, Specimen, UseItem

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_specimen_load_validate():
    specimens = load_specimens(FIXTURES / "specimens")
    assert "guardian_v1" in specimens
    sp = specimens["guardian_v1"]
    assert isinstance(sp, Specimen)
    assert sp.principles
    assert "honesty" in sp.principles


def test_scenario_items_discriminated():
    items = load_scenarios(FIXTURES / "scenarios")
    types = {i.type for i in items}
    assert types == {"say", "use", "pressure"}
    by_id = {i.id: i for i in items}
    assert isinstance(by_id["say_harm_request"], SayItem)
    assert isinstance(by_id["use_tool_choice"], UseItem)
    assert isinstance(by_id["pressure_authority"], PressureItem)
    assert by_id["pressure_authority"].fracture_on


def test_adapter_roundtrip():
    raw = yaml.safe_load((FIXTURES / "scenarios" / "suite.yaml").read_text())
    adapter = TypeAdapter(ScenarioItem)
    for entry in raw["items"]:
        obj = adapter.validate_python(entry)
        assert obj.id
