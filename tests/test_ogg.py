"""Tests for OGG Vorbis utilities (encoding and tagging)."""

from pathlib import Path

import pytest

from tests.utils import add_ogg_tags, encode_ogg, tone_samples


class TestEncodeOGG:
    """Tests for encode_ogg function."""

    def test_file_created(self, tmp_path: Path) -> None:
        """Verify that encoding produces an OGG file at the output path."""
        pcm_data = tone_samples(freq=440, duration=1.0)
        output = tmp_path / "test.ogg"
        result = encode_ogg(pcm_data, str(output))
        assert result == str(output)
        assert output.exists()
        assert output.stat().st_size > 0

    def test_custom_sample_rate(self, tmp_path: Path) -> None:
        """Test encoding with different sample rate."""
        pcm_data = tone_samples(freq=440, duration=0.5, samplerate=22050)
        output = tmp_path / "test.ogg"
        encode_ogg(pcm_data, str(output), samplerate=22050)
        assert output.exists()

    def test_stereo(self, tmp_path: Path) -> None:
        """Test stereo encoding."""
        pcm_data = tone_samples(freq=440, duration=0.5)
        output = tmp_path / "stereo.ogg"
        encode_ogg(pcm_data, str(output), channels=2)
        assert output.exists()

    def test_invalid_pcm_raises_error(self) -> None:
        """Verify ffmpeg.Error is raised when giving clearly invalid PCM data."""
        import ffmpeg

        garbage = b"\xff\xfe" * 10
        output = "/tmp/a" + str(Path().resolve()) + "/_junk_invalid.ogg"
        with pytest.raises(ffmpeg.Error):
            encode_ogg(garbage, output)


class TestAddOggTags:
    """Tests for add_ogg_tags function."""

    def test_tags_written(self, tmp_path: Path) -> None:
        """Verify OGG tags appear in file metadata after writing."""
        output = tmp_path / "tagged.ogg"
        pcm_data = tone_samples(freq=440, duration=0.5)
        encode_ogg(pcm_data, str(output))

        add_ogg_tags(
            filepath=str(output),
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            genre="Classical",
            tracknumber=5,
        )

        from mutagen.oggvorbis import OggVorbis

        audio = OggVorbis(str(output))
        assert audio.tags is not None
        assert str(audio["TITLE"][0]) == "Test Song"
        assert str(audio["ARTIST"][0]) == "Test Artist"
        assert str(audio["ALBUM"][0]) == "Test Album"
        assert str(audio["GENRE"][0]) == "Classical"
        assert str(audio["TRACKNUMBER"][0]) == "5"

    def test_title_only(self, tmp_path: Path) -> None:
        """Verify only title tag is required, others are optional."""
        output = tmp_path / "title_only.ogg"
        pcm_data = tone_samples(freq=440, duration=0.5)
        encode_ogg(pcm_data, str(output))

        add_ogg_tags(filepath=str(output), title="Just Title")

        from mutagen.oggvorbis import OggVorbis

        audio = OggVorbis(str(output))
        assert audio.tags is not None
        assert str(audio["TITLE"][0]) == "Just Title"

    def test_tracknumber_default(self, tmp_path: Path) -> None:
        """Verify default tracknumber of 1 is written."""
        output = tmp_path / "default_track.ogg"
        pcm_data = tone_samples(freq=440, duration=0.5)
        encode_ogg(pcm_data, str(output))

        add_ogg_tags(filepath=str(output), title="Test")

        from mutagen.oggvorbis import OggVorbis

        audio = OggVorbis(str(output))
        assert audio.tags is not None
        assert str(audio["TRACKNUMBER"][0]) == "1"
