"""CLI entry point for trackoon."""

import sys
from pathlib import Path

import typer

from trackoon import __version__

app = typer.Typer(
    name="trackoon",
    help="Scan music files, analyze metadata, and update tags.",
    add_completion=False,
)


@app.callback()
def main(ctx: typer.Context, version: bool = typer.Option(False, "--version", help="Print version")):
    """Trackoon - automate music tag enhancement."""
    if version:
        typer.echo(__version__)
        raise typer.Exit()


def run():
    """Entry point for the installable CLI."""
    app()


@app.command("000-enhance-genres")
def enhance_genres(
    path: Path = typer.Argument(..., help="Path to music directory or file to scan"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would change without writing"),
    pattern: str = typer.Option("(*.mp3|*.flac|*.m4a|*.ogg|*.wma)", help="File pattern to filter"),
):
    """Scan music files and enhance/update genre tags."""
    typer.echo(f"Scanning: {path}")
    typer.echo(f"Dry run: {dry_run}")
    typer.echo(f"Pattern: {pattern}")
    typer.echo("Not yet implemented.")


if __name__ == "__main__":
    run()
