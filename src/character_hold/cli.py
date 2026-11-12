"""CLI entry point: character-hold."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console

from character_hold.analyze import write_report
from character_hold.runner import load_config, rescore_run, run_evaluation, validate_paths

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


@app.command("validate")
def validate(
    config: Path = typer.Option(Path("configs/default.yaml"), "--config", help="Config YAML"),
) -> None:
    """Validate specimens + scenarios against schema and cross-references."""
    load_dotenv()
    cfg = load_config(config)
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


if __name__ == "__main__":
    app()
