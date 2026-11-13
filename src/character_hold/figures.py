"""Publication-ready matplotlib figures for character-hold reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Headless-safe backend before pyplot import
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

# Distinctive but restrained palette (avoid purple-on-white AI-default look)
_COLORS = {
    "say": "#1B6B4A",
    "use": "#2F5D8C",
    "hold": "#A65D2F",
    "gap_pos": "#8B3A3A",
    "gap_neg": "#3A6B8B",
    "fracture": "#5C4B3A",
    "faith": "#2C5F5A",
    "grid": "#E6E2DB",
    "text": "#1A1A1A",
    "muted": "#5A5A5A",
    "bg": "#FAF8F5",
}


def _style(ax: plt.Axes) -> None:
    ax.set_facecolor(_COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#C8C2B8")
    ax.spines["bottom"].set_color("#C8C2B8")
    ax.tick_params(colors=_COLORS["muted"])
    ax.yaxis.grid(True, color=_COLORS["grid"], linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def _short_specimen(name: str) -> str:
    mapping = {
        "truth_over_agreement": "truth_over_agr.",
        "calibrated_uncertainty": "calibrated_unc.",
        "principle_under_authority": "principle_auth.",
    }
    return mapping.get(name, name[:18])


def figure_say_use_hold_bars(
    summary: dict[str, Any], out_path: Path, *, series_label: str = "MOCK pilot"
) -> Path:
    """Grouped bars: say / use / hold rates per specimen."""
    cells = summary.get("by_specimen_model") or []
    if not cells:
        cells = [
            {
                "specimen_id": "aggregate",
                "say_rate": summary.get("say_rate"),
                "use_rate": summary.get("use_rate"),
                "hold_rate": summary.get("hold_rate"),
            }
        ]

    labels = [_short_specimen(str(c.get("specimen_id") or "?")) for c in cells]
    say = [float(c.get("say_rate") or 0.0) for c in cells]
    use = [float(c.get("use_rate") or 0.0) for c in cells]
    hold = [float(c.get("hold_rate") or 0.0) for c in cells]

    x = np.arange(len(labels))
    width = 0.25
    fig, ax = plt.subplots(figsize=(8.2, 4.6), dpi=140)
    fig.patch.set_facecolor(_COLORS["bg"])
    _style(ax)
    ax.bar(x - width, say, width, label="say", color=_COLORS["say"], zorder=2)
    ax.bar(x, use, width, label="use", color=_COLORS["use"], zorder=2)
    ax.bar(x + width, hold, width, label="hold", color=_COLORS["hold"], zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Rate", color=_COLORS["text"])
    ax.set_title(
        f"Say / use / hold rates by specimen ({series_label})",
        color=_COLORS["text"],
        fontsize=12,
    )
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def figure_say_use_gap(
    summary: dict[str, Any], out_path: Path, *, series_label: str = "MOCK pilot"
) -> Path:
    """Horizontal bar chart of say−use gap per specimen."""
    cells = summary.get("by_specimen_model") or []
    if not cells:
        cells = [{"specimen_id": "aggregate", "say_use_gap": summary.get("say_use_gap")}]

    labels = [_short_specimen(str(c.get("specimen_id") or "?")) for c in cells][::-1]
    gaps = [float(c.get("say_use_gap") or 0.0) for c in cells][::-1]
    colors = [_COLORS["gap_pos"] if g >= 0 else _COLORS["gap_neg"] for g in gaps]

    fig, ax = plt.subplots(figsize=(7.5, 3.8), dpi=140)
    fig.patch.set_facecolor(_COLORS["bg"])
    _style(ax)
    y = np.arange(len(labels))
    ax.barh(y, gaps, color=colors, height=0.55, zorder=2)
    ax.axvline(0, color="#888888", linewidth=0.9)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("say_rate − use_rate", color=_COLORS["text"])
    ax.set_title(
        f"Say–use gap by specimen ({series_label})",
        color=_COLORS["text"],
        fontsize=12,
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def figure_break_turn_distribution(
    records: list[dict[str, Any]], out_path: Path, *, series_label: str = "MOCK pilot"
) -> Path:
    """Histogram of break turns among fractured pressure items."""
    turns: list[int] = []
    for r in records:
        if r.get("record_type") in {"meta", "error"}:
            continue
        if r.get("item_type") != "pressure":
            continue
        if r.get("fractured") and r.get("break_turn") is not None:
            turns.append(int(r["break_turn"]))

    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=140)
    fig.patch.set_facecolor(_COLORS["bg"])
    _style(ax)
    if turns:
        max_t = max(turns)
        bins = np.arange(0.5, max_t + 1.5, 1.0)
        ax.hist(turns, bins=bins, color=_COLORS["fracture"], edgecolor="white", zorder=2)
        med = float(np.median(turns))
        ax.axvline(med, color="#C45C26", linewidth=1.6, linestyle="--", label=f"median = {med:.1f}")
        ax.legend(frameon=False)
    else:
        ax.text(0.5, 0.5, "No fractures", ha="center", va="center", transform=ax.transAxes)
    ax.set_xlabel("Break turn (1-based)", color=_COLORS["text"])
    ax.set_ylabel("Count", color=_COLORS["text"])
    ax.set_title(
        f"Break-turn distribution ({series_label})",
        color=_COLORS["text"],
        fontsize=12,
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def figure_fracture_faithfulness(
    summary: dict[str, Any], out_path: Path, *, series_label: str = "MOCK pilot"
) -> Path:
    """Side-by-side counts: fracture types and faithfulness verdicts."""
    ftc = dict(summary.get("fracture_type_counts") or {})
    faith = dict(summary.get("faithfulness") or {})

    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.0), dpi=140)
    fig.patch.set_facecolor(_COLORS["bg"])

    for ax, data, title, color in (
        (axes[0], ftc, "Fracture type counts", _COLORS["fracture"]),
        (axes[1], faith, "Faithfulness verdicts", _COLORS["faith"]),
    ):
        _style(ax)
        if data:
            keys = sorted(data.keys())
            vals = [data[k] for k in keys]
            ax.bar(keys, vals, color=color, zorder=2)
            ax.set_ylabel("Count", color=_COLORS["text"])
            for i, v in enumerate(vals):
                ax.text(i, v + max(vals) * 0.02, str(v), ha="center", va="bottom", fontsize=9, color=_COLORS["muted"])
        else:
            ax.text(0.5, 0.5, "none", ha="center", va="center", transform=ax.transAxes)
        ax.set_title(title, color=_COLORS["text"], fontsize=11)
        ax.tick_params(axis="x", rotation=20)

    fig.suptitle(
        f"Fracture & faithfulness ({series_label})",
        color=_COLORS["text"],
        fontsize=12,
        y=1.02,
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def write_all_figures(
    summary: dict[str, Any],
    records: list[dict[str, Any]],
    figures_dir: str | Path,
    *,
    series_label: str = "MOCK pilot",
) -> dict[str, Path]:
    """Write the standard figure set; return map of name → path."""
    out = Path(figures_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "say_use_hold": figure_say_use_hold_bars(
            summary, out / "say_use_hold_bars.png", series_label=series_label
        ),
        "say_use_gap": figure_say_use_gap(
            summary, out / "say_use_gap.png", series_label=series_label
        ),
        "break_turns": figure_break_turn_distribution(
            records, out / "break_turn_distribution.png", series_label=series_label
        ),
        "fracture_faith": figure_fracture_faithfulness(
            summary, out / "fracture_faithfulness.png", series_label=series_label
        ),
    }
    return paths
