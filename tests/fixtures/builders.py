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

TONES = [
    {
        "name": "note_C",
        "freq": 261.63,
        "duration": 3.0,
        "title": "C",
        "artist": "Harmonics",
        "album": "C",
        "genre": "Classical",
        "tracknumber": 1,
    },
    {
        "name": "note_A",
        "freq": 440,
        "duration": 3.0,
        "title": "A",
        "artist": "Harmonics",
        "album": "A",
        "genre": "Classical",
        "tracknumber": 2,
    },
    {
        "name": "note_H",
        "freq": 415.30,
        "duration": 4.0,
        "title": "H",
        "artist": "Humore",
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

EXPECTED_TOTAL_FILES = len(TONES) * len(FORMATS)


def _build_tone_file(
    output_dir: Path,
    tone: dict,
    fmt: str,
    encode_kw: dict | None = None,
) -> Path:
    """Encode and tag a single tone file in the given format."""
    info = FORMATS[fmt]
    pcm = tone_samples(
        freq=int(tone["freq"]),
        duration=tone["duration"],
        samplerate=44100,
    )
    filename = f"{tone['name']}.{fmt}"
    path = output_dir / filename

    encoder_kw = {**(encode_kw or {})}
    info["encode"](pcm, str(path), **encoder_kw)

    info["tags"](
        filepath=str(path),
        title=tone["title"],
        artist=tone["artist"],
        album=tone["album"],
        genre=tone["genre"],
        tracknumber=tone["tracknumber"],
    )
    return path


def generate_sample_dir(base: Path) -> int:
    """Generate all sample files for all formats under *base*.

    Creates one subdirectory per format (mp3/, flac/, m4a/, ogg/, wma/)
    with 3 tone files each (note_C, note_A, note_H).

    Returns the total number of files created.
    """
    total = 0
    for fmt, meta in FORMATS.items():
        fmt_dir = base / fmt
        fmt_dir.mkdir(parents=True, exist_ok=True)

        for tone in TONES:
            path = _build_tone_file(fmt_dir, tone, fmt, encode_kw=meta.get("encode_kw"))
            total += 1

    return total
