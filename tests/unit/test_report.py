"""Report generation: markdown, HTML, figures."""

from __future__ import annotations

from pathlib import Path

from character_hold.analyze import FAITHFULNESS_LABELS, summarize, to_html, to_markdown, write_report
from character_hold.runner import run_evaluation
from character_hold.schema import RunConfig

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_write_report_emits_md_html_figures(tmp_path: Path):
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
        run_id="report-test",
    )
    run_dir = run_evaluation(cfg, project_root=ROOT)
    paths = write_report(run_dir)
    assert paths["summary_md"].exists()
    assert paths["report_md"].exists()
    assert paths["report_html"].exists()
    assert paths["index_md"].exists()
    figs = paths["figures"]
    assert len(figs) == 4
    for p in figs.values():
        assert p.exists()
        assert p.stat().st_size > 500

    md = paths["report_md"].read_text(encoding="utf-8")
    assert "say_rate" in md
    assert "figures/" in md
    html = paths["report_html"].read_text(encoding="utf-8")
    assert "MOCK" in html
    assert "figures/" in html
    assert "IBM Plex Sans" in html
    assert "fonts.googleapis.com" in html
    assert "median_break_turn" in html
    assert "2.000" not in html  # break turns must not use rate .3f formatting
    assert "faithful" in FAITHFULNESS_LABELS


def test_live_report_is_not_labeled_mock(tmp_path: Path):
    from character_hold.storage import write_jsonl

    run_dir = tmp_path / "live"
    run_dir.mkdir()
    write_jsonl(
        run_dir / "scored.jsonl",
        [
            {
                "record_type": "item",
                "item_id": "s1",
                "item_type": "say",
                "specimen_id": "truth_over_agreement",
                "passed": True,
                "model": "deepseek/deepseek-v4.1-flash",
                "provider": "openrouter",
                "score_detail": {},
            },
            {
                "record_type": "item",
                "item_id": "u1",
                "item_type": "use",
                "specimen_id": "truth_over_agreement",
                "passed": False,
                "model": "deepseek/deepseek-v4.1-flash",
                "provider": "openrouter",
                "score_detail": {"parse_fail": False, "method": "deterministic_choice_parse"},
            },
            {
                "record_type": "item",
                "item_id": "p1",
                "item_type": "pressure",
                "specimen_id": "truth_over_agreement",
                "passed": True,
                "fractured": False,
                "model": "deepseek/deepseek-v4.1-flash",
                "provider": "openrouter",
                "turns": [],
            },
        ],
    )
    paths = write_report(run_dir)
    html = paths["report_html"].read_text(encoding="utf-8")
    index = paths["index_md"].read_text(encoding="utf-8")
    assert "MOCK PROVIDER" not in html
    assert "deepseek/deepseek-v4.1-flash" in html
    assert "LIVE" in html
    assert "MOCK dry-run" not in index
    assert "live API run" in html


def test_to_markdown_faithfulness_semantics():
    summary = summarize([])
    text = to_markdown(
        {
            **summary,
            "n_items": 0,
            "faithfulness": {"faithful": 1, "unfaithful": 1},
        }
    )
    assert "no-pressure replay holds" in text
    assert "still reverses" in text
    html = to_html({"n_items": 0, "faithfulness": {"transparent": 1}, "by_specimen_model": []})
    assert "admits pressure" in html
