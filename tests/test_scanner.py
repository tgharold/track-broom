"""Tests for the scanner module."""

from pathlib import Path

import pytest

from tests.utils import add_m4a_tags, encode_m4a, tone_samples
from track_broom.scanner import list_files


@pytest.fixture
def sample_dir(tmp_path: Path) -> Path:
    """Create a directory with various nested files for testing."""
    # Top-level files
    (tmp_path / "song1.mp3").touch()
    (tmp_path / "song2.flac").touch()
    (tmp_path / "readme.txt").touch()
    (tmp_path / "cover.jpg").touch()

    # Nested directory
    sub1 = tmp_path / "album1"
    sub1.mkdir()
    (sub1 / "track01.mp3").touch()
    (sub1 / "track02.mp3").touch()
    (sub1 / "notes.md").touch()

    # Deeper nesting — real M4A file (not .touch())
    sub2 = sub1 / "bonus"
    sub2.mkdir()
    pcm_data = tone_samples(freq=440, duration=0.5)
    m4a_path = sub2 / "hidden.m4a"
    encode_m4a(pcm_data, str(m4a_path))
    add_m4a_tags(str(m4a_path), title="Hidden Track")

    # Empty directory
    (tmp_path / "empty_album").mkdir()

    return tmp_path


class TestListFiles:
    """Tests for list_files function."""

    def test_list_all_files(self, sample_dir: Path) -> None:
        """Test that list_files returns all files in a directory recursively."""
        result = list(list_files(sample_dir))
        assert len(result) == 8

    def test_all_extension_types_present(self, sample_dir: Path) -> None:
        """Test that all file extension types are captured."""
        result = list(list_files(sample_dir))
        extensions = {ext for _, ext in result}
        assert extensions == {"mp3", "flac", "txt", "jpg", "md", "m4a"}

    def test_correct_path_extension_pairs(self, sample_dir: Path) -> None:
        """Test that files are correctly paired with their extensions."""
        result = list(list_files(sample_dir))
        expected = [
            (sample_dir / "album1" / "bonus" / "hidden.m4a", "m4a"),
            (sample_dir / "album1" / "notes.md", "md"),
            (sample_dir / "album1" / "track01.mp3", "mp3"),
            (sample_dir / "album1" / "track02.mp3", "mp3"),
            (sample_dir / "cover.jpg", "jpg"),
            (sample_dir / "readme.txt", "txt"),
            (sample_dir / "song1.mp3", "mp3"),
            (sample_dir / "song2.flac", "flac"),
        ]
        assert result == expected

    def test_filter_by_extension(self, sample_dir: Path) -> None:
        """Test filtering to only MP3 files."""
        result = list(list_files(sample_dir, extension="mp3"))
        assert len(result) == 3
        assert all(ext == "mp3" for _, ext in result)

    def test_filter_by_extension_with_dot(self, sample_dir: Path) -> None:
        """Test filtering with a dot prefix in extension doesn't add leading dot."""
        result = list(list_files(sample_dir, extension=".flac"))
        assert len(result) == 1
        assert result[0][0] == sample_dir / "song2.flac"
        assert result[0][1] == "flac"

    def test_filter_by_nonexistent_extension(self, sample_dir: Path) -> None:
        """Test filtering to a non-existent extension returns empty."""
        result = list(list_files(sample_dir, extension="zip"))
        assert result == []

    def test_empty_directory(self, tmp_path: Path) -> None:
        """Test that an empty directory yields no files."""
        (tmp_path / "empty").mkdir()
        result = list(list_files(tmp_path / "empty"))
        assert result == []

    def test_single_file_no_extension(self, tmp_path: Path) -> None:
        """Test listing a single file with no extension."""
        file_path = tmp_path / "noextension"
        file_path.touch()
        result = list(list_files(file_path))
        assert len(result) == 1
        assert result[0] == (file_path, "")

    def test_single_file_with_extension(self, tmp_path: Path) -> None:
        """Test listing a single file with extension."""
        file_path = tmp_path / "song.mp3"
        file_path.touch()
        result = list(list_files(file_path))
        assert len(result) == 1
        assert result[0] == (file_path, "mp3")

    def test_single_file_filtered_match(self, tmp_path: Path) -> None:
        """Test filtering a single file where extension matches."""
        file_path = tmp_path / "song.mp3"
        file_path.touch()
        result = list(list_files(file_path, extension="mp3"))
        assert len(result) == 1

    def test_single_file_filtered_no_match(self, tmp_path: Path) -> None:
        """Test filtering a single file where extension doesn't match."""
        file_path = tmp_path / "song.mp3"
        file_path.touch()
        result = list(list_files(file_path, extension="flac"))
        assert result == []

    def test_results_are_sorted(self, sample_dir: Path) -> None:
        """Test that results are sorted lexicographically."""
        result = list(list_files(sample_dir))
        paths = [path for path, _ in result]
        assert paths == sorted(paths)

    def test_recursive_finds_deep_files(self, sample_dir: Path) -> None:
        """Test that deeply nested files are found."""
        result = list(list_files(sample_dir))
        deep_file = sample_dir / "album1" / "bonus" / "hidden.m4a"
        assert (deep_file, "m4a") in result

    def test_skips_directories_in_results(self, sample_dir: Path) -> None:
        """Test that subdirectories themselves don't appear in results."""
        result = list(list_files(sample_dir))
        dir_path = sample_dir / "album1" / "bonus"
        for file_path, _ in result:
            assert file_path != dir_path
