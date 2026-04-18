"""Scan directories for music files."""

from pathlib import Path

MUSIC_EXTENSIONS = {".mp3", ".flac", ".m4a", ".ogg", ".wma", ".wav", ".aac", ".mka"}


def scan_music(directory: Path):
    """Find all music files recursively in a directory or yield a single file if not a directory.

    Yields (file_path, extension) tuples.
    """
    if not directory.is_dir():
        if directory.suffix.lower() in MUSIC_EXTENSIONS:
            yield (directory, directory.suffix.lower())
        return

    for ext in MUSIC_EXTENSIONS:
        for file_path in directory.rglob(f"*{ext}"):
            if file_path.is_file():
                yield (file_path, ext)


def list_files(directory: Path, extension: str | None = None):
    """Recursively list all files in a directory.

    If extension is provided, only yield files matching that extension.
    Yields (file_path, extension) tuples.
    """
    if not directory.is_dir():
        ext = directory.suffix.lstrip(".") if directory.suffix else ""
        if extension is None or ext == extension.lstrip("."):
            yield (directory, ext)
        return

    for file_path in sorted(directory.rglob("*")):
        if not file_path.is_file():
            continue
        ext = file_path.suffix.lstrip(".")
        if extension is None or ext == extension.lstrip("."):
            yield (file_path, ext)
