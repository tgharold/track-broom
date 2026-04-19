"""Generate test MP3s with synthetic tones and ID3 tags."""

import math
import struct

import ffmpeg
from mutagen.id3 import TALB, TCON, TIT2, TPE1, TRCK
from mutagen.mp3 import MP3


def tone_samples(
    freq: int = 440,
    duration: float = 3.0,
    samplerate: int = 44100,
) -> bytes:
    """Generate raw PCM samples for a sine wave at the given frequency.

    Uses signed 16-bit little-endian format with a 50ms fade-in/fade-out
    to avoid clicks and normalizes to the 16-bit range.
    """
    num_samples = int(samplerate * duration)
    fade_samples = int(samplerate * 0.05)

    samples = []
    for i in range(num_samples):
        t = i / samplerate
        amp = math.sin(2.0 * math.pi * freq * t)
        if i < fade_samples:
            envelope = i / fade_samples
        elif i > num_samples - fade_samples:
            envelope = (num_samples - i) / fade_samples
        else:
            envelope = 1.0
        amp *= envelope
        samples.append(int(amp * 32767))

    max_val = max(abs(s) for s in samples) if samples else 1
    if max_val > 0:
        scaled = [s * 32767 // max_val for s in samples]
    else:
        scaled = samples

    return struct.pack(f"<{len(scaled)}h", *scaled)


def encode_mp3(
    pcm_data: bytes,
    output_path: str,
    samplerate: int = 44100,
    channels: int = 1,
    bitrate: int = 128,
) -> str:
    """Encode raw PCM bytes to MP3 using ffmpeg-python.

    Returns output_path on success, raises ffmpeg.Error on failure.
    """
    (
        ffmpeg
        .input("pipe:0", format="s16le", ar=samplerate, ac=channels)
        .output(output_path, ar=samplerate, **{"b:a": f"{bitrate}k"})
        .overwrite_output()
        .run(input=pcm_data, capture_stdout=True, capture_stderr=True)
    )
    return output_path


def add_id3_tags(
    filepath: str,
    title: str,
    artist: str = "",
    album: str = "",
    genre: str = "",
    tracknumber: int = 1,
) -> None:
    """Write ID3 tags to an MP3 file.

    Sets TIT2 (title), TPE1 (artist), TALB (album), TCON (genre),
    and TRCK (track) as UTF-8 encoded text frames.
    """
    audio = MP3(filepath)

    if audio.tags is None:
        audio.add_tags()

    tags = audio.tags
    tags.add(TIT2(encoding=3, text=title))
    if artist:
        tags.add(TPE1(encoding=3, text=artist))
    if album:
        tags.add(TALB(encoding=3, text=album))
    if genre:
        tags.add(TCON(encoding=3, text=genre))
    tags.add(TRCK(encoding=3, text=str(tracknumber)))

    audio.save()
