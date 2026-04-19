"""Read and write metadata from music files using mutagen."""

from pathlib import Path

from mutagen import File as MutagenFile
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis

try:
    from mutagen.wma import WMA
except ImportError:
    WMA = None


STANDARD_FIELDS = [
    "artist",
    "title",
    "album",
    "date",
    "genre",
    "discnumber",
    "tracknumber",
]

MP3_FIELD_MAP = {
    "artist": "TPE1",
    "title": "TIT2",
    "album": "TALB",
    "date": "TDRC",
    "genre": "TCON",
    "discnumber": "TPA",
    "tracknumber": "TRCK",
}

MP4_FIELD_MAP = {
    "artist": "\xa9ART",
    "title": "\xa9nam",
    "album": "\xa9alb",
    "date": "\xa9day",
    "genre": "gnr ",
    "discnumber": "disk",
    "tracknumber": "trkn",
}


def get_tags(file_path: Path) -> dict:
    """Read metadata tags from a music file.

    Returns a dict mapping standard field names to their string values.
    Missing fields map to empty strings.
    """
    audio = _load_file(file_path)
    if audio is None:
        return {f: "" for f in STANDARD_FIELDS}

    ext = file_path.suffix.lower()
    field_map = _get_field_map(ext)

    result: dict[str, str] = {}
    for field_name in STANDARD_FIELDS:
        tag_key = field_map.get(field_name, field_name)
        val = audio.tags.get(tag_key)
        if val is not None:
            items = [str(v) for v in val if v]
            result[field_name] = items[0] if len(items) == 1 else " ".join(items)
        else:
            result[field_name] = ""

    return result


def set_tag(file_path: Path, field_name: str, value: str) -> None:
    """Write a single tag field to a music file."""
    if not file_path.is_file():
        return

    audio = _load_file(file_path)
    if audio is None:
        return

    ext = file_path.suffix.lower()
    field_map = _get_field_map(ext)
    tag_key = field_map.get(field_name, field_name)

    audio.tags[tag_key] = [value]
    audio.tags.save()


def set_genres(file_path: Path, genres: list[str]) -> None:
    """Append new genres to what's already stored.

    Collects existing genres (split on semicolons), then
    writes the combined list back as a semicolon-separated string.
    """
    existing = get_tags(file_path).get("genre")
    existing_genres = [g.strip() for g in existing.split(";")] if existing else []
    existing_genres = [g for g in existing_genres if g]

    all_genres = existing_genres + [g.strip() for g in genres if g.strip()]
    if not all_genres:
        return

    combined = "; ".join(all_genres)
    set_tag(file_path, "genre", combined)


def has_genre(file_path: Path) -> bool:
    """Check if a file has a non-empty genre tag."""
    tags = get_tags(file_path)
    return bool(tags.get("genre", "").strip())


def _get_field_map(ext: str) -> dict:
    """Return mapping of standard field names to mutagen tag keys."""
    if ext == ".mp3":
        return MP3_FIELD_MAP
    if ext == ".m4a":
        return MP4_FIELD_MAP
    # FLAC and OGG use lowercase field names
    return {f: f for f in STANDARD_FIELDS}


def _load_file(file_path: Path):
    """Load a mutagen audio object with tags, or None on failure."""
    ext = file_path.suffix.lower()
    try:
        if ext == ".mp3":
            audio = MP3(str(file_path), ID3=MP3)
        elif ext == ".flac":
            audio = FLAC(str(file_path))
        elif ext == ".m4a":
            audio = MP4(str(file_path))
        elif ext == ".ogg":
            audio = OggVorbis(str(file_path))
        elif ext == ".wma":
            audio = WMA(str(file_path))
        else:
            audio = MutagenFile(str(file_path))
    except Exception:
        return None

    tags = getattr(audio, "tags", None)
    if tags is None:
        return None

    return audio
