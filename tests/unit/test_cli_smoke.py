"""CLI smoke via typer testing."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from character_hold.cli import app

ROOT = Path(__file__).resolve().parents[2]
runner = CliRunner()


def test_cli_validate_ok():
    result = runner.invoke(app, ["validate", "--config", str(ROOT / "configs" / "default.yaml")])
    assert result.exit_code == 0, result.output
    assert "OK" in result.output
    assert "144" in result.output or "scenarios=" in result.output


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "saying" in result.output.lower() or "character" in result.output.lower()
