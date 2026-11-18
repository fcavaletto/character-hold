"""CLI entry point: character-hold."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console

from character_hold.analyze import write_report
from character_hold.annotate import run_dual_annotation
from character_hold.agreement import compare_author_labels
from character_hold.runner import load_config, rescore_run, run_evaluation, validate_paths
from character_hold.schema import AblationMode

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help=(
        "character-hold: evaluate whether declared assistant character "
        "survives saying → using → holding under pressure."
    ),
)
console = Console()


def _root() -> Path:
    return Path.cwd()


def _resolve_cfg_paths(cfg, config_path: Path):
    """Resolve specimen/scenario dirs relative to CWD, else config's project root."""
    root = _root()
    cfg_root = config_path.resolve().parent.parent if config_path else root
    updates = {}
    for key in ("specimens_dir", "scenarios_dir", "results_dir"):
        raw = getattr(cfg, key)
        p = Path(raw)
        if p.is_absolute() and p.exists():
            continue
        if (root / raw).exists():
            updates[key] = str((root / raw).resolve())
        elif (cfg_root / raw).exists():
            updates[key] = str((cfg_root / raw).resolve())
    return cfg.model_copy(update=updates) if updates else cfg


@app.command("validate")
def validate(
    config: Path = typer.Option(Path("configs/default.yaml"), "--config", help="Config YAML"),
) -> None:
    """Validate specimens + scenarios against schema and cross-references."""
    load_dotenv()
    cfg = _resolve_cfg_paths(load_config(config), config)
    report = validate_paths(cfg)
    if not report["ok"]:
        fixtures = _root() / "tests" / "fixtures"
        if not fixtures.exists():
            fixtures = config.resolve().parent.parent / "tests" / "fixtures"
        from character_hold.schema import RunConfig

        alt = cfg.model_copy(
            update={
                "specimens_dir": str(fixtures / "specimens"),
                "scenarios_dir": str(fixtures / "scenarios"),
                "specimen_ids": None,
            }
        )
        report = validate_paths(alt)
        if report["ok"]:
            console.print(
                "[yellow]Project specimens/scenarios missing; fixtures validate OK.[/yellow]"
            )
    if report["ok"]:
        by_type = report.get("by_type") or {}
        type_bits = " ".join(f"{k}={v}" for k, v in sorted(by_type.items()))
        console.print(
            f"[green]OK[/green] specimens={report['n_specimens']} "
            f"scenarios={report['n_scenarios']}"
            + (f" ({type_bits})" if type_bits else "")
        )
        raise typer.Exit(0)
    for err in report["errors"]:
        console.print(f"[red]ERROR[/red] {err}")
    raise typer.Exit(1)


@app.command("run")
def run(
    config: Path = typer.Option(Path("configs/default.yaml"), "--config", help="Config YAML"),
    provider: Optional[str] = typer.Option(
        None, "--provider", help="Provider override: mock | openai | anthropic | openrouter"
    ),
    model: Optional[str] = typer.Option(None, "--model", help="Model id override"),
    run_id: Optional[str] = typer.Option(
        None, "--run-id", help="Stable results subdir (e.g. pilot) under results/"
    ),
    resume: bool = typer.Option(
        False,
        "--resume",
        help="Keep an existing run-id JSONL and skip item ids already logged",
    ),
    ablation: Optional[str] = typer.Option(
        None,
        "--ablation",
        help=(
            "Ablation arm: character | stripped | imperative | naturalistic_reverse | "
            "character_user | format_rule | no_character | demand_opposite | opposite_character"
        ),
    ),
) -> None:
    """Execute evaluation suites and write JSONL under results/."""
    load_dotenv()
    cfg = _resolve_cfg_paths(load_config(config), config)
    if ablation:
        cfg = cfg.model_copy(update={"ablation_mode": AblationMode(ablation)})
    run_dir = run_evaluation(
        cfg,
        provider_override=provider,
        model_override=model,
        project_root=_root(),
        run_id_override=run_id,
        resume=resume,
    )
    console.print(f"[green]Run complete[/green] → {run_dir}")
    console.print(f"         ablation={cfg.ablation_mode.value}")


@app.command("score")
def score(
    input: Path = typer.Option(..., "--input", help="Run directory or raw.jsonl"),
    scenarios_dir: Optional[Path] = typer.Option(
        None, "--scenarios-dir", help="Scenario YAML dir for offline say/use rescoring"
    ),
) -> None:
    """Re-score raw logs offline (deterministic)."""
    load_dotenv()
    out = rescore_run(input, scenarios_dir=scenarios_dir)
    console.print(f"[green]Scored[/green] → {out}")


