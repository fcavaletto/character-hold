"""Load config/specimens/scenarios, execute suites, store raw JSONL, score."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from pydantic import TypeAdapter

from character_hold.analyze import write_report
from character_hold.faithfulness import run_faithfulness_check
from character_hold.fracture import detect_break
from character_hold.providers import get_provider
from character_hold.providers.base import ChatMessage, Provider
from character_hold.schema import (
    FaithfulnessVerdict,
    FractureOn,
    IdentityScore,
    ItemResult,
    PressureItem,
    PrincipleScore,
    RunConfig,
    SayItem,
    ScenarioItem,
    Specimen,
    TurnRecord,
    UseItem,
)
from character_hold.scoring.pressure import score_pressure_response
from character_hold.scoring.say import score_say
from character_hold.scoring.use import score_use
from character_hold.storage import append_jsonl, ensure_dir, read_jsonl, write_json, write_jsonl

_scenario_adapter = TypeAdapter(ScenarioItem)


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_config(path: str | Path) -> RunConfig:
    data = load_yaml(Path(path)) or {}
    return RunConfig.model_validate(data)


def load_specimens(directory: str | Path, specimen_ids: list[str] | None = None) -> dict[str, Specimen]:
    root = Path(directory)
    if not root.exists():
        return {}
    out: dict[str, Specimen] = {}
    for path in sorted(root.glob("**/*")):
        if path.suffix.lower() not in {".yaml", ".yml", ".json"}:
            continue
        raw = load_yaml(path) if path.suffix.lower() in {".yaml", ".yml"} else json.loads(path.read_text())
        if isinstance(raw, list):
            items = raw
        elif isinstance(raw, dict) and "specimens" in raw:
            items = raw["specimens"]
        else:
            items = [raw]
        for item in items:
            sp = Specimen.model_validate(item)
            out[sp.id] = sp
    if specimen_ids:
        missing = [i for i in specimen_ids if i not in out]
        if missing:
            raise ValueError(f"Specimen ids not found: {missing}")
        out = {i: out[i] for i in specimen_ids}
    return out


def load_scenarios(directory: str | Path, suites: list[str] | None = None) -> list[ScenarioItem]:
    root = Path(directory)
    if not root.exists():
        return []
    items: list[ScenarioItem] = []
    for path in sorted(root.glob("**/*")):
        if path.suffix.lower() not in {".yaml", ".yml", ".json"}:
            continue
        raw = load_yaml(path) if path.suffix.lower() in {".yaml", ".yml"} else json.loads(path.read_text())
        if raw is None:
            continue
        if isinstance(raw, dict) and "items" in raw:
            blob = raw["items"]
        elif isinstance(raw, list):
            blob = raw
        else:
            blob = [raw]
        for entry in blob:
            items.append(_scenario_adapter.validate_python(entry))
    if suites:
        allowed = set(suites)
        items = [i for i in items if i.type in allowed]
    return items


def validate_paths(config: RunConfig) -> dict[str, Any]:
    specimens = load_specimens(config.specimens_dir, config.specimen_ids)
    scenarios = load_scenarios(config.scenarios_dir, config.suites)
    errors: list[str] = []
    if not specimens:
        errors.append(f"No specimens found under {config.specimens_dir}")
    if not scenarios:
        errors.append(f"No scenarios found under {config.scenarios_dir}")
    orphan = [i.id for i in scenarios if i.specimen_id not in specimens]
    if orphan:
        errors.append(f"Scenario items reference missing specimens: {orphan[:20]}")

    # Cross-check: unique ids, use prompts require CHOICE cue, pressure turns present
    seen_ids: set[str] = set()
    by_type: dict[str, int] = {"say": 0, "use": 0, "pressure": 0}
    by_specimen: dict[str, dict[str, int]] = {}
    for item in scenarios:
        if item.id in seen_ids:
            errors.append(f"Duplicate scenario id: {item.id}")
        seen_ids.add(item.id)
        by_type[item.type] = by_type.get(item.type, 0) + 1
        cell = by_specimen.setdefault(item.specimen_id, {"say": 0, "use": 0, "pressure": 0})
        cell[item.type] = cell.get(item.type, 0) + 1
        if isinstance(item, UseItem):
            blob = f"{item.prompt}\n{item.choice_a_summary}\n{item.choice_b_summary}".upper()
            if "CHOICE" not in blob and "OPTION A" not in blob:
                errors.append(f"Use item missing CHOICE/option cue: {item.id}")
        if isinstance(item, PressureItem):
            if not item.adversary_turns:
                errors.append(f"Pressure item has no adversary turns: {item.id}")
            if item.max_turns < 1:
                errors.append(f"Pressure item max_turns < 1: {item.id}")
        if isinstance(item, SayItem) and not item.pass_patterns:
            errors.append(f"Say item missing pass_patterns: {item.id}")

    return {
        "ok": not errors,
        "errors": errors,
        "n_specimens": len(specimens),
        "n_scenarios": len(scenarios),
        "by_type": by_type,
        "by_specimen": by_specimen,
        "specimen_ids": sorted(specimens.keys()),
        "item_ids": [i.id for i in scenarios],
    }


def score_item_record(record: dict[str, Any], item: ScenarioItem | None = None) -> dict[str, Any]:
    """Offline-capable scoring from a raw/partial record + optional item schema."""
    itype = record.get("item_type") or (item.type if item else None)
    out = dict(record)
    if itype == "say" and item and isinstance(item, SayItem):
        detail = score_say(item, record.get("raw_response") or "")
        out["passed"] = detail["passed"]
        out["score_detail"] = detail
    elif itype == "use" and item and isinstance(item, UseItem):
        detail = score_use(item, record.get("raw_response") or "")
        out["passed"] = detail["passed"]
        out["score_detail"] = detail
    elif itype == "pressure":
        # Recompute heuristics from stored assistant text when present, then break turn.
        turns_data = record.get("turns") or []
        fracture_on = (
            record.get("fracture_on")
            or (record.get("score_detail") or {}).get("fracture_on")
            or ["out", "reverses"]
        )
        turns: list[TurnRecord] = []
        for t in turns_data:
            if isinstance(t, TurnRecord):
                base = t
            else:
                base = TurnRecord.model_validate(t)
            detail = score_pressure_response(base.content or "")
            turns.append(
                TurnRecord(
                    turn=base.turn,
                    role=base.role,
                    content=base.content,
                    identity=IdentityScore(detail["identity"]),
                    principle=PrincipleScore(detail["principle"]),
                )
            )
        fractured, break_turn = detect_break(turns, fracture_on)
        out["turns"] = [t.model_dump() for t in turns]
        out["fractured"] = fractured
        out["break_turn"] = break_turn
        out["passed"] = not fractured
        last_detail = (
            score_pressure_response(turns[-1].content or "") if turns else {}
        )
        out["score_detail"] = {
            "fracture_on": [getattr(f, "value", f) for f in fracture_on],
            "last_turn_detail": last_detail or None,
            "method": "deterministic_fracture",
            "fractured": fractured,
            "break_turn": break_turn,
        }
        break_principle = None
        if fractured and break_turn is not None:
            for tr in turns:
                if tr.turn == break_turn and tr.principle is not None:
                    break_principle = tr.principle.value
                    break
        # Drop a stored faithfulness verdict when the rescored break is not a reverse.
        if not fractured or break_principle != PrincipleScore.REVERSES.value:
            out["faithfulness"] = None
    return out


def _run_say(
    item: SayItem,
    specimen: Specimen,
    provider: Provider,
    config: RunConfig,
) -> ItemResult:
    messages = [ChatMessage(role="user", content=item.prompt)]
    completion = provider.complete(
        messages,
        system=specimen.system_prompt,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )
    detail = score_say(item, completion.text)
    return ItemResult(
        item_id=item.id,
        item_type="say",
        specimen_id=item.specimen_id,
        passed=detail["passed"],
        score_detail=detail,
        raw_response=completion.text,
        model=provider.model,
        provider=provider.name,
    )


def _run_use(
    item: UseItem,
    specimen: Specimen,
    provider: Provider,
    config: RunConfig,
) -> ItemResult:
    prompt = (
        f"{item.prompt}\n\n"
        f"Option A: {item.choice_a_summary}\n"
        f"Option B: {item.choice_b_summary}\n"
        "Answer with exactly one line: CHOICE: A or CHOICE: B."
    )
    messages = [ChatMessage(role="user", content=prompt)]
    completion = provider.complete(
        messages,
        system=specimen.system_prompt,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )
    detail = score_use(item, completion.text)
    return ItemResult(
        item_id=item.id,
        item_type="use",
        specimen_id=item.specimen_id,
        passed=detail["passed"],
        score_detail=detail,
        raw_response=completion.text,
        model=provider.model,
        provider=provider.name,
    )


def _run_pressure(
    item: PressureItem,
    specimen: Specimen,
    provider: Provider,
    config: RunConfig,
) -> ItemResult:
    fracture_on = item.fracture_on or list(config.fracture_on)
    messages: list[ChatMessage] = []
    turns: list[TurnRecord] = []
    last_assistant = ""
    last_user = ""

    for adv in item.adversary_turns:
        if adv.turn > item.max_turns:
            break
        messages.append(ChatMessage(role="user", content=adv.content))
        last_user = adv.content
        completion = provider.complete(
            messages,
            system=specimen.system_prompt,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
        messages.append(ChatMessage(role="assistant", content=completion.text))
        last_assistant = completion.text
        detail = score_pressure_response(completion.text, principles=specimen.principles)
        identity = IdentityScore(detail["identity"])
        principle = PrincipleScore(detail["principle"])
        turns.append(
            TurnRecord(
                turn=adv.turn,
                role="assistant",
                content=completion.text,
                identity=identity,
                principle=principle,
            )
        )
        fractured_now, break_turn = detect_break(turns, fracture_on)
        if fractured_now:
            faithfulness: FaithfulnessVerdict | None = None
            faith_replay = None
            if config.run_faithfulness and principle == PrincipleScore.REVERSES:
                faithfulness, faith_replay = run_faithfulness_check(
                    provider,
                    system_prompt=specimen.system_prompt,
                    pressure_user_content=last_user,
                    original_response=last_assistant,
                )
            return ItemResult(
                item_id=item.id,
                item_type="pressure",
                specimen_id=item.specimen_id,
                passed=False,
                score_detail={
                    "fracture_on": [f.value for f in fracture_on],
                    "last_turn_detail": detail,
                    "faithfulness_replay": faith_replay,
                    "method": "deterministic_fracture",
                },
                raw_response=last_assistant,
                turns=turns,
                break_turn=break_turn,
                fractured=True,
                faithfulness=faithfulness,
                model=provider.model,
                provider=provider.name,
            )

    fractured, break_turn = detect_break(turns, fracture_on)
    return ItemResult(
        item_id=item.id,
        item_type="pressure",
        specimen_id=item.specimen_id,
        passed=not fractured,
        score_detail={
            "fracture_on": [f.value for f in fracture_on],
            "method": "deterministic_fracture",
        },
        raw_response=last_assistant or None,
        turns=turns,
        break_turn=break_turn,
        fractured=fractured,
        model=provider.model,
        provider=provider.name,
    )


def _empty_usage() -> dict[str, float | int]:
    return {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "reasoning_tokens": 0,
        "cost_usd": 0.0,
        "n_calls": 0,
        "n_length_truncated": 0,
    }


def _usage_snapshot(provider: Provider) -> dict[str, float | int]:
    totals = getattr(provider, "usage_totals", None)
    base = _empty_usage()
    if not isinstance(totals, dict):
        return base
    for key in base:
        if key in totals and totals[key] is not None:
            base[key] = totals[key]
    return base


def _usage_delta(
    before: dict[str, float | int], after: dict[str, float | int]
) -> dict[str, float | int]:
    delta = _empty_usage()
    for key in delta:
        b = before.get(key) or 0
        a = after.get(key) or 0
        if key == "cost_usd":
            delta[key] = float(a) - float(b)
        else:
            delta[key] = int(a) - int(b)
    return delta


def _sum_item_usage(records: list[dict[str, Any]]) -> dict[str, float | int]:
    total = _empty_usage()
    for rec in records:
        usage = rec.get("usage") or {}
        if not isinstance(usage, dict):
            continue
        for key in total:
            val = usage.get(key)
            if val is None:
                continue
            if key == "cost_usd":
                total[key] = float(total[key]) + float(val)
            else:
                total[key] = int(total[key]) + int(val)
    return total


def run_evaluation(
    config: RunConfig,
    *,
    provider_override: str | None = None,
    model_override: str | None = None,
    project_root: str | Path | None = None,
    run_id_override: str | None = None,
    resume: bool = False,
) -> Path:
    root = Path(project_root) if project_root else Path.cwd()
    specimens_dir = (root / config.specimens_dir).resolve() if not Path(config.specimens_dir).is_absolute() else Path(config.specimens_dir)
    scenarios_dir = (root / config.scenarios_dir).resolve() if not Path(config.scenarios_dir).is_absolute() else Path(config.scenarios_dir)
    results_dir = (root / config.results_dir).resolve() if not Path(config.results_dir).is_absolute() else Path(config.results_dir)

    # Fallback to test fixtures when project dirs are empty/missing
    specimens = load_specimens(specimens_dir, config.specimen_ids)
    scenarios = load_scenarios(scenarios_dir, config.suites)
    if not specimens or not scenarios:
        fixtures = root / "tests" / "fixtures"
        if not specimens:
            specimens = load_specimens(fixtures / "specimens", config.specimen_ids)
        if not scenarios:
            scenarios = load_scenarios(fixtures / "scenarios", config.suites)

    if not specimens:
        raise FileNotFoundError(
            f"No specimens in {specimens_dir} (and no fixtures fallback). "
            "Agent C owns specimens/; tests use tests/fixtures/specimens/."
        )
    if not scenarios:
        raise FileNotFoundError(
            f"No scenarios in {scenarios_dir} (and no fixtures fallback). "
            "Agent C owns scenarios/; tests use tests/fixtures/scenarios/."
        )

    provider_name = provider_override or config.provider
    model = model_override or config.model
    provider = get_provider(
        provider_name,
        model=model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        seed=config.seed,
    )

    # Mock runs use a fixed stamp so `make demo` keeps committed artifacts clean.
    if str(provider_name).lower() == "mock":
        stamp = f"MOCKSEED{int(config.seed) if config.seed is not None else 0:04d}T000000Z"
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = run_id_override or config.run_id
    if run_id:
        run_dir = ensure_dir(results_dir / run_id)
    else:
        run_dir = ensure_dir(results_dir / f"run_{stamp}_{provider.name}")
    raw_path = run_dir / "raw.jsonl"

    done_ids: set[str] = set()
    if resume and raw_path.exists():
        prior = list(read_jsonl(raw_path))
        metas = [r for r in prior if r.get("record_type") == "meta" and r.get("model")]
        if metas:
            prior_model = metas[0].get("model")
            prior_provider = metas[0].get("provider")
            if prior_model != provider.model or prior_provider != provider.name:
                raise RuntimeError(
                    f"Refusing to resume {raw_path}: existing run is "
                    f"{prior_provider}/{prior_model}, requested {provider.name}/{provider.model}."
                )
        done_ids = {
            str(r["item_id"])
            for r in prior
            if r.get("record_type") == "item" and r.get("item_id")
        }
        append_jsonl(
            raw_path,
            {
                "record_type": "meta",
                "resumed_at": stamp,
                "run_id": run_id,
                "provider": provider.name,
                "model": provider.model,
                "n_already_complete": len(done_ids),
            },
        )
    else:
        if run_id:
            # Stable pilot dirs are overwritten so artifacts stay under a known path.
            # Resume keeps raw.jsonl and skips completed item ids.
            for name in (
                "raw.jsonl",
                "scored.jsonl",
                "summary.json",
                "summary.md",
                "report.md",
                "report.html",
                "INDEX.md",
                "run_manifest.json",
                "usage.json",
            ):
                stale = run_dir / name
                if stale.exists():
                    stale.unlink()
            figures_dir = run_dir / "figures"
            if figures_dir.is_dir():
                for png in figures_dir.glob("*.png"):
                    png.unlink()
        meta = {
            "record_type": "meta",
            "started_at": stamp,
            "run_id": run_id,
            "provider": provider.name,
            "model": provider.model,
            "config": config.model_dump(mode="json"),
            "n_specimens": len(specimens),
            "n_items": len(scenarios),
            "extra_body": getattr(provider, "extra_body", None),
        }
        append_jsonl(raw_path, meta)

    n_total = len(scenarios)
    for index, item in enumerate(scenarios, start=1):
        if item.id in done_ids:
            print(
                f"[character-hold] {index}/{n_total} skip {item.id}",
                file=sys.stderr,
                flush=True,
            )
            continue
        specimen = specimens.get(item.specimen_id)
        if specimen is None:
            append_jsonl(
                raw_path,
                {
                    "record_type": "error",
                    "item_id": item.id,
                    "error": f"missing specimen {item.specimen_id}",
                },
            )
            continue
        before_usage = _usage_snapshot(provider)
        if isinstance(item, SayItem):
            result = _run_say(item, specimen, provider, config)
        elif isinstance(item, UseItem):
            result = _run_use(item, specimen, provider, config)
        elif isinstance(item, PressureItem):
            result = _run_pressure(item, specimen, provider, config)
        else:
            continue
        rec = result.model_dump(mode="json")
        rec["record_type"] = "item"
        delta = _usage_delta(before_usage, _usage_snapshot(provider))
        if int(delta.get("n_calls") or 0) > 0:
            rec["usage"] = delta
        append_jsonl(raw_path, rec)
        print(
            f"[character-hold] {index}/{n_total} {item.type} {item.id} passed={result.passed}",
            file=sys.stderr,
            flush=True,
        )

    raw_records = list(read_jsonl(raw_path))
    scored_rows = [r for r in raw_records if r.get("record_type") == "item"]
    # One row per item id (resume can only append; keep the latest copy).
    latest: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for row in scored_rows:
        iid = str(row.get("item_id"))
        if iid not in latest:
            order.append(iid)
        latest[iid] = row
    scored_rows = [latest[i] for i in order]
    scored_path = run_dir / "scored.jsonl"
    write_jsonl(scored_path, scored_rows)
    usage = _sum_item_usage(scored_rows)
    if int(usage.get("n_calls") or 0) > 0:
        write_json(run_dir / "usage.json", usage)
    write_report(run_dir, out_dir=run_dir)
    write_json(
        run_dir / "run_manifest.json",
        {
            "raw": str(raw_path),
            "scored": str(scored_path),
            "provider": provider.name,
            "model": provider.model,
            "upstream_model": getattr(provider, "upstream_model", None),
            "n_results": len(scored_rows),
            "seed": config.seed,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "extra_body": getattr(provider, "extra_body", None),
            "mock": provider.name == "mock",
            "resumed": bool(resume and done_ids),
            "usage": usage if int(usage.get("n_calls") or 0) > 0 else None,
        },
    )
    return run_dir


def rescore_run(input_path: str | Path, scenarios_dir: str | Path | None = None) -> Path:
    """Re-score from raw JSONL offline (deterministic)."""
    p = Path(input_path)
    run_dir = p if p.is_dir() else p.parent
    raw_file = run_dir / "raw.jsonl" if p.is_dir() else p
    items_by_id: dict[str, ScenarioItem] = {}
    if scenarios_dir:
        for it in load_scenarios(scenarios_dir):
            items_by_id[it.id] = it

    scored: list[dict[str, Any]] = []
    for rec in read_jsonl(raw_file):
        if rec.get("record_type") in {"meta", "error"}:
            continue
        item = items_by_id.get(rec.get("item_id", ""))
        # For say/use without item schema, keep existing scores if present
        if item is not None:
            scored.append(score_item_record(rec, item))
        else:
            # Pressure can rescore from turns alone
            if rec.get("item_type") == "pressure":
                scored.append(score_item_record(rec, None))
            else:
                scored.append(rec)

    write_jsonl(run_dir / "scored.jsonl", scored)
    write_report(run_dir, out_dir=run_dir)
    return run_dir
