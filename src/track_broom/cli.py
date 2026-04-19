"""CLI entry point for track_broom."""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from track_broom import __version__
from track_broom.filetree import FileSystemDirectoryEntry, FileSystemFileEntry
from track_broom.scanner import list_files, scan_music
from track_broom.tags import get_tags

app = typer.Typer(
    name="track_broom",
    help="Scan music files, analyze metadata, and update tags.",
    add_completion=False,
)

console = Console()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Print version"),
):
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

    for file_path, _ext in files:
        tags = get_tags(file_path)
        table.add_row(
            str(file_path.relative_to(path.parent) if path.is_dir() else file_path.name),
            tags.get("artist", ""),
            tags.get("title", ""),
            tags.get("album", ""),
            tags.get("genre", ""),
        )

    console.print(table)


@app.command("list")
def list_files_cmd(
    path: Path = typer.Argument(..., help="Path to directory to list"),
    extension: str | None = typer.Option(
        None,
        "--ext",
        "-e",
        help="Filter by extension (e.g. mp3, pdf)",
    ),
    output_json: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output results as JSON",
    ),
):
    """List all files in a directory recursively."""
    files = list(list_files(path, extension=extension))
    if not files:
        if output_json:
            typer.echo(json.dumps({"results": []}))
        else:
            console.print("[yellow]No files found[/yellow]")
        return
    root_dir = FileSystemDirectoryEntry(path) if path.is_dir() else None
    results = []
    for file_path, _ext in files:
        if root_dir:
            entry = FileSystemFileEntry(file_path, parent=root_dir)
        else:
            entry = FileSystemFileEntry(file_path)
        if path.is_dir():
            display = entry.path.relative_to(path)
        else:
            display = entry.path
        results.append(
            {
                "path": str(display),
                "directory": str(display.parent) if display.parent != Path(".") else "",
                "filename": display.name,
                "extension": entry.extension,
            }
        )
    if output_json:
        typer.echo(json.dumps({"results": results}))
    else:
        for result in results:
            console.print(result["path"])


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

    for file_path, _ext in files:
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

    console.print(
        f"\n[bold]Results:[/bold] {processed} processed, {updated} updated, {errors} errors"
    )


if __name__ == "__main__":
    app()
