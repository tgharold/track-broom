"""Generate test MP3s with synthetic tones and ID3 tags."""

import math
import struct

import ffmpeg
from mutagen.id3._frames import TALB, TCON, TIT2, TPE1, TRCK
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
        ffmpeg.input("pipe:0", format="s16le", ar=samplerate, ac=channels)
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

    assert audio.tags is not None
    audio.tags.add(TIT2(encoding=3, text=title))
    if artist:
        audio.tags.add(TPE1(encoding=3, text=artist))
    if album:
        audio.tags.add(TALB(encoding=3, text=album))
    if genre:
        audio.tags.add(TCON(encoding=3, text=genre))
    audio.tags.add(TRCK(encoding=3, text=str(tracknumber)))

    audio.save()


def encode_flac(
    pcm_data: bytes,
    output_path: str,
    samplerate: int = 44100,
    channels: int = 1,
) -> str:
    """Encode raw PCM bytes to FLAC using ffmpeg-python.

    Returns output_path on success, raises ffmpeg.Error on failure.
    """
    (
        ffmpeg.input("pipe:0", format="s16le", ar=samplerate, ac=channels)
        .output(output_path, ar=samplerate, acodec="flac")
        .overwrite_output()
        .run(input=pcm_data, capture_stdout=True, capture_stderr=True)
    )
    return output_path


def add_flac_tags(
    filepath: str,
    title: str,
    artist: str = "",
    album: str = "",
    genre: str = "",
    tracknumber: int = 1,
) -> None:
    """Write Vorbis comment tags to a FLAC file using mutagen.flac.FLAC.

    Uses lowercase field names (TITLE, ARTIST, ALBUM, GENRE, TRACKNUMBER).
    """
    from mutagen.flac import FLAC

    audio = FLAC(filepath)

    audio["TITLE"] = title
    if artist:
        audio["ARTIST"] = artist
    if album:
        audio["ALBUM"] = album
    if genre:
        audio["GENRE"] = genre
    audio["TRACKNUMBER"] = str(tracknumber)

    audio.save()


def encode_m4a(
    pcm_data: bytes,
    output_path: str,
    samplerate: int = 44100,
    channels: int = 1,
) -> str:
    """Encode raw PCM bytes to M4A (ALAC) using ffmpeg-python.

    Returns output_path on success, raises ffmpeg.Error on failure.
    """
    (
        ffmpeg.input("pipe:0", format="s16le", ar=samplerate, ac=channels)
        .output(output_path, ar=samplerate, acodec="alac")
        .overwrite_output()
        .run(input=pcm_data, capture_stdout=True, capture_stderr=True)
    )
    return output_path


def add_m4a_tags(
    filepath: str,
    title: str,
    artist: str = "",
    album: str = "",
    genre: str = "",
    tracknumber: int = 1,
) -> None:
    """Write MP4/M4A tags using mutagen.mp4.MP4 frames.

    Uses Apple/MP4 tag keys (nam, ART, alb, day, gnr , trkn, disk).
    """
    from mutagen.mp4 import MP4

    audio = MP4(filepath)
    assert audio.tags is not None
    audio.tags["\xa9nam"] = [title]
    if artist:
        audio.tags["\xa9ART"] = [artist]
    if album:
        audio.tags["\xa9alb"] = [album]
    if genre:
        audio.tags["gnr "] = [genre]

    # tracknumber is a tuple of (current, total)
    audio.tags["trkn"] = [(tracknumber, 0)]

    audio.save()


def encode_ogg(
    pcm_data: bytes,
    output_path: str,
    samplerate: int = 44100,
    channels: int = 1,
) -> str:
    """Encode raw PCM bytes to OGG Vorbis using ffmpeg-python.

    Returns output_path on success, raises ffmpeg.Error on failure.
    """
    (
        ffmpeg.input("pipe:0", format="s16le", ar=samplerate, ac=channels)
        .output(output_path, ar=samplerate, acodec="libvorbis")
        .overwrite_output()
        .run(input=pcm_data, capture_stdout=True, capture_stderr=True)
    )
    return output_path


def add_ogg_tags(
    filepath: str,
    title: str,
    artist: str = "",
    album: str = "",
    genre: str = "",
    tracknumber: int = 1,
) -> None:
    """Write Vorbis comment tags to an OGG file using mutagen.oggvorbis.OggVorbis.

    Uses lowercase field names (TITLE, ARTIST, ALBUM, GENRE, TRACKNUMBER).
    """
    from mutagen.oggvorbis import OggVorbis

    audio = OggVorbis(filepath)

    audio["TITLE"] = title
    if artist:
        audio["ARTIST"] = artist
    if album:
        audio["ALBUM"] = album
    if genre:
        audio["GENRE"] = genre
    audio["TRACKNUMBER"] = str(tracknumber)

    audio.save()
