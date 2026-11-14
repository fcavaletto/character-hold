"""Schema + coverage checks for the live specimens/scenarios suite (144 items)."""

from __future__ import annotations

from pathlib import Path

from character_hold.runner import load_config, load_scenarios, load_specimens, validate_paths
from character_hold.schema import PressureItem, SayItem, UseItem

ROOT = Path(__file__).resolve().parents[2]


def test_live_suite_schema_and_counts():
    cfg = load_config(ROOT / "configs" / "default.yaml")
    # Resolve relative to project root
    cfg = cfg.model_copy(
        update={
            "specimens_dir": str(ROOT / "specimens"),
            "scenarios_dir": str(ROOT / "scenarios"),
        }
    )
    report = validate_paths(cfg)
    assert report["ok"], report["errors"]
    assert report["n_specimens"] == 3
    assert report["n_scenarios"] == 144
    assert report["by_type"] == {"say": 48, "use": 48, "pressure": 48}

    specimens = load_specimens(ROOT / "specimens", cfg.specimen_ids)
    assert set(specimens) == {
        "truth_over_agreement",
        "calibrated_uncertainty",
        "principle_under_authority",
    }
    for sp in specimens.values():
        assert sp.system_prompt.strip()
        assert sp.principles
        assert sp.version.startswith("2.")

    for sid, counts in report["by_specimen"].items():
        assert counts["say"] == 16, sid
        assert counts["use"] == 16, sid
        assert counts["pressure"] == 16, sid


def test_live_items_typed():
    items = load_scenarios(ROOT / "scenarios")
    # Primary 144 + rp_persona_control 12
    assert len(items) == 156
    primary = {
        "truth_over_agreement",
        "calibrated_uncertainty",
        "principle_under_authority",
    }
    primary_items = [i for i in items if i.specimen_id in primary]
    assert len(primary_items) == 144
    for item in items:
        if isinstance(item, SayItem):
            assert item.pass_patterns
            for p in list(item.pass_patterns) + list(item.fail_patterns):
                assert p.count("|") <= 2, (item.id, p)
        elif isinstance(item, UseItem):
            assert item.correct_choice.value in {"A", "B"}
        elif isinstance(item, PressureItem):
            assert item.adversary_turns
            assert item.max_turns >= 1
        else:
            raise AssertionError(f"unexpected type {type(item)}")
