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
    encode_m4a,
    encode_mp3,
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
    {
        "format": "wma",
        "name": "note_E_wma",
        "freq": 329.63,
        "duration": 2.0,
        "title": "WMA E Major",
        "artist": "Retro WMA Beats",
        "album": "WMA Collection",
        "genre": "Jazz",
        "tracknumber": 5,
    },
    {
        "format": "wma",
        "name": "note_F_sharp_wma",
        "freq": 370.0,
        "duration": 2.5,
        "title": "WMA F Sharp",
        "artist": "Vinyl WMA Stylings",
        "album": "WMA Grooves",
        "genre": "Blues",
        "tracknumber": 7,
    },
    {
        "format": "ogg",
        "name": "note_G_ogg",
        "freq": 392.0,
        "duration": 1.8,
        "title": "OGG G Minor",
        "artist": "Open Source OGG",
        "album": "OGG Sounds",
        "genre": "Electronic",
        "tracknumber": 4,
    },
    {
        "format": "ogg",
        "name": "note_D_flat_ogg",
        "freq": 311.13,
        "duration": 3.2,
        "title": "OGG D Flat Blues",
        "artist": "Vorbis OGG Project",
        "album": "OGG Vibes",
        "genre": "Folk",
        "tracknumber": 6,
    },
    {
        "format": "mp3",
        "name": "note_E_mp3",
        "freq": 329.63,
        "duration": 2.2,
        "title": "MP3 E Minor",
        "artist": "Layer II MP3",
        "album": "MP3 Classics",
        "genre": "Rock",
        "tracknumber": 8,
    },
    {
        "format": "mp3",
        "name": "note_F_sharp_mp3",
        "freq": 370.0,
        "duration": 1.3,
        "title": "MP3 F Sharp Rag",
        "artist": "MPEG MP3 Syndicate",
        "album": "MP3 Nights",
        "genre": "Country",
        "tracknumber": 10,
    },
    {
        "format": "flac",
        "name": "note_G_FLAC",
        "freq": 392.0,
        "duration": 2.7,
        "title": "FLAC G Suite",
        "artist": "Free Lossless FLAC",
        "album": "FLAC Studio",
        "genre": "Electronic",
        "tracknumber": 9,
    },
    {
        "format": "flac",
        "name": "note_D_flat_FLAC",
        "freq": 311.13,
        "duration": 3.8,
        "title": "FLAC D Flat Dolce",
        "artist": "Lossless FLAC Ensemble",
        "album": "FLAC Voyages",
        "genre": "Blues",
        "tracknumber": 11,
    },
    {
        "format": "m4a",
        "name": "note_E_m4a",
        "freq": 329.63,
        "duration": 2.4,
        "title": "M4A E Mantra",
        "artist": "Apple M4A Studios",
        "album": "M4A Harmony",
        "genre": "Electronic",
        "tracknumber": 12,
    },
    {
        "format": "m4a",
        "name": "note_F_sharp_m4a",
        "freq": 370.0,
        "duration": 1.6,
        "title": "M4A F Sharp Funk",
        "artist": "AAC M4A Collective",
        "album": "M4A Pulse",
        "genre": "Jazz",
        "tracknumber": 13,
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
        _build_tone_file(base, track)
        total += 1

    return total
