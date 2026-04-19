"""Tests for MP3 utilities (encoding and tagging)."""

from pathlib import Path

import pytest

from tests.utils import add_id3_tags, encode_mp3, tone_samples


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
        import ffmpeg

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
