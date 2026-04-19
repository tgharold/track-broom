"""Tests for M4A utilities (encoding and tagging)."""

from pathlib import Path

import ffmpeg
import pytest

from tests.utils import add_m4a_tags, encode_m4a, tone_samples


class TestEncodeM4a:
    """Tests for encode_m4a function."""

    def test_file_created(self, tmp_path: Path) -> None:
        """Verify that encoding produces an M4A file at the output path."""
        pcm_data = tone_samples(freq=440, duration=1.0)
        output = tmp_path / "test.m4a"
        result = encode_m4a(pcm_data, str(output))
        assert result == str(output)
        assert output.exists()
        assert output.stat().st_size > 0

    def test_custom_sample_rate(self, tmp_path: Path) -> None:
        """Test encoding with different sample rate."""
        pcm_data = tone_samples(freq=440, duration=0.5, samplerate=22050)
        output = tmp_path / "test.m4a"
        encode_m4a(pcm_data, str(output), samplerate=22050)
        assert output.exists()

    def test_stereo(self, tmp_path: Path) -> None:
        """Test stereo encoding."""
        pcm_data = tone_samples(freq=440, duration=0.5)
        output = tmp_path / "stereo.m4a"
        encode_m4a(pcm_data, str(output), channels=2)
        assert output.exists()

    def test_invalid_pcm_raises_error(self) -> None:
        """Verify ffmpeg.Error is raised when giving clearly invalid PCM data."""
        garbage = b"\xff\xfe" * 10
        output = "/tmp/a" + str(Path().resolve()) + "/_junk_invalid.m4a"
        with pytest.raises(ffmpeg.Error):
            encode_m4a(garbage, output)


class TestAddM4aTags:
    """Tests for add_m4a_tags function."""

    def test_tags_written(self, tmp_path: Path) -> None:
        """Verify M4A tags appear in file metadata after writing."""
        output = tmp_path / "tagged.m4a"
        pcm_data = tone_samples(freq=440, duration=0.5)
        encode_m4a(pcm_data, str(output))

        add_m4a_tags(
            filepath=str(output),
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            genre="Classical",
            tracknumber=5,
        )

        from mutagen.mp4 import MP4

        audio = MP4(str(output))
        assert audio.tags is not None
        assert str(audio.tags["\xa9nam"][0]) == "Test Song"
        assert str(audio.tags["\xa9ART"][0]) == "Test Artist"
        assert str(audio.tags["\xa9alb"][0]) == "Test Album"
        assert str(audio.tags["gnr "][0]) == "Classical"
        track = audio.tags["trkn"][0]
        assert track[0] == 5

    def test_title_only(self, tmp_path: Path) -> None:
        """Verify only title tag is required, others are optional."""
        output = tmp_path / "title_only.m4a"
        pcm_data = tone_samples(freq=440, duration=0.5)
        encode_m4a(pcm_data, str(output))

        add_m4a_tags(filepath=str(output), title="Just Title")

        from mutagen.mp4 import MP4

        audio = MP4(str(output))
        assert audio.tags is not None
        assert str(audio.tags["\xa9nam"][0]) == "Just Title"

    def test_tracknumber_default(self, tmp_path: Path) -> None:
        """Verify default tracknumber of 1 is written."""
        output = tmp_path / "default_track.m4a"
        pcm_data = tone_samples(freq=440, duration=0.5)
        encode_m4a(pcm_data, str(output))

        add_m4a_tags(filepath=str(output), title="Test")

        from mutagen.mp4 import MP4

        audio = MP4(str(output))
        assert audio.tags is not None
        track = audio.tags["trkn"][0]
        assert track[0] == 1