@app.command("report")
def report(
    input: Path = typer.Option(..., "--input", help="Run directory or scored.jsonl"),
    no_figures: bool = typer.Option(False, "--no-figures", help="Skip matplotlib figures"),
    no_html: bool = typer.Option(False, "--no-html", help="Skip report.html"),
) -> None:
    """Write summary JSON/MD, report.md, figures, and optional report.html."""
    load_dotenv()
    paths = write_report(input, write_figures=not no_figures, write_html=not no_html)
    console.print(f"[green]Report[/green] summary → {paths['summary_md']}")
    console.print(f"         report.md → {paths['report_md']}")
    if paths.get("report_html"):
        console.print(f"         report.html → {paths['report_html']}")
    if paths.get("figures"):
        console.print(f"         figures → {Path(list(paths['figures'].values())[0]).parent}")
    console.print(f"         INDEX → {paths['index_md']}")


@app.command("annotate-pressure")
def annotate_pressure(
    input: Path = typer.Option(..., "--input", help="Subject run directory (scored.jsonl)"),
    judge_provider: str = typer.Option(
        "openrouter", "--judge-provider", help="Provider for secondary LLM judge"
    ),
    judge_model: str = typer.Option(
        ...,
        "--judge-model",
        help="Judge model id (prefer a different family than the subject)",
    ),
    sample: int = typer.Option(24, "--sample", help="Number of pressure dialogues to annotate"),
    seed: int = typer.Option(0, "--seed", help="Sampling seed"),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        help="Output directory (default: <input>/dual_annotation/)",
    ),
    item_ids: Optional[str] = typer.Option(
        None,
        "--item-ids",
        help="Comma-separated item ids (overrides stratified sampling)",
    ),
) -> None:
    """Dual-annotate a pressure subset: heuristic primary + LLM judge secondary."""
    load_dotenv()
    out = output or (input / "dual_annotation")
    ids = [x.strip() for x in item_ids.split(",") if x.strip()] if item_ids else None
    result = run_dual_annotation(
        input_dir=input,
        output_dir=out,
        judge_provider=judge_provider,
        judge_model=judge_model,
        sample=sample,
        seed=seed,
        item_ids=ids,
    )
    agr = result["agreement"]
    console.print(
        f"[green]Dual annotation[/green] n={agr['n']} → {result['output_dir']}"
    )
    console.print(
        "  fracture match="
        f"{agr['fracture']['exact_match_rate']:.3f} "
        f"κ={agr['fracture']['cohens_kappa']}"
    )
    console.print(
        "  identity match="
        f"{agr['identity']['exact_match_rate']:.3f} "
        f"κ={agr['identity']['cohens_kappa']}"
    )
    console.print(
        "  principle match="
        f"{agr['principle']['exact_match_rate']:.3f} "
        f"κ={agr['principle']['cohens_kappa']}"
    )
    console.print(
        "[yellow]Note[/yellow] LLM judge is secondary only; primary hold/say/use unchanged."
    )


@app.command("agree")
def agree(
    author: Path = typer.Option(
        ...,
        "--author",
        help="Author annotation JSONL (annotations/pressure_v2_author/*.jsonl)",
    ),
    run: Optional[Path] = typer.Option(
        None,
        "--run",
        help="Subject run dir for heuristic labels (default: infer from annotation meta)",
    ),
    judge: Optional[Path] = typer.Option(
        None,
        "--judge",
        help="Optional dual_annotation dir with LLM-judge labels",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        help="Output directory for agreement tables (default: alongside author file)",
    ),
) -> None:
    """Compare heuristic (± LLM judge) labels against author codebook annotations."""
    load_dotenv()
    out = compare_author_labels(
        author_path=author,
        run_dir=run,
        judge_dir=judge,
        output_dir=output,
    )
    console.print(f"[green]Agreement[/green] → {out['output_dir']}")
    for key, blob in (out.get("agreement") or {}).items():
        if not isinstance(blob, dict):
            continue
        if "exact_match_rate" in blob:
            console.print(
                f"  {key}: match={blob['exact_match_rate']:.3f} "
                f"κ={blob.get('cohens_kappa')} n={blob.get('n')}"
            )


if __name__ == "__main__":
    app()
