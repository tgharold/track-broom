"""CLI entry point for trackoon."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from trackoon import __version__
from trackoon.scanner import list_files, scan_music
from trackoon.tags import get_tags, set_genres
from trackoon.util import tone_samples, encode_mp3, add_id3_tags

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

@app.command("list")
def list_files_cmd(
    path: Path = typer.Argument(..., help="Path to directory to list"),
    extension: str | None = typer.Option(None, "--ext", "-e", help="Filter by extension (e.g. mp3, pdf)"),
):
    """List all files in a directory recursively."""
    files = list(list_files(path, extension=extension))
    if not files:
        console.print("[yellow]No files found[/yellow]")
        return
    for file_path, ext in files:
        if path.is_dir():
            console.print(str(file_path.relative_to(path)))
        else:
            console.print(file_path.name)



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


@app.command()
def generate_tone(
    freq: float = typer.Option(440.0, "--freq", help="Tone frequency in Hz"),
    duration: float = typer.Option(5.0, "--duration", help="Duration in seconds"),
    output: Path = typer.Option(Path("./tone.mp3"), "--output", "-o", help="Output file path"),
    samplerate: int = typer.Option(44100, "--samplerate", help="Sample rate in Hz"),
    channels: int = typer.Option(1, "--channels", help="Mono=1 / Stereo=2"),
    bitrate: int = typer.Option(128, "--bitrate", help="MP3 bitrate in kbps"),
    title: str = typer.Option("Generated Tone", "--title", help="ID3 title tag"),
    artist: str = typer.Option("", "--artist", help="ID3 artist tag"),
    album: str = typer.Option("", "--album", help="ID3 album tag"),
    genre: str = typer.Option("", "--genre", help="ID3 genre tag"),
    tracknumber: int = typer.Option(1, "--tracknumber", help="Track number"),
):
    """Generate a synthetic tone and save it as an MP3 file with ID3 tags."""
    console.print(f"[bold]Generating tone:[/bold] {freq} Hz, {duration}s")
    console.print(f"[bold]Output:[/bold] {output}")

    pcm_path = output.with_suffix(".pcm")
    pcm_data = tone_samples(freq=int(freq), duration=duration, samplerate=samplerate)
    pcm_path.write_bytes(pcm_data)
    console.print(f"  [green]PCM:[/green] {pcm_path}")

    encode_mp3(
        pcm_data=pcm_data,
        output_path=str(output),
        samplerate=samplerate,
        channels=channels,
        bitrate=bitrate,
    )
    console.print(f"  [green]MP3:[/green] {output}")

    add_id3_tags(
        filepath=str(output),
        title=title,
        artist=artist,
        album=album,
        genre=genre,
        tracknumber=tracknumber,
    )
    console.print(f"  [green]ID3 tags:[/green] title={title}, artist={artist or '(none)'}")
    console.print(f"  [green]Done:[/green] {output}")

    try:
        pcm_path.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    app()
