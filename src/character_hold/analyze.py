"""Summary tables, markdown/HTML reports, and figures from scored run results."""

from __future__ import annotations

import html
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

from character_hold.storage import read_jsonl, write_json

# Faithfulness label semantics (harness v0) — keep in sync with methodology §12 / README.
FAITHFULNESS_LABELS = {
    "faithful": "no-pressure replay holds (prior reverse looks pressure-driven)",
    "unfaithful": "replay still reverses without admitting pressure",
    "transparent": "replay admits pressure influence",
}


def load_results(input_path: str | Path) -> list[dict[str, Any]]:
    p = Path(input_path)
    if p.is_dir():
        for name in ("scored.jsonl", "raw.jsonl"):
            candidate = p / name
            if candidate.exists():
                return list(read_jsonl(candidate))
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
        "hold_pass": hold_pass,
        "say_pass": say_pass,
        "use_pass": use_pass,
        "hold": hold,
    }


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    items = _iter_items(records)
    overall = _cell_metrics(items)

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


def _faithfulness_footnote() -> str:
    bits = "; ".join(f"`{k}` = {v}" for k, v in FAITHFULNESS_LABELS.items())
    return (
        "_Harness labels (v0): "
        + bits
        + ". Pressure scoring is deterministic/heuristic, not LLM-judge._"
    )


def to_markdown(summary: dict[str, Any], *, figure_rels: dict[str, str] | None = None) -> str:
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

    if figure_rels:
        lines.extend(["", "## Figures", ""])
        captions = {
            "say_use_hold": "Say / use / hold rates by specimen",
            "say_use_gap": "Say–use gap by specimen",
            "break_turns": "Break-turn distribution",
            "fracture_faith": "Fracture type and faithfulness counts",
        }
        for key, rel in figure_rels.items():
            caption = captions.get(key, key)
            lines.append(f"### {caption}")
            lines.append("")
            lines.append(f"![{caption}]({rel})")
            lines.append("")

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
        lines.append(_faithfulness_footnote())
    lines.append("")
    return "\n".join(lines)


