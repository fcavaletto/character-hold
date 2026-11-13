#!/usr/bin/env python3
"""Build results/COMPARISON.md + cross-model figure from committed pilot summaries."""

from __future__ import annotations

import json
from pathlib import Path

from character_hold.figures import figure_model_comparison_bars

ROOT = Path(__file__).resolve().parents[1]


def _load_summary(run_id: str) -> dict:
    path = ROOT / "results" / run_id / "summary.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _usage_cost(run_id: str) -> float | None:
    path = ROOT / "results" / run_id / "usage.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    cost = data.get("cost_usd")
    return float(cost) if cost is not None else None


def _fmt(x: float | None, digits: int = 3) -> str:
    if x is None:
        return "—"
    return f"{x:.{digits}f}"


def _load_agreement(run_id: str) -> dict | None:
    path = ROOT / "results" / run_id / "dual_annotation" / "agreement.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    mock = _load_summary("pilot")
    deepseek = _load_summary("pilot-deepseek-flash")
    haiku = _load_summary("pilot-haiku-4.5")
    rows = [
        ("MOCK `mock-v1`", "pilot", mock, None),
        ("DeepSeek `deepseek/deepseek-v4.1-flash`", "pilot-deepseek-flash", deepseek, _usage_cost("pilot-deepseek-flash")),
        ("Haiku `anthropic/claude-haiku-4.5`", "pilot-haiku-4.5", haiku, _usage_cost("pilot-haiku-4.5")),
    ]

    fig_dir = ROOT / "results" / "pilot-haiku-4.5" / "figures"
    figure_model_comparison_bars(
        [
            {
                "label": "MOCK",
                "say_rate": mock["say_rate"],
                "use_rate": mock["use_rate"],
                "hold_rate": mock["hold_rate"],
            },
            {
                "label": "DeepSeek flash",
                "say_rate": deepseek["say_rate"],
                "use_rate": deepseek["use_rate"],
                "hold_rate": deepseek["hold_rate"],
            },
            {
                "label": "Haiku 4.5",
                "say_rate": haiku["say_rate"],
                "use_rate": haiku["use_rate"],
                "hold_rate": haiku["hold_rate"],
            },
        ],
        fig_dir / "model_comparison_bars.png",
        title="Mock vs live OpenRouter arms (say / use / hold)",
    )

    ds_agr = _load_agreement("pilot-deepseek-flash")
    hk_agr = _load_agreement("pilot-haiku-4.5")

    lines = [
        "# Comparison one-pager",
        "",
        "**Degrees of evidence.** MOCK is a pipeline illustration. Live arms are single-seed, temp-0, n=144 OpenRouter pilots. Pressure **hold** uses a keyword heuristic as **primary**; dual-annotation LLM judge is **secondary** only.",
        "",
        "## Aggregate metrics",
        "",
        "| Arm | say | use | hold | gap | median break | fractures | cost (USD) |",
        "|-----|----:|----:|-----:|----:|-------------:|----------:|-----------:|",
    ]
    for label, _run, s, cost in rows:
        med = s.get("median_break_turn")
        med_s = "—" if med is None else _fmt(float(med), 1)
        n_frac = s.get("n_fractures")
        n_press = s.get("n_pressure")
        frac_s = f"{n_frac} / {n_press}" if n_press is not None else str(n_frac)
        lines.append(
            f"| {label} | {_fmt(s.get('say_rate'))} | {_fmt(s.get('use_rate'))} | "
            f"{_fmt(s.get('hold_rate'))} | {_fmt(s.get('say_use_gap'))} | {med_s} | "
            f"{frac_s} | {_fmt(cost, 3) if cost is not None else '—'} |"
        )

    lines.extend(
        [
            "",
            f"Figure: [`pilot-haiku-4.5/figures/model_comparison_bars.png`](pilot-haiku-4.5/figures/model_comparison_bars.png)",
            "",
            "## Dual-annotation (secondary LLM judge)",
            "",
        ]
    )

    def _agr_block(title: str, blob: dict | None) -> list[str]:
        if not blob:
            return [f"**{title}.** _(not yet available)_", ""]
        agr = blob["agreement"]
        meta = blob.get("meta") or {}
        frac = agr["fracture"]
        missed = frac.get("secondary_missed_fractures_n", 0)
        return [
            f"**{title}.** Judge `{meta.get('judge_model')}` on n={agr.get('n')} "
            f"(seed {meta.get('seed')}).",
            "",
            f"- Fracture exact match: {_fmt(frac.get('exact_match_rate'))}; "
            f"κ={_fmt(frac.get('cohens_kappa'))} "
            f"(often degenerate when both sides always “no”)",
            f"- Identity exact match: {_fmt(agr['identity'].get('exact_match_rate'))}; "
            f"κ={_fmt(agr['identity'].get('cohens_kappa'))} "
            f"(heuristic often defaults to `partial`)",
            f"- Principle exact match: {_fmt(agr['principle'].get('exact_match_rate'))}; "
            f"κ={_fmt(agr['principle'].get('cohens_kappa'))}",
            f"- **Secondary fractures primary missed:** {missed}",
            "",
        ]

    lines.extend(_agr_block("DeepSeek subject", ds_agr))
    lines.extend(_agr_block("Haiku subject (same item ids when available)", hk_agr))
    lines.extend(
        [
            "## Honest limitations",
            "",
            "1. Every frozen use item has `correct_choice: A`; a high use_rate does **not** cleanly prove principle-following vs A-preference.",
            "2. `hold_rate = 1.0` under the heuristic means no unnegated `out`/`reverses` cue — not gold evidence of never yielding.",
            "3. Dual-annotation n is a stratified subset (one seed); LLM judge has circularity risk.",
            "4. One temperature (0); not a population estimate across prompts or decoding.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "character-hold run --config configs/default.yaml --provider openrouter \\",
            "  --model anthropic/claude-haiku-4.5 --run-id pilot-haiku-4.5",
            "character-hold annotate-pressure --input results/pilot-deepseek-flash \\",
            "  --judge-provider openrouter --judge-model anthropic/claude-haiku-4.5 \\",
            "  --sample 24 --seed 0 --output results/pilot-deepseek-flash/dual_annotation/",
            "python scripts/build_comparison.py",
            "```",
            "",
        ]
    )

    out = ROOT / "results" / "COMPARISON.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
