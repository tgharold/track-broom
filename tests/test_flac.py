"""Tests for FLAC utilities (encoding and tagging)."""

from pathlib import Path

import pytest

from tests.utils import add_flac_tags, encode_flac, tone_samples


class TestEncodeFLAC:
    """Tests for encode_flac function."""

    def test_file_created(self, tmp_path: Path) -> None:
        """Verify that encoding produces a FLAC file at the output path."""
        pcm_data = tone_samples(freq=440, duration=1.0)
        output = tmp_path / "test.flac"
        result = encode_flac(pcm_data, str(output))
        assert result == str(output)
        assert output.exists()
        assert output.stat().st_size > 0

    def test_custom_sample_rate(self, tmp_path: Path) -> None:
        """Test encoding with different sample rate."""
        pcm_data = tone_samples(freq=440, duration=0.5, samplerate=22050)
        output = tmp_path / "test.flac"
        encode_flac(pcm_data, str(output), samplerate=22050)
        assert output.exists()

    def test_stereo(self, tmp_path: Path) -> None:
        """Test stereo encoding."""
        pcm_data = tone_samples(freq=440, duration=0.5)
        output = tmp_path / "stereo.flac"
        encode_flac(pcm_data, str(output), channels=2)
        assert output.exists()

    def test_invalid_pcm_raises_error(self) -> None:
        """Verify ffmpeg.Error is raised when giving clearly invalid PCM data."""
        import ffmpeg

        garbage = b"\xff\xfe" * 10
        output = "/tmp/a" + str(Path().resolve()) + "/_junk_invalid.flac"
        with pytest.raises(ffmpeg.Error):
            encode_flac(garbage, output)


class TestAddFlacTags:
    """Tests for add_flac_tags function."""

    def test_tags_written(self, tmp_path: Path) -> None:
        """Verify FLAC tags appear in file metadata after writing."""
        output = tmp_path / "tagged.flac"
        pcm_data = tone_samples(freq=440, duration=0.5)
        encode_flac(pcm_data, str(output))

        add_flac_tags(
            filepath=str(output),
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            genre="Classical",
            tracknumber=5,
        )

        from mutagen.flac import FLAC

        audio = FLAC(str(output))
        assert audio.tags is not None
        assert str(audio["TITLE"][0]) == "Test Song"
        assert str(audio["ARTIST"][0]) == "Test Artist"
        assert str(audio["ALBUM"][0]) == "Test Album"
        assert str(audio["GENRE"][0]) == "Classical"
        assert str(audio["TRACKNUMBER"][0]) == "5"

    def test_title_only(self, tmp_path: Path) -> None:
        """Verify only title tag is required, others are optional."""
        output = tmp_path / "title_only.flac"
        pcm_data = tone_samples(freq=440, duration=0.5)
        encode_flac(pcm_data, str(output))

        add_flac_tags(filepath=str(output), title="Just Title")

        from mutagen.flac import FLAC

        audio = FLAC(str(output))
        assert audio.tags is not None
        assert str(audio["TITLE"][0]) == "Just Title"

    def test_tracknumber_default(self, tmp_path: Path) -> None:
        """Verify default tracknumber of 1 is written."""
        output = tmp_path / "default_track.flac"
        pcm_data = tone_samples(freq=440, duration=0.5)
        encode_flac(pcm_data, str(output))

        add_flac_tags(filepath=str(output), title="Test")

        from mutagen.flac import FLAC

        audio = FLAC(str(output))
        assert audio.tags is not None
        assert str(audio["TRACKNUMBER"][0]) == "1"