def to_html(
    summary: dict[str, Any],
    *,
    figure_rels: dict[str, str] | None = None,
    title: str = "character-hold pilot report",
    banner: str = "MOCK PROVIDER — illustrative pipeline dry-run, not live-model evidence",
) -> str:
    """Self-contained static HTML (no JS framework) suitable for demos."""

    def esc(x: Any) -> str:
        return html.escape("" if x is None else str(x))

    def rate_cell(v: float | None) -> str:
        return esc(_fmt_rate(v))

    rows_agg = [
        ("say_rate", summary.get("say_rate")),
        ("use_rate", summary.get("use_rate")),
        ("hold_rate", summary.get("hold_rate")),
        ("say_use_gap", summary.get("say_use_gap")),
        ("use_parse_fail_rate", summary.get("use_parse_fail_rate")),
        ("median_break_turn", summary.get("median_break_turn")),
        ("n_fractures", summary.get("n_fractures")),
        ("n_items", summary.get("n_items")),
    ]
    agg_html = "".join(
        f"<tr><td>{esc(k)}</td><td class='num'>{rate_cell(v) if isinstance(v, float) else esc(v)}</td></tr>"
        for k, v in rows_agg
    )

    cell_rows = ""
    for cell in summary.get("by_specimen_model") or []:
        cell_rows += (
            "<tr>"
            f"<td>{esc(cell.get('specimen_id'))}</td>"
            f"<td>{esc(cell.get('model'))}</td>"
            f"<td class='num'>{rate_cell(cell.get('say_rate'))}</td>"
            f"<td class='num'>{rate_cell(cell.get('use_rate'))}</td>"
            f"<td class='num'>{rate_cell(cell.get('hold_rate'))}</td>"
            f"<td class='num'>{rate_cell(cell.get('say_use_gap'))}</td>"
            f"<td class='num'>{esc(cell.get('median_break_turn') if cell.get('median_break_turn') is not None else '—')}</td>"
            f"<td class='num'>{esc(cell.get('n_items'))}</td>"
            "</tr>"
        )

    def count_table(data: dict[str, Any]) -> str:
        if not data:
            return "<p class='muted'>none</p>"
        body = "".join(
            f"<tr><td>{esc(k)}</td><td class='num'>{esc(v)}</td></tr>" for k, v in sorted(data.items())
        )
        return f"<table><thead><tr><th>Label</th><th>Count</th></tr></thead><tbody>{body}</tbody></table>"

    figs = ""
    if figure_rels:
        captions = {
            "say_use_hold": "Say / use / hold rates by specimen",
            "say_use_gap": "Say–use gap by specimen",
            "break_turns": "Break-turn distribution",
            "fracture_faith": "Fracture type and faithfulness counts",
        }
        blocks = []
        for key, rel in figure_rels.items():
            cap = captions.get(key, key)
            blocks.append(
                f"<figure><img src='{esc(rel)}' alt='{esc(cap)}'/><figcaption>{esc(cap)}</figcaption></figure>"
            )
        figs = "<section><h2>Figures</h2>" + "".join(blocks) + "</section>"

    faith_note = esc(
        "Harness labels (v0): "
        + "; ".join(f"{k} = {v}" for k, v in FAITHFULNESS_LABELS.items())
        + "."
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{esc(title)}</title>
<style>
  :root {{
    --bg: #f7f4ef;
    --ink: #1c1a17;
    --muted: #5c574f;
    --card: #fffdf9;
    --line: #ddd6c8;
    --accent: #1b6b4a;
    --warn: #8b3a3a;
    --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
    --sans: "IBM Plex Sans", "Source Sans 3", "Segoe UI", sans-serif;
    --mono: "IBM Plex Mono", "SFMono-Regular", Consolas, monospace;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background:
      radial-gradient(1200px 500px at 10% -10%, #e7efe8 0%, transparent 55%),
      radial-gradient(900px 400px at 100% 0%, #efe6d8 0%, transparent 50%),
      var(--bg);
    color: var(--ink);
    font-family: var(--sans);
    line-height: 1.5;
  }}
  header {{
    padding: 2.25rem 1.5rem 1.25rem;
    max-width: 960px;
    margin: 0 auto;
  }}
  .banner {{
    display: inline-block;
    background: #f3e4dc;
    color: var(--warn);
    border: 1px solid #e2c4b4;
    padding: 0.35rem 0.7rem;
    font-size: 0.78rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-family: var(--mono);
    margin-bottom: 1rem;
  }}
  h1 {{
    font-family: var(--serif);
    font-weight: 600;
    font-size: clamp(1.8rem, 3vw, 2.4rem);
    margin: 0 0 0.4rem;
    letter-spacing: -0.02em;
  }}
  .lede {{
    color: var(--muted);
    max-width: 42rem;
    margin: 0;
  }}
  main {{
    max-width: 960px;
    margin: 0 auto;
    padding: 0 1.5rem 3rem;
  }}
  section {{
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 1.25rem 1.35rem;
    margin: 1rem 0;
  }}
  h2 {{
    font-family: var(--serif);
    font-size: 1.25rem;
    margin: 0 0 0.85rem;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.92rem;
  }}
  th, td {{
    border-bottom: 1px solid var(--line);
    padding: 0.45rem 0.4rem;
    text-align: left;
  }}
  th {{ color: var(--muted); font-weight: 600; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.03em; }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; font-family: var(--mono); }}
  figure {{ margin: 1rem 0 1.4rem; }}
  figure img {{ width: 100%; height: auto; border: 1px solid var(--line); border-radius: 6px; background: #faf8f5; }}
  figcaption {{ color: var(--muted); font-size: 0.85rem; margin-top: 0.4rem; }}
  .muted {{ color: var(--muted); font-size: 0.9rem; }}
  footer {{
    max-width: 960px;
    margin: 0 auto;
    padding: 0 1.5rem 2.5rem;
    color: var(--muted);
    font-size: 0.85rem;
  }}
  a {{ color: var(--accent); }}
</style>
</head>
<body>
  <header>
    <div class="banner">{esc(banner)}</div>
    <h1>{esc(title)}</h1>
    <p class="lede">Behavioral dissociation of saying, using, and holding declared assistant character under pressure. Numbers below are from a deterministic mock provider.</p>
  </header>
  <main>
    <section>
      <h2>Aggregate rates</h2>
      <table><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>{agg_html}</tbody></table>
    </section>
    <section>
      <h2>Per specimen × model</h2>
      <table>
        <thead>
          <tr>
            <th>Specimen</th><th>Model</th><th>say</th><th>use</th><th>hold</th>
            <th>gap</th><th>med. break</th><th>n</th>
          </tr>
        </thead>
        <tbody>{cell_rows}</tbody>
      </table>
    </section>
    {figs}
    <section>
      <h2>Fracture types</h2>
      {count_table(summary.get("fracture_type_counts") or {})}
    </section>
    <section>
      <h2>Faithfulness</h2>
      {count_table(summary.get("faithfulness") or {})}
      <p class="muted">{faith_note}</p>
    </section>
  </main>
  <footer>
    Generated by <code>character-hold report</code>. See <code>docs/methodology.md</code> and <code>docs/pilot_protocol.md</code>.
  </footer>
</body>
</html>
"""


def write_index_md(
    summary: dict[str, Any],
    *,
    base: Path,
    figure_rels: dict[str, str] | None = None,
) -> Path:
    """One-page results landing for a run directory."""
    lines = [
        "# Pilot results index",
        "",
        "> **MOCK dry-run.** Deterministic mock provider; not live-model evidence.",
        "",
        "## Headline metrics",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| say_rate | {_fmt_rate(summary.get('say_rate'))} |",
        f"| use_rate | {_fmt_rate(summary.get('use_rate'))} |",
        f"| hold_rate | {_fmt_rate(summary.get('hold_rate'))} |",
        f"| say_use_gap | {_fmt_rate(summary.get('say_use_gap'))} |",
        f"| median_break_turn | {summary.get('median_break_turn') if summary.get('median_break_turn') is not None else '—'} |",
        f"| n_items | {summary.get('n_items', 0)} |",
        "",
        "## Artifacts",
        "",
        "- [Interactive HTML report](report.html)",
        "- [Full markdown report](report.md)",
        "- [Compact summary](summary.md) · [summary.json](summary.json)",
        "- [Scored JSONL](scored.jsonl) · [Raw JSONL](raw.jsonl)",
        "- [Run manifest](run_manifest.json) · [Spot-check notes](notes.md)",
        "",
    ]
    if figure_rels:
        lines.append("## Figures")
        lines.append("")
        for key, rel in figure_rels.items():
            lines.append(f"- [{key}]({rel})")
        lines.append("")
    path = base / "INDEX.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_report(
    input_path: str | Path,
    *,
    out_dir: str | Path | None = None,
    write_figures: bool = True,
    write_html: bool = True,
) -> dict[str, Any]:
    records = load_results(input_path)
    summary = summarize(records)
    base = Path(out_dir) if out_dir else (Path(input_path) if Path(input_path).is_dir() else Path(input_path).parent)
    base.mkdir(parents=True, exist_ok=True)

    figure_paths: dict[str, Path] = {}
    figure_rels: dict[str, str] = {}
    if write_figures:
        from character_hold.figures import write_all_figures

        figure_paths = write_all_figures(summary, records, base / "figures")
        figure_rels = {k: f"figures/{p.name}" for k, p in figure_paths.items()}

    json_path = write_json(base / "summary.json", summary)
    summary_md = base / "summary.md"
    summary_md.write_text(to_markdown(summary), encoding="utf-8")

    report_md = base / "report.md"
    report_md.write_text(to_markdown(summary, figure_rels=figure_rels), encoding="utf-8")

    html_path: Path | None = None
    if write_html:
        html_path = base / "report.html"
        html_path.write_text(
            to_html(summary, figure_rels=figure_rels),
            encoding="utf-8",
        )

    index_path = write_index_md(summary, base=base, figure_rels=figure_rels)

    out: dict[str, Any] = {
        "summary_json": json_path,
        "summary_md": summary_md,
        "report_md": report_md,
        "index_md": index_path,
        "summary": summary,
        "figures": figure_paths,
    }
    if html_path is not None:
        out["report_html"] = html_path
    return out
