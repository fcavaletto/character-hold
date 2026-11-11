"""Summary tables from scored run results."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

from character_hold.storage import read_jsonl, write_json


def load_results(input_path: str | Path) -> list[dict[str, Any]]:
    p = Path(input_path)
    if p.is_dir():
        # Prefer scored.jsonl, else raw.jsonl
        for name in ("scored.jsonl", "raw.jsonl"):
            candidate = p / name
            if candidate.exists():
                return list(read_jsonl(candidate))
        # Concatenate all jsonl
        rows: list[dict[str, Any]] = []
        for f in sorted(p.glob("*.jsonl")):
            rows.extend(read_jsonl(f))
        return rows
    return list(read_jsonl(p))


def _iter_items(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in records if r.get("record_type") not in {"meta", "error"}]


def _rate(passed: int, n: int) -> float | None:
    if n <= 0:
        return None
    return passed / n


def _fracture_type(turns: list[dict[str, Any]], break_turn: int | None) -> str | None:
    if break_turn is None:
        return None
    for t in turns:
        if int(t.get("turn") or -1) != int(break_turn):
            continue
        identity = (t.get("identity") or "").lower()
        principle = (t.get("principle") or "").lower()
        out = identity == "out"
        rev = principle == "reverses"
        if out and rev:
            return "both"
        if out:
            return "out"
        if rev:
            return "reverses"
        if identity == "partial":
            return "partial"
        if principle == "hedges":
            return "hedges"
        return identity or principle or "unknown"
    return "unknown"


def _cell_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        itype = r.get("item_type") or r.get("type") or "unknown"
        by_type[itype].append(r)

    say = by_type.get("say", [])
    use = by_type.get("use", [])
    pressure = by_type.get("pressure", [])

    say_pass = sum(1 for r in say if r.get("passed") is True)
    use_pass = sum(1 for r in use if r.get("passed") is True)
    use_parse_fail = sum(
        1
        for r in use
        if (r.get("score_detail") or {}).get("parse_fail") is True
        or (
            r.get("passed") is False
            and (r.get("score_detail") or {}).get("extracted_choice") is None
            and (r.get("score_detail") or {}).get("method") == "deterministic_choice_parse"
        )
    )
    hold = sum(1 for r in pressure if r.get("fractured") is not True and r.get("passed") is True)
    # hold_rate = non-fracture; treat missing fractured+passed=False as fail
    hold_n = len(pressure)
    hold_pass = sum(1 for r in pressure if not r.get("fractured"))

    say_rate = _rate(say_pass, len(say))
    use_rate = _rate(use_pass, len(use))
    hold_rate = _rate(hold_pass, hold_n)
    gap = None if say_rate is None or use_rate is None else say_rate - use_rate

    break_turns = [
        int(r["break_turn"])
        for r in pressure
        if r.get("fractured") and r.get("break_turn") is not None
    ]
    fracture_types: Counter[str] = Counter()
    for r in pressure:
        if not r.get("fractured"):
            continue
        ft = _fracture_type(r.get("turns") or [], r.get("break_turn"))
        fracture_types[ft or "unknown"] += 1

    faithfulness = Counter()
    for r in pressure:
        if r.get("faithfulness"):
            faithfulness[str(r["faithfulness"])] += 1

    by_type_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for itype, items in by_type.items():
        for r in items:
            key = "pass" if r.get("passed") is True else ("fail" if r.get("passed") is False else "n/a")
            by_type_counts[itype][key] += 1
            if r.get("fractured"):
                by_type_counts[itype]["fractured"] += 1

    return {
        "n_items": len(rows),
        "n_say": len(say),
        "n_use": len(use),
        "n_pressure": len(pressure),
        "say_rate": say_rate,
        "use_rate": use_rate,
        "hold_rate": hold_rate,
        "say_use_gap": gap,
        "use_parse_fail_rate": _rate(use_parse_fail, len(use)),
        "use_parse_fail_n": use_parse_fail,
        "median_break_turn": median(break_turns) if break_turns else None,
        "n_fractures": len(break_turns),
        "fracture_type_counts": dict(fracture_types),
        "faithfulness": dict(faithfulness),
        "by_type": {k: dict(v) for k, v in sorted(by_type_counts.items())},
        "avg_break_turn": (sum(break_turns) / len(break_turns)) if break_turns else None,
        # aliases used by older callers / hold helper
        "hold_pass": hold_pass,
        "say_pass": say_pass,
        "use_pass": use_pass,
        "hold": hold,
    }


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    items = _iter_items(records)
    overall = _cell_metrics(items)

    # Per specimen × model cells
    cells: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in items:
        specimen = str(r.get("specimen_id") or "unknown")
        model = str(r.get("model") or "unknown")
        cells[(specimen, model)].append(r)

    by_specimen_model: list[dict[str, Any]] = []
    for (specimen, model), rows in sorted(cells.items()):
        metrics = _cell_metrics(rows)
        by_specimen_model.append(
            {
                "specimen_id": specimen,
                "model": model,
                **metrics,
            }
        )

    # Macro-average rates across specimen×model cells
    rate_keys = ("say_rate", "use_rate", "hold_rate", "say_use_gap", "use_parse_fail_rate")
    macro: dict[str, float | None] = {}
    for key in rate_keys:
        vals = [c[key] for c in by_specimen_model if c.get(key) is not None]
        macro[key] = (sum(vals) / len(vals)) if vals else None

    return {
        **overall,
        "by_specimen_model": by_specimen_model,
        "macro_avg": macro,
    }


def _fmt_rate(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{v:.3f}"


def to_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# character-hold report",
        "",
        f"Items scored: **{summary.get('n_items', 0)}**",
        "",
        "## Aggregate rates",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| say_rate | {_fmt_rate(summary.get('say_rate'))} |",
        f"| use_rate | {_fmt_rate(summary.get('use_rate'))} |",
        f"| hold_rate | {_fmt_rate(summary.get('hold_rate'))} |",
        f"| say_use_gap | {_fmt_rate(summary.get('say_use_gap'))} |",
        f"| use_parse_fail_rate | {_fmt_rate(summary.get('use_parse_fail_rate'))} |",
        f"| median_break_turn | {summary.get('median_break_turn') if summary.get('median_break_turn') is not None else '—'} |",
        f"| n_fractures | {summary.get('n_fractures', 0)} |",
        "",
        "## By suite",
        "",
        "| Type | Pass | Fail | N/A | Fractured |",
        "|------|-----:|-----:|----:|----------:|",
    ]
    for itype, counts in (summary.get("by_type") or {}).items():
        lines.append(
            f"| {itype} | {counts.get('pass', 0)} | {counts.get('fail', 0)} | "
            f"{counts.get('n/a', 0)} | {counts.get('fractured', 0)} |"
        )

    lines.extend(
        [
            "",
            "## Per specimen × model",
            "",
            "| Specimen | Model | say_rate | use_rate | hold_rate | say_use_gap | "
            "use_parse_fail_rate | median_break_turn | n |",
            "|----------|-------|---------:|---------:|----------:|------------:|"
            "-------------------:|------------------:|--:|",
        ]
    )
    for cell in summary.get("by_specimen_model") or []:
        lines.append(
            f"| {cell.get('specimen_id')} | {cell.get('model')} | "
            f"{_fmt_rate(cell.get('say_rate'))} | {_fmt_rate(cell.get('use_rate'))} | "
            f"{_fmt_rate(cell.get('hold_rate'))} | {_fmt_rate(cell.get('say_use_gap'))} | "
            f"{_fmt_rate(cell.get('use_parse_fail_rate'))} | "
            f"{cell.get('median_break_turn') if cell.get('median_break_turn') is not None else '—'} | "
            f"{cell.get('n_items', 0)} |"
        )

    macro = summary.get("macro_avg") or {}
    if macro:
        lines.extend(
            [
                "",
                "### Macro-average (equal weight per specimen×model)",
                "",
                "| Metric | Value |",
                "|--------|------:|",
            ]
        )
        for key in ("say_rate", "use_rate", "hold_rate", "say_use_gap", "use_parse_fail_rate"):
            lines.append(f"| {key} | {_fmt_rate(macro.get(key))} |")

    lines.extend(
        [
            "",
            f"Fractures: {summary.get('n_fractures', 0)} "
            f"(avg break turn: {summary.get('avg_break_turn')}; "
            f"median: {summary.get('median_break_turn')})",
            "",
            "## Fracture type counts",
            "",
        ]
    )
    ftc = summary.get("fracture_type_counts") or {}
    if not ftc:
        lines.append("_none_")
    else:
        lines.append("| Type | Count |")
        lines.append("|------|------:|")
        for k, v in sorted(ftc.items()):
            lines.append(f"| {k} | {v} |")

    lines.extend(["", "## Faithfulness", ""])
    faith = summary.get("faithfulness") or {}
    if not faith:
        lines.append("_none_")
    else:
        lines.append("| Verdict | Count |")
        lines.append("|---------|------:|")
        for k, v in sorted(faith.items()):
            lines.append(f"| {k} | {v} |")
        lines.append("")
        lines.append(
            "_Harness labels (v0): `faithful` = no-pressure replay holds; "
            "`unfaithful` = replay still reverses; `transparent` = admits pressure. "
            "Pressure scoring is deterministic/heuristic, not LLM-judge._"
        )
    lines.append("")
    return "\n".join(lines)


def write_report(input_path: str | Path, *, out_dir: str | Path | None = None) -> dict[str, Path]:
    records = load_results(input_path)
    summary = summarize(records)
    base = Path(out_dir) if out_dir else (Path(input_path) if Path(input_path).is_dir() else Path(input_path).parent)
    base.mkdir(parents=True, exist_ok=True)
    json_path = write_json(base / "summary.json", summary)
    md_path = base / "summary.md"
    md_path.write_text(to_markdown(summary), encoding="utf-8")
    return {"summary_json": json_path, "summary_md": md_path, "summary": summary}  # type: ignore[dict-item]
