"""Shared test tone builders for all supported audio formats.

Used by both the standalone generate scripts and pytest fixtures.
"""

from pathlib import Path

from tests.utils import (
    add_flac_tags,
    add_id3_tags,
    add_m4a_tags,
    add_ogg_tags,
    add_wma_tags,
    encode_flac,
    encode_mp3,
    encode_m4a,
    encode_ogg,
    encode_wma,
    tone_samples,
)

# Create at least one of each file format, but you can create more if you want
TRACKS = [
    {
        "format": "wma",
        "name": "note_C_wma",
        "freq": 261.63,
        "duration": 3.5,
        "title": "WMA C",
        "artist": "Harmonics & WMA",
        "album": "C",
        "genre": "Classical",
        "tracknumber": 1,
    },
    {
        "format": "ogg",
        "name": "note_B_flat_ogg",
        "freq": 233.08,
        "duration": 1.5,
        "title": "Ogg B Flat",
        "artist": "Harmonics & Ogg",
        "album": "B-Flat",
        "genre": "Classical",
        "tracknumber": 1,
    },
    {
        "format": "mp3",
        "name": "note_A_mp3",
        "freq": 440,
        "duration": 3.0,
        "title": "MP3 A",
        "artist": "MP3 Harmonics",
        "album": "A",
        "genre": "Classical",
        "tracknumber": 2,
    },
    {
        "format": "flac",
        "name": "note_A_FLAC",
        "freq": 440,
        "duration": 1.0,
        "title": "FLAC A",
        "artist": "FLAC Harmonics",
        "album": "A FLAC",
        "genre": "Classical",
        "tracknumber": 2,
    },
    {
        "format": "m4a",
        "name": "note_B_natural_m4a",
        "freq": 493.88,
        "duration": 4.0,
        "title": "B Natural M4A",
        "artist": "Dancing M4A Humore",
        "album": "H",
        "genre": "Classical",
        "tracknumber": 3,
    },
]

FORMATS = {
    "mp3": {"encode": encode_mp3, "tags": add_id3_tags, "encode_kw": {"b:a": "192k"}},
    "flac": {"encode": encode_flac, "tags": add_flac_tags},
    "m4a": {"encode": encode_m4a, "tags": add_m4a_tags},
    "ogg": {"encode": encode_ogg, "tags": add_ogg_tags},
    "wma": {"encode": encode_wma, "tags": add_wma_tags},
}

EXPECTED_TOTAL_FILES = len(TRACKS)

def _build_tone_file(
    output_dir: Path,
    track: dict,
    encode_kw: dict | None = None,
) -> Path:
    """Encode and tag a single tone file in the given format."""
    fmt = track["format"]
    fmt_dir = output_dir / fmt
    fmt_dir.mkdir(parents=True, exist_ok=True)
    info = FORMATS[fmt]
    pcm = tone_samples(
        freq=int(track["freq"]),
        duration=track["duration"],
        samplerate=44100,
    )
    filename = f"{track['name']}.{fmt}"
    path = output_dir / filename

    encoder_kw = {**(encode_kw or {})}
    info["encode"](pcm, str(path), **encoder_kw)

    info["tags"](
        filepath=str(path),
        title=track["title"],
        artist=track["artist"],
        album=track["album"],
        genre=track["genre"],
        tracknumber=track["tracknumber"],
    )
    return path

def generate_sample_dir(base: Path) -> int:
    """Generate all sample files for all formats under *base*.
    Returns the total number of files created.
    """
    total = 0
    for track in TRACKS:
        path = _build_tone_file(base, track)
        total += 1

    return total
