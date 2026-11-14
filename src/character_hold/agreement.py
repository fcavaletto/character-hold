"""Author annotation agreement vs heuristic and optional LLM judge."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from character_hold.annotate import cohens_kappa, confusion_matrix, observed_agreement
from character_hold.scoring.pressure import score_pressure_response
from character_hold.storage import ensure_dir, read_jsonl, write_json


IDENTITY_LABELS = ("in_character", "partial", "out")
PRINCIPLE_LABELS = ("holds", "hedges", "reverses")
COMPLIANCE_LABELS = ("holds", "partial_compliance", "full_yield")


def _load_author_rows(path: Path) -> list[dict[str, Any]]:
    if path.is_dir():
        rows: list[dict[str, Any]] = []
        for f in sorted(path.glob("*.jsonl")):
            rows.extend(read_jsonl(f))
        for f in sorted(path.glob("*.json")):
            if f.name.endswith("meta.json") or f.name.endswith("agreement.json"):
                continue
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, list):
                rows.extend(data)
            elif isinstance(data, dict) and "items" in data:
                rows.extend(data["items"])
            else:
                rows.append(data)
        return rows
    if path.suffix.lower() == ".jsonl":
        return list(read_jsonl(path))
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "annotations" in data:
        return list(data["annotations"])
    return [data]


def _pair_agreement(
    gold: list[str], pred: list[str], labels: tuple[str, ...]
) -> dict[str, Any]:
    n = len(gold)
    pairs = list(zip(gold, pred))
    kappa = cohens_kappa(pairs, labels) if n else None
    if kappa is not None and isinstance(kappa, float) and kappa != kappa:  # NaN
        kappa = None
    return {
        "n": n,
        "exact_match_rate": observed_agreement(pairs) if n else None,
        "cohens_kappa": kappa,
        "confusion": confusion_matrix(pairs, labels) if n else {},
    }


def compare_author_labels(
    *,
    author_path: str | Path,
    run_dir: str | Path | None = None,
    judge_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    author_p = Path(author_path)
    rows = _load_author_rows(author_p)
    # Keep turn-level author labels
    labels = [
        r
        for r in rows
        if r.get("record_type") in (None, "annotation", "author_annotation")
        and (r.get("assistant_text") or r.get("content") or r.get("identity"))
    ]

    heuristic_identity: list[str] = []
    heuristic_principle: list[str] = []
    heuristic_compliance: list[str] = []
    author_identity: list[str] = []
    author_principle: list[str] = []
    author_compliance: list[str] = []

    for r in labels:
        text = r.get("assistant_text") or r.get("content") or ""
        # Prefer stored heuristic snapshot if present; else rescore text.
        h = r.get("heuristic") or {}
        if not h and text:
            h = score_pressure_response(text)
        a_id = str(r.get("identity") or "")
        a_pr = str(r.get("principle") or "")
        a_comp = str(r.get("compliance_level") or "")
        if not a_comp:
            if a_pr == "reverses" or a_id == "out":
                a_comp = "full_yield"
            elif a_pr == "hedges" or a_id == "partial":
                a_comp = "partial_compliance"
            else:
                a_comp = "holds"
        h_id = str(h.get("identity") or "partial")
        h_pr = str(h.get("principle") or "holds")
        h_comp = str(h.get("compliance_level") or "")
        if not h_comp:
            if h_pr == "reverses" or h_id == "out":
                h_comp = "full_yield"
            elif h_pr == "hedges" or h_id == "partial":
                h_comp = "partial_compliance"
            else:
                h_comp = "holds"
        if a_id and h_id:
            author_identity.append(a_id)
            heuristic_identity.append(h_id)
        if a_pr and h_pr:
            author_principle.append(a_pr)
            heuristic_principle.append(h_pr)
        author_compliance.append(a_comp)
        heuristic_compliance.append(h_comp)

    agreement: dict[str, Any] = {
        "annotator": "author",
        "note": "Author annotation — not independent blind multi-rater psychometrics.",
        "heuristic_vs_author": {
            "identity": _pair_agreement(
                author_identity, heuristic_identity, IDENTITY_LABELS
            ),
            "principle": _pair_agreement(
                author_principle, heuristic_principle, PRINCIPLE_LABELS
            ),
            "compliance_level": _pair_agreement(
                author_compliance, heuristic_compliance, COMPLIANCE_LABELS
            ),
        },
        "label_counts_author": {
            "identity": dict(Counter(author_identity)),
            "principle": dict(Counter(author_principle)),
            "compliance_level": dict(Counter(author_compliance)),
        },
    }

    # Optional judge comparison if dual_annotation JSONL present
    if judge_dir is not None:
        jd = Path(judge_dir)
        judge_rows = []
        for name in ("annotations.jsonl", "judge.jsonl", "dual.jsonl"):
            cand = jd / name
            if cand.exists():
                judge_rows = list(read_jsonl(cand))
                break
        if not judge_rows:
            for f in sorted(jd.glob("*.jsonl")):
                judge_rows.extend(read_jsonl(f))
        # Match by item_id + turn when possible
        by_key = {
            (str(r.get("item_id")), int(r.get("turn") or 0)): r
            for r in judge_rows
            if r.get("item_id")
        }
        j_id: list[str] = []
        a_id2: list[str] = []
        j_pr: list[str] = []
        a_pr2: list[str] = []
        for r in labels:
            key = (str(r.get("item_id")), int(r.get("turn") or 0))
            jr = by_key.get(key) or by_key.get((str(r.get("item_id")), 0))
            if not jr:
                continue
            sec = jr.get("secondary") or jr.get("judge") or jr
            if r.get("identity") and sec.get("identity"):
                a_id2.append(str(r["identity"]))
                j_id.append(str(sec["identity"]))
            if r.get("principle") and sec.get("principle"):
                a_pr2.append(str(r["principle"]))
                j_pr.append(str(sec["principle"]))
        agreement["judge_vs_author"] = {
            "identity": _pair_agreement(a_id2, j_id, IDENTITY_LABELS),
            "principle": _pair_agreement(a_pr2, j_pr, PRINCIPLE_LABELS),
        }

    out_dir = Path(output_dir) if output_dir else (
        author_p if author_p.is_dir() else author_p.parent
    )
    ensure_dir(out_dir)
    write_json(out_dir / "agreement.json", agreement)

    # Markdown summary
    lines = [
        "# Author annotation agreement",
        "",
        "> Labels are **author annotation** (not independent blind raters).",
        "",
        "## Heuristic ↔ author",
        "",
    ]
    hv = agreement["heuristic_vs_author"]
    for dim, blob in hv.items():
        lines.append(
            f"- **{dim}**: match={blob.get('exact_match_rate')} κ={blob.get('cohens_kappa')} "
            f"n={blob.get('n')}"
        )
        conf = blob.get("confusion") or {}
        if conf:
            lines.append("")
            lines.append(f"### Confusion ({dim})")
            lines.append("")
            lines.append("```")
            lines.append(json.dumps(conf, indent=2))
            lines.append("```")
    if "judge_vs_author" in agreement:
        lines.extend(["", "## Judge ↔ author", ""])
        for dim, blob in agreement["judge_vs_author"].items():
            lines.append(
                f"- **{dim}**: match={blob.get('exact_match_rate')} κ={blob.get('cohens_kappa')} "
                f"n={blob.get('n')}"
            )
    (out_dir / "agreement.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Touch run_dir only to document linkage
    _ = run_dir
    return {"output_dir": str(out_dir), "agreement": {
        "identity": hv["identity"],
        "principle": hv["principle"],
        "compliance_level": hv["compliance_level"],
        **(
            {f"judge_{k}": v for k, v in agreement.get("judge_vs_author", {}).items()}
            if "judge_vs_author" in agreement
            else {}
        ),
    }}
