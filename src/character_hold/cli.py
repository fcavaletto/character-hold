"""CLI entry point: character-hold."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console

from character_hold.analyze import write_report
from character_hold.runner import load_config, rescore_run, run_evaluation, validate_paths

app = typer.Typer(add_completion=False, no_args_is_help=True, help="character-hold evaluation CLI")
console = Console()


def _root() -> Path:
    return Path.cwd()


@app.command("validate")
def validate(
    config: Path = typer.Option(Path("configs/default.yaml"), "--config", help="Config YAML"),
) -> None:
    """Validate specimens + scenarios against schema and cross-references."""
    load_dotenv()
    cfg = load_config(config)
    # Prefer project dirs; fall back to fixtures for dry validation
    report = validate_paths(cfg)
    if not report["ok"]:
        fixtures = _root() / "tests" / "fixtures"
        from character_hold.schema import RunConfig

        alt = cfg.model_copy(
            update={
                "specimens_dir": str(fixtures / "specimens"),
                "scenarios_dir": str(fixtures / "scenarios"),
            }
        )
        report = validate_paths(alt)
        if report["ok"]:
            console.print(
                "[yellow]Project specimens/scenarios missing; fixtures validate OK.[/yellow]"
            )
    if report["ok"]:
        console.print(
            f"[green]OK[/green] specimens={report['n_specimens']} scenarios={report['n_scenarios']}"
        )
        raise typer.Exit(0)
    for err in report["errors"]:
        console.print(f"[red]ERROR[/red] {err}")
    raise typer.Exit(1)


@app.command("run")
def run(
    config: Path = typer.Option(Path("configs/default.yaml"), "--config"),
    provider: Optional[str] = typer.Option(None, "--provider"),
    model: Optional[str] = typer.Option(None, "--model"),
    run_id: Optional[str] = typer.Option(
        None, "--run-id", help="Stable results subdir (e.g. pilot) under results/"
    ),
) -> None:
    """Execute evaluation suites and write JSONL under results/."""
    load_dotenv()
    cfg = load_config(config)
    run_dir = run_evaluation(
        cfg,
        provider_override=provider,
        model_override=model,
        project_root=_root(),
        run_id_override=run_id,
    )
    console.print(f"[green]Run complete[/green] → {run_dir}")


@app.command("score")
def score(
    input: Path = typer.Option(..., "--input", help="Run directory or raw.jsonl"),
    scenarios_dir: Optional[Path] = typer.Option(None, "--scenarios-dir"),
) -> None:
    """Re-score raw logs offline (deterministic)."""
    load_dotenv()
    out = rescore_run(input, scenarios_dir=scenarios_dir)
    console.print(f"[green]Scored[/green] → {out}")


@app.command("report")
def report(
    input: Path = typer.Option(..., "--input", help="Run directory or scored.jsonl"),
) -> None:
    """Write summary JSON + markdown tables."""
    load_dotenv()
    paths = write_report(input)
    console.print(f"[green]Report[/green] → {paths['summary_md']}")


if __name__ == "__main__":
    app()
