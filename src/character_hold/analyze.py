"""Summary tables from scored run results."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
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


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_type: dict[str, Counter[str]] = defaultdict(Counter)
    fracture_breaks: list[int] = []
    faithfulness = Counter()
    n = 0
    for r in records:
        if r.get("record_type") == "meta":
            continue
        n += 1
        itype = r.get("item_type") or r.get("type") or "unknown"
        passed = r.get("passed")
        key = "pass" if passed is True else ("fail" if passed is False else "n/a")
        by_type[itype][key] += 1
        if r.get("fractured"):
            by_type[itype]["fractured"] += 1
            if r.get("break_turn") is not None:
                fracture_breaks.append(int(r["break_turn"]))
        if r.get("faithfulness"):
            faithfulness[str(r["faithfulness"])] += 1

    avg_break = sum(fracture_breaks) / len(fracture_breaks) if fracture_breaks else None
    return {
        "n_items": n,
        "by_type": {k: dict(v) for k, v in sorted(by_type.items())},
        "faithfulness": dict(faithfulness),
        "avg_break_turn": avg_break,
        "n_fractures": len(fracture_breaks),
    }


def to_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# character-hold report",
        "",
        f"Items scored: **{summary.get('n_items', 0)}**",
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
            f"Fractures: {summary.get('n_fractures', 0)} "
            f"(avg break turn: {summary.get('avg_break_turn')})",
            "",
            "## Faithfulness",
            "",
        ]
    )
    faith = summary.get("faithfulness") or {}
    if not faith:
        lines.append("_none_")
    else:
        lines.append("| Verdict | Count |")
        lines.append("|---------|------:|")
        for k, v in sorted(faith.items()):
            lines.append(f"| {k} | {v} |")
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
