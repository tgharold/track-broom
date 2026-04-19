"""Tests for WMA utilities (encoding and tagging)."""

from pathlib import Path

import ffmpeg
import pytest

from tests.utils import add_wma_tags, encode_wma, tone_samples


class TestEncodeWMA:
    """Tests for encode_wma function."""

    def test_file_created(self, tmp_path: Path) -> None:
        """Verify that encoding produces a WMA file at the output path."""
        pcm_data = tone_samples(freq=440, duration=1.0)
        output = tmp_path / "test.wma"
        result = encode_wma(pcm_data, str(output))
        assert result == str(output)
        assert output.exists()
        assert output.stat().st_size > 0

    def test_custom_sample_rate(self, tmp_path: Path) -> None:
        """Test encoding with different sample rate."""
        pcm_data = tone_samples(freq=440, duration=0.5, samplerate=22050)
        output = tmp_path / "test.wma"
        encode_wma(pcm_data, str(output), samplerate=22050)
        assert output.exists()

    def test_stereo(self, tmp_path: Path) -> None:
        """Test stereo encoding."""
        pcm_data = tone_samples(freq=440, duration=0.5)
        output = tmp_path / "stereo.wma"
        encode_wma(pcm_data, str(output), channels=2)
        assert output.exists()

    def test_invalid_pcm_raises_error(self) -> None:
        """Verify ffmpeg.Error is raised when giving clearly invalid PCM data."""
        garbage = b"\xff\xfe" * 10
        output = "/tmp/a" + str(Path().resolve()) + "/_junk_invalid.wma"
        with pytest.raises(ffmpeg.Error):
            encode_wma(garbage, output)


class TestAddWmaTags:
    """Tests for add_wma_tags function."""

    def test_tags_written(self, tmp_path: Path) -> None:
        """Verify WMA tags appear in file metadata after writing."""
        output = tmp_path / "tagged.wma"
        pcm_data = tone_samples(freq=440, duration=0.5)
        encode_wma(pcm_data, str(output))

        add_wma_tags(
            filepath=str(output),
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            genre="Classical",
            tracknumber=5,
        )

        from mutagen.asf import ASF

        audio = ASF(str(output))
        assert audio.tags is not None
        assert audio["Title"][0] == "Test Song"
        assert audio["Author"][0] == "Test Artist"
        assert audio["WM/AlbumName"][0] == "Test Album"
        assert audio["WM/Genre"][0] == "Classical"
        assert audio["WM/TrackNumber"][0] == "5"

    def test_title_only(self, tmp_path: Path) -> None:
        """Verify only title tag is required, others are optional."""
        output = tmp_path / "title_only.wma"
        pcm_data = tone_samples(freq=440, duration=0.5)
        encode_wma(pcm_data, str(output))

        add_wma_tags(filepath=str(output), title="Just Title")

        from mutagen.asf import ASF

        audio = ASF(str(output))
        assert audio.tags is not None
        assert audio["Title"][0] == "Just Title"

    def test_tracknumber_default(self, tmp_path: Path) -> None:
        """Verify default tracknumber of 1 is written."""
        output = tmp_path / "default_track.wma"
        pcm_data = tone_samples(freq=440, duration=0.5)
        encode_wma(pcm_data, str(output))

        add_wma_tags(filepath=str(output), title="Test")

        from mutagen.asf import ASF

        audio = ASF(str(output))
        assert audio.tags is not None
        assert audio["WM/TrackNumber"][0] == "1"
