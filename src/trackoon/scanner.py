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
