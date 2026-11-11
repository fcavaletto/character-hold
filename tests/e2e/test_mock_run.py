from pathlib import Path

from character_hold.analyze import load_results, summarize
from character_hold.runner import load_config, run_evaluation
from character_hold.schema import RunConfig
from character_hold.storage import read_jsonl

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_e2e_mock_run_writes_jsonl_and_summary(tmp_path: Path):
    cfg = RunConfig(
        specimens_dir=str(FIXTURES / "specimens"),
        scenarios_dir=str(FIXTURES / "scenarios"),
        results_dir=str(tmp_path / "results"),
        provider="mock",
        model="mock-v1",
        temperature=0.0,
        seed=42,
        run_faithfulness=True,
        suites=["say", "use", "pressure"],
    )
    run_dir = run_evaluation(cfg, project_root=ROOT)
    assert run_dir.exists()
    raw = run_dir / "raw.jsonl"
    scored = run_dir / "scored.jsonl"
    summary_json = run_dir / "summary.json"
    summary_md = run_dir / "summary.md"
    assert raw.exists()
    assert scored.exists()
    assert summary_json.exists()
    assert summary_md.exists()

    records = list(read_jsonl(raw))
    assert any(r.get("record_type") == "meta" for r in records)
    items = [r for r in records if r.get("record_type") == "item"]
    assert len(items) == 3
    types = {r["item_type"] for r in items}
    assert types == {"say", "use", "pressure"}

    loaded = load_results(run_dir)
    summary = summarize(loaded)
    assert summary["n_items"] >= 3
    assert "by_type" in summary


def test_default_config_loads():
    cfg = load_config(ROOT / "configs" / "default.yaml")
    assert cfg.provider == "mock"
    assert cfg.temperature == 0.0
