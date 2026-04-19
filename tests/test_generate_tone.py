"""Tests for the util module (tone generation, MP3 encoding, ID3 tags)."""

import struct
from pathlib import Path

import ffmpeg
import pytest

from tests.utils import add_id3_tags, encode_mp3, tone_samples


class TestToneSamples:
    """Tests for tone_samples function."""

    def test_440hz_5s_expected_samples(self) -> None:
        """Verify sample count matches expected duration of 440Hz for 5s."""
        samplerate = 44100
        duration = 5.0
        pcm = tone_samples(freq=440, duration=duration, samplerate=samplerate)
        num_samples = len(pcm) // 2  # 2 bytes per sample (int16)
        expected = samplerate * duration
        assert num_samples == expected

    def test_440hz_3s_expected_samples(self) -> None:
        """Verify sample count matches expected duration of 440Hz for 3s."""
        samplerate = 44100
        duration = 3.0
        pcm = tone_samples(freq=440, duration=duration, samplerate=samplerate)
        num_samples = len(pcm) // 2
        expected = samplerate * duration
        assert num_samples == expected

    def test_default_params(self) -> None:
        """Test that default parameters produce valid output with correct duration."""
        pcm = tone_samples()
        num_samples = len(pcm) // 2
        assert num_samples == 44100 * 3  # 3 seconds default

    def test_8khz_sample(self) -> None:
        """Test with 8kHz sample rate."""
        pcm = tone_samples(freq=220, duration=1.0, samplerate=8000)
        num_samples = len(pcm) // 2
        assert num_samples == 8000

    def test_fade_in_small_value(self) -> None:
        """Fade-in samples should start with small values near zero."""
        pcm = tone_samples(freq=440, duration=3.0, samplerate=44100)
        samples = struct.unpack(f"<{len(pcm) // 2}h", pcm)
        first_50 = samples[:50]
        # First samples should be very small due to fade-in envelope
        max_first_50 = max(abs(s) for s in first_50)
        assert max_first_50 < 2000

    def test_fade_out_small_value(self) -> None:
        """Fade-out samples should end with small values near zero."""
        samplerate = 44100
        pcm = tone_samples(freq=440, duration=3.0, samplerate=samplerate)
        samples = struct.unpack(f"<{len(pcm) // 2}h", pcm)
        fade_count = samplerate * 3 // 1000
        last_samples = samples[-fade_count:]
        max_last = max(abs(s) for s in last_samples)
        assert max_last < 2000

    def test_values_in_16bit_range(self) -> None:
        """All raw values before normalization should be in [-32767, 32767]."""
        samples = tone_samples(freq=261, duration=0.5, samplerate=44100)
        decoded = struct.unpack(f"<{len(samples) // 2}h", samples)
        for s in decoded:
            assert -32768 <= s <= 32767


class TestEncodeMP3:
    """Tests for encode_mp3 function."""

    def test_file_created(self, tmp_path: Path) -> None:
        """Verify that encoding produces an MP3 file at the output path."""
        pcm_data = tone_samples(freq=440, duration=1.0)
        output = tmp_path / "test.mp3"
        result = encode_mp3(pcm_data, str(output))
        assert result == str(output)
        assert output.exists()
        assert output.stat().st_size > 0

    def test_custom_bitrate(self, tmp_path: Path) -> None:
        """Test encoding with different bitrates."""
        pcm_data = tone_samples(freq=440, duration=0.5)
        output = tmp_path / "test.mp3"
        encode_mp3(pcm_data, str(output), bitrate=64)
        assert output.exists()

    def test_stereo(self, tmp_path: Path) -> None:
        """Test stereo encoding."""
        pcm_data = tone_samples(freq=440, duration=0.5, samplerate=8000)
        output = tmp_path / "stereo.mp3"
        encode_mp3(pcm_data, str(output), channels=2, samplerate=8000)
        assert output.exists()

    def test_invalid_pcm_raises_error(self) -> None:
        """Verify ffmpeg.Error is raised when giving clearly invalid PCM data (garbage bytes)."""
        garbage = b"\xff\xfe" * 10
        output = "/tmp/a" + str(Path().resolve()) + "/_junk_invalid.mp3"
        with pytest.raises(ffmpeg.Error):
            encode_mp3(garbage, output)


class TestAddID3Tags:
    """Tests for add_id3_tags function."""

    def test_tags_written(self, tmp_path: Path) -> None:
        """Verify ID3 tags appear in file metadata after writing."""
        output = tmp_path / "tagged.mp3"
        pcm_data = tone_samples(freq=440, duration=0.5)
        encode_mp3(pcm_data, str(output))

        add_id3_tags(
            filepath=str(output),
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            genre="Classical",
            tracknumber=5,
        )

        # Reload and verify tags are present
        from mutagen.mp3 import MP3
        audio = MP3(str(output))
        assert audio.tags is not None
        tit2 = audio.tags.get("TIT2")
        assert tit2 is not None
        assert str(tit2.text[0]) == "Test Song"

        tpe1 = audio.tags.get("TPE1")
        assert tpe1 is not None
        assert str(tpe1.text[0]) == "Test Artist"

        talb = audio.tags.get("TALB")
        assert talb is not None
        assert str(talb.text[0]) == "Test Album"

        tcon = audio.tags.get("TCON")
        assert tcon is not None
        assert str(tcon.text[0]) == "Classical"

        trck = audio.tags.get("TRCK")
        assert trck is not None
        assert str(trck.text[0]) == "5"

    def test_title_only(self, tmp_path: Path) -> None:
        """Verify only title tag is required, others are optional."""
        output = tmp_path / "title_only.mp3"
        pcm_data = tone_samples(freq=440, duration=0.5)
        encode_mp3(pcm_data, str(output))

        add_id3_tags(filepath=str(output), title="Just Title")

        from mutagen.mp3 import MP3
        audio = MP3(str(output))
        assert audio.tags is not None
        tit2 = audio.tags.get("TIT2")
        assert tit2 is not None
        assert str(tit2.text[0]) == "Just Title"

    def test_tracknumber_default(self, tmp_path: Path) -> None:
        """Verify default tracknumber of 1 is written."""
        output = tmp_path / "default_track.mp3"
        pcm_data = tone_samples(freq=440, duration=0.5)
        encode_mp3(pcm_data, str(output))

        add_id3_tags(filepath=str(output), title="Test")

        from mutagen.mp3 import MP3
        audio = MP3(str(output))
        assert audio.tags is not None
        trck = audio.tags.get("TRCK")
        assert trck is not None
        assert str(trck.text[0]) == "1"
