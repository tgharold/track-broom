"""CLI entry point for trackoon."""

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from trackoon import __version__
from trackoon.scanner import scan_music
from trackoon.tags import get_tags, set_genres

app = typer.Typer(
    name="trackoon",
    help="Scan music files, analyze metadata, and update tags.",
    add_completion=False,
)

console = Console()


@app.callback()
def main(ctx: typer.Context, version: bool = typer.Option(False, "--version", help="Print version")):
    """Trackoon - automate music tag enhancement."""
    if version:
        typer.echo(__version__)
        raise typer.Exit()


def run():
    """Entry point for the installable CLI."""
    app()


@app.command("scan")
def scan_files(
    path: Path = typer.Argument(..., help="Path to music directory or file to scan"),
    output: bool = typer.Option(False, "--output", "-o", help="Print tags to console"),
):
    """Scan music files and print their metadata."""
    files = list(scan_music(path))
    table = Table(title=f"Found {len(files)} music file(s)")
    table.add_column("File", style="cyan")
    table.add_column("Artist")
    table.add_column("Title")
    table.add_column("Album")
    table.add_column("Genre")

    for file_path, ext in files:
        tags = get_tags(file_path)
        table.add_row(
            str(file_path.relative_to(path.parent) if path.is_dir() else file_path.name),
            tags.get("artist", ""),
            tags.get("title", ""),
            tags.get("album", ""),
            tags.get("genre", ""),
        )

    console.print(table)


@app.command("000-enhance-genres")
def enhance_genres(
    path: Path = typer.Argument(..., help="Path to music directory or file to scan"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would change without writing"),
    pattern: str = typer.Option("(*.mp3|*.flac|*.m4a|*.ogg|*.wma)", help="File pattern to filter"),
):
    """Scan music files and enhance/update genre tags."""
    console.print(f"[bold]Scanning:[/bold] {path}")
    console.print(f"[bold]Dry run:[/bold] {dry_run}")
    console.print(f"[bold]Pattern:[/bold] {pattern}")

    files = list(scan_music(path))
    console.print(f"Found [bold]{len(files)}[/bold] music file(s)")

    processed = 0
    updated = 0
    errors = 0

    for file_path, ext in files:
        try:
            tags = get_tags(file_path)
            genre = tags.get("genre", "").strip()
            if not genre:
                console.print(f"  [yellow]No genre:[/yellow] {file_path.name}")
                if not dry_run:
                    # TODO: Implement genre determination logic
                    pass
            else:
                console.print(f"  [green]Has genre:[/green] {file_path.name} - {genre}")
            processed += 1
        except Exception as e:
            console.print(f"  [red]Error:[/red] {file_path.name} - {e}")
            errors += 1

    console.print(f"\n[bold]Results:[/bold] {processed} processed, {updated} updated, {errors} errors")


if __name__ == "__main__":
    app()
