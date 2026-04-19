#!/usr/bin/env python3
"""Generate standard test M4A tone files."""

from pathlib import Path

from tests.utils import add_m4a_tags, encode_m4a, tone_samples

OUTPUT_DIR = Path("test_files/m4a")

TONES = [
    {
        "filename": "note_C.m4a",
        "freq": 261.63,
        "duration": 3.0,
        "title": "C",
        "artist": "Harmonics",
        "album": "C",
        "genre": "Classical",
        "tracknumber": 1,
    },
    {
        "filename": "note_A.m4a",
        "freq": 440,
        "duration": 3.0,
        "title": "A",
        "artist": "Harmonics",
        "album": "A",
        "genre": "Classical",
        "tracknumber": 2,
    },
    {
        "filename": "note_H.m4a",
        "freq": 415.30,
        "duration": 4.0,
        "title": "H",
        "artist": "Humore",
        "album": "H",
        "genre": "Classical",
        "tracknumber": 3,
    },
]


def main() -> int:
    """Generate all test M4A files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for tone_info in TONES:
        print(f"Generating {tone_info['filename']}: {tone_info['freq']} Hz")

        pcm_data = tone_samples(
            freq=int(tone_info["freq"]),
            duration=tone_info["duration"],
            samplerate=44100,
        )

        output_path = OUTPUT_DIR / tone_info["filename"]
        encode_m4a(pcm_data, str(output_path))

        add_m4a_tags(
            filepath=str(output_path),
            title=tone_info["title"],
            artist=tone_info["artist"],
            album=tone_info["album"],
            genre=tone_info["genre"],
            tracknumber=tone_info["tracknumber"],
        )

        print(f"  Created {output_path}")

    print(f"All {len(TONES)} tones generated in {OUTPUT_DIR}/")

    return len(TONES)


if __name__ == "__main__":
    main()
