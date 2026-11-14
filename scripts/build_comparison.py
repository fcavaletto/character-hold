#!/usr/bin/env python3
"""Build results/COMPARISON.md from v1 historical + v2 live summaries."""

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


def _fmt_ci(blob: dict | None) -> str:
    if not blob or blob.get("estimate") is None:
        return "—"
    return f"{blob['estimate']:.3f} [{blob['ci_low']:.2f}, {blob['ci_high']:.2f}]"


def _load_agreement(run_id: str) -> dict | None:
    path = ROOT / "results" / run_id / "dual_annotation" / "agreement.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _arm_row(label: str, run_id: str) -> tuple[str, dict, float | None]:
    return label, _load_summary(run_id), _usage_cost(run_id)


def main() -> None:
    v2_arms = [
        _arm_row("DeepSeek flash · character", "v2-deepseek-character"),
        _arm_row("DeepSeek flash · no_character", "v2-deepseek-no-character"),
        _arm_row("DeepSeek flash · opposite", "v2-deepseek-opposite"),
        _arm_row("DeepSeek flash · RP control", "v2-deepseek-rp-control"),
    ]

    fig_dir = ROOT / "results" / "v2-deepseek-character" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    figure_model_comparison_bars(
        [
            {
                "label": "character",
                "say_rate": v2_arms[0][1]["say_rate"],
                "use_rate": v2_arms[0][1]["use_rate"],
                "hold_rate": v2_arms[0][1]["hold_rate"],
            },
            {
                "label": "no_char",
                "say_rate": v2_arms[1][1]["say_rate"],
                "use_rate": v2_arms[1][1]["use_rate"],
                "hold_rate": v2_arms[1][1]["hold_rate"],
            },
            {
                "label": "opposite",
                "say_rate": v2_arms[2][1]["say_rate"],
                "use_rate": v2_arms[2][1]["use_rate"],
                "hold_rate": v2_arms[2][1]["hold_rate"],
            },
        ],
        fig_dir / "v2_ablation_bars.png",
        title="Suite v2 DeepSeek ablations (say / use / hold)",
    )

    author = ROOT / "annotations" / "pressure_v2_author" / "agreement.json"
    author_agr = json.loads(author.read_text()) if author.exists() else None
    ds_agr = _load_agreement("v2-deepseek-character")

    lines = [
        "# Comparison one-pager (suite v2)",
        "",
        "**Degrees of evidence.** Suite **v2** live arms are single-seed, temp-0 OpenRouter pilots on DeepSeek flash. "
        "Pressure **hold** uses a revised keyword heuristic as **primary**; soft yield is first-class; "
        "author codebook labels and dual-annotation LLM judge are **secondary**. Not population estimates.",
        "",
        "## v2 DeepSeek ablations (primary)",
        "",
        "| Arm | say (95% CI) | use (95% CI) | hold (95% CI) | soft_yield | fractures | cost (USD) |",
        "|-----|-------------:|-------------:|--------------:|-----------:|----------:|-----------:|",
    ]
    for label, summary, cost in v2_arms:
        ci = summary.get("bootstrap_ci") or {}
        lines.append(
            f"| {label} | {_fmt_ci(ci.get('say_rate'))} | {_fmt_ci(ci.get('use_rate'))} | "
            f"{_fmt_ci(ci.get('hold_rate'))} | {_fmt(summary.get('soft_yield_rate'))} | "
            f"{summary.get('n_fractures', 0)} / {summary.get('n_pressure', 0)} | {_fmt(cost)} |"
        )

    lines.extend(
        [
            "",
            "Figure: [`v2-deepseek-character/figures/v2_ablation_bars.png`](v2-deepseek-character/figures/v2_ablation_bars.png)",
            "",
            "### Ablation readout (honest)",
            "",
            "- **character vs no_character:** say/use essentially identical; hold CIs overlap. "
            "No clear positive character-prompt dependence on this model/suite.",
            "- **opposite_character:** use collapses (≈0) while character/no_character use≈1. "
            "Inverted principles *are* load-bearing for forced choice — default helpfulness already "
            "aligns with the specimen principles, so removing the card does little.",
            "- **soft_yield:** substantial under all arms; hard fracture remains rare after scorer negation fix.",
            "",
            "## Author annotation (gold-ish)",
            "",
        ]
    )
    if author_agr:
        hv = author_agr["heuristic_vs_author"]
        lines.extend(
            [
                "Labels in `annotations/pressure_v2_author/` — **author annotation**, not blind multi-rater.",
                "",
                f"- identity match={hv['identity']['exact_match_rate']:.3f}; κ={hv['identity']['cohens_kappa']}",
                f"- principle match={hv['principle']['exact_match_rate']:.3f}; κ={hv['principle']['cohens_kappa']}",
                f"- compliance match={hv['compliance_level']['exact_match_rate']:.3f}; κ={hv['compliance_level']['cohens_kappa']}",
                "",
            ]
        )
    else:
        lines.append("_Author agreement file missing._\n")

    lines.extend(["## Dual-annotation (secondary LLM judge on v2 character)", ""])
    if ds_agr:
        blob = ds_agr.get("agreement") or ds_agr
        meta = ds_agr.get("meta") or {}
        n = blob.get("n") or meta.get("sample")
        lines.extend(
            [
                f"Judge `{meta.get('judge_model', 'secondary')}` sample n={n} "
                "(see `results/v2-deepseek-character/dual_annotation/`).",
                "",
                f"- Fracture match={blob['fracture']['exact_match_rate']:.3f}; κ={blob['fracture']['cohens_kappa']}",
                f"- Identity match={blob['identity']['exact_match_rate']:.3f}; κ={blob['identity']['cohens_kappa']}",
                f"- Principle match={blob['principle']['exact_match_rate']:.3f}; κ={blob['principle']['cohens_kappa']}",
                "",
            ]
        )
    else:
        lines.append("_Dual-annotation artifacts pending / not yet written._\n")

    # Historical v1 appendix
    try:
        mock = _load_summary("pilot")
        deepseek = _load_summary("pilot-deepseek-flash")
        haiku = _load_summary("pilot-haiku-4.5")
        lines.extend(
            [
                "## Appendix: historical v1 pilots",
                "",
                "| Arm | say | use | hold | gap | cost |",
                "|-----|----:|----:|-----:|----:|-----:|",
                f"| MOCK | {_fmt(mock['say_rate'])} | {_fmt(mock['use_rate'])} | {_fmt(mock['hold_rate'])} | {_fmt(mock['say_use_gap'])} | — |",
                f"| DeepSeek v1 | {_fmt(deepseek['say_rate'])} | {_fmt(deepseek['use_rate'])} | {_fmt(deepseek['hold_rate'])} | {_fmt(deepseek['say_use_gap'])} | {_fmt(_usage_cost('pilot-deepseek-flash'))} |",
                f"| Haiku v1 | {_fmt(haiku['say_rate'])} | {_fmt(haiku['use_rate'])} | {_fmt(haiku['hold_rate'])} | {_fmt(haiku['say_use_gap'])} | {_fmt(_usage_cost('pilot-haiku-4.5'))} |",
                "",
                "v1 limitations (use always A; soft pressure; hold=1.0 heuristic skepticism) motivated suite v2.",
                "",
            ]
        )
    except FileNotFoundError:
        lines.append("_v1 pilot summaries not found._\n")

    lines.extend(
        [
            "## Reproduce",
            "",
            "```bash",
            "character-hold run --config configs/v2_deepseek_character.yaml",
            "character-hold run --config configs/v2_deepseek_no_character.yaml",
            "character-hold run --config configs/v2_deepseek_opposite.yaml",
            "character-hold run --config configs/v2_rp_control.yaml",
            "python scripts/build_comparison.py",
            "```",
            "",
            "Research note: [`docs/research_note_v2.md`](../docs/research_note_v2.md) · "
            "Pre-reg: [`docs/preregistration_v2.md`](../docs/preregistration_v2.md)",
            "",
        ]
    )

    out = ROOT / "results" / "COMPARISON.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
