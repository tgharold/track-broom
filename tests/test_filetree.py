"""Tests for the filetree module."""

import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

from track_broom.filetree import (
    FileSystemDirectoryEntry,
    FileSystemFileEntry,
)


@pytest.fixture
def hier_tmp_path(tmp_path: Path) -> Path:
    """Create a multi-level directory structure for reuse in tests.

    Structure::

        /tmp_path
            loose-song1.mp3
            loose-song2.m4a
            Seasons_artist/
                album1_spring/
                    track-rainy-day-01.mp3
                    track-night-02.mp3
                    track-before-the-dawn-03.mp3
                album2_fall/
                    track-fall-01.mp3
                    track-fall-02.mp3
            Artist_formerly_known_as_Jester/
                Colors/
                    purple-01.mp3
                    rain-02.mp3
                    bonus/
                        hidden_colors.ogg
    """
    (tmp_path / "loose-song1.mp3").touch()
    (tmp_path / "loose-song2.m4a").touch()

    seasons = tmp_path / "Seasons_artist"
    seasons.mkdir()
    album1 = seasons / "album1_spring"
    album1.mkdir()
    (album1 / "track-rainy-day-01.mp3").touch()
    (album1 / "track-night-02.mp3").touch()
    (album1 / "track-before-the-dawn-03.mp3").touch()
    album2 = seasons / "album2_fall"
    album2.mkdir()
    (album2 / "track-fall-01.mp3").touch()
    (album2 / "track-fall-02.mp3").touch()

    jester = tmp_path / "Artist_formerly_known_as_Jester"
    jester.mkdir()
    colors = jester / "Colors"
    colors.mkdir()
    (colors / "purple-01.mp3").touch()
    (colors / "rain-02.mp3").touch()
    bonus = colors / "bonus"
    bonus.mkdir()
    (bonus / "hidden_colors.ogg").touch()

    return tmp_path


# ---- FileSystemEntry base class ----


class TestFileSystemEntry:
    """Tests for the base FileSystemEntry class."""

    def test_name_from_path(self, tmp_path: Path) -> None:
        file_path = tmp_path / "mymusic.mp3"
        file_path.touch()
        entry = FileSystemFileEntry(file_path)
        assert entry.name == "mymusic.mp3"

    def test_name_from_path_no_extension(self, tmp_path: Path) -> None:
        file_path = tmp_path / "nobasename"
        file_path.touch()
        entry = FileSystemFileEntry(file_path)
        assert entry.name == "nobasename"

    def test_path_returns_full_path(self, tmp_path: Path) -> None:
        file_path = tmp_path / "subdir" / "file.mp3"
        file_path.parent.mkdir(parents=True)
        file_path.touch()
        entry = FileSystemFileEntry(file_path)
        assert entry.path == file_path

    def test_size_returns_file_size(self, tmp_path: Path) -> None:
        with tempfile.NamedTemporaryFile(dir=str(tmp_path), delete=False) as f:
            f.write(b"hello")
            f.flush()
            expected_size = f.tell()

        entry = FileSystemFileEntry(Path(f.name))
        assert entry.size == expected_size

    def test_size_is_zero_for_empty_file(self, tmp_path: Path) -> None:
        file_path = tmp_path / "empty.txt"
        file_path.touch()
        entry = FileSystemFileEntry(file_path)
        assert entry.size == 0

    def test_last_modified_returns_utc_datetime(self, tmp_path: Path) -> None:
        file_path = tmp_path / "file.dat"
        file_path.touch()
        entry = FileSystemFileEntry(file_path)
        assert isinstance(entry.last_modified, datetime)
        assert entry.last_modified.tzinfo is UTC

    def test_last_modified_is_recent(self, tmp_path: Path) -> None:
        file_path = tmp_path / "file.dat"
        file_path.touch()
        entry = FileSystemFileEntry(file_path)
        now = datetime.now(UTC)
        before = now.replace(year=2000)
        after = now.replace(year=2100)
        assert before <= entry.last_modified <= after

    def test_repr_file(self, tmp_path: Path) -> None:
        file_path = tmp_path / "test.mp3"
        file_path.touch()
        entry = FileSystemFileEntry(file_path)
        assert repr(entry) == "FileSystemFileEntry(name='test.mp3', size=0)"

    def test_repr_directory(self, tmp_path: Path) -> None:
        dir_path = tmp_path / "mydir"
        dir_path.mkdir()
        entry = FileSystemDirectoryEntry(dir_path)
        assert entry.name == "mydir"
        assert entry.size > 0
        assert "FileSystemDirectoryEntry" in repr(entry)


class TestFileSystemEntryParent:
    """Tests for the parent property."""

    def test_root_entry_has_no_parent(self, tmp_path: Path) -> None:
        file_path = tmp_path / "root.mp3"
        file_path.touch()
        entry = FileSystemFileEntry(file_path)
        assert entry.parent is None

        file_path2 = tmp_path / "root2.mp3"
        file_path2.touch()
        entry2 = FileSystemFileEntry(file_path2)
        assert entry2.parent is None

    def test_nested_file_has_correct_parent(self, tmp_path: Path) -> None:
        subdir = tmp_path / "sub"
        subdir.mkdir()
        file_path = subdir / "music.mp3"
        file_path.touch()
        parent_dir = FileSystemDirectoryEntry(subdir)
        entry = FileSystemFileEntry(file_path, parent=parent_dir)
        assert entry.parent is parent_dir
        assert entry.parent is not None and entry.parent.name == "sub"

    def test_directory_has_correct_parent(self, tmp_path: Path) -> None:
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        subdir = base_dir / "child_dir"
        subdir.mkdir()
        parent = FileSystemDirectoryEntry(base_dir)
        entry = FileSystemDirectoryEntry(subdir, parent=parent)
        assert entry.parent is parent
        assert entry.parent is not None and entry.parent.name == "base"


# ---- FileSystemFileEntry ----


class TestFileSystemFileEntry:
    """Tests for the FileSystemFileEntry class."""

    def test_extension_with_dot(self, tmp_path: Path) -> None:
        file_path = tmp_path / "song.mp3"
        file_path.touch()
        entry = FileSystemFileEntry(file_path)
        assert entry.extension == ".mp3"

    def test_extension_lowercase(self, tmp_path: Path) -> None:
        file_path = tmp_path / "song.MP3"
        file_path.touch()
        entry = FileSystemFileEntry(file_path)
        assert entry.extension == ".mp3"

    def test_extension_various_formats(self, tmp_path: Path) -> None:
        formats = [".MP3", ".Flac", ".M4A", ".ogg", ".WMA", ".wav", ".AAC", ".mka"]
        for fmt in formats:
            file_path = tmp_path / f"file{fmt.lower()}"
            file_path.touch()
            entry = FileSystemFileEntry(file_path)
            assert entry.extension == fmt.lower()

    def test_extension_no_dot(self, tmp_path: Path) -> None:
        file_path = tmp_path / "file.mp3"
        file_path.touch()
        entry = FileSystemFileEntry(file_path)
        assert entry.extension == ".mp3"

    def test_extension_no_extension(self, tmp_path: Path) -> None:
        file_path = tmp_path / "noextension"
        file_path.touch()
        entry = FileSystemFileEntry(file_path)
        assert entry.extension == ""

    def test_extension_single_letter(self, tmp_path: Path) -> None:
        file_path = tmp_path / "file.m"
        file_path.touch()
        entry = FileSystemFileEntry(file_path)
        assert entry.extension == ".m"

    def test_extension_multiple_dots(self, tmp_path: Path) -> None:
        file_path = tmp_path / "file.name.mp3"
        file_path.touch()
        entry = FileSystemFileEntry(file_path)
        assert entry.extension == ".mp3"


# ---- FileSystemDirectoryEntry ----


class TestFileSystemDirectoryEntry:
    """Tests for the FileSystemDirectoryEntry class."""

    def test_entries_returns_all_children(self, tmp_path: Path) -> None:
        (tmp_path / "dir1").mkdir()
        (tmp_path / "file1.mp3").touch()
        (tmp_path / "file2.flac").touch()

        entry = FileSystemDirectoryEntry(tmp_path)
        children = entry.entries()
        assert len(children) == 3

        dirs = [c for c in children if isinstance(c, FileSystemDirectoryEntry)]
        files = [c for c in children if isinstance(c, FileSystemFileEntry)]
        assert len(dirs) == 1
        assert len(files) == 2

    def test_entries_returns_nested_files(self, tmp_path: Path) -> None:
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.mp3").touch()

        entry = FileSystemDirectoryEntry(tmp_path)
        children = entry.entries()
        names = {c.name for c in children}
        assert names == {"subdir"}

        subdir_entry = [c for c in children if c.name == "subdir"][0]
        assert isinstance(subdir_entry, FileSystemDirectoryEntry)
        nested_children = subdir_entry.entries()
        assert len(nested_children) == 1
        assert nested_children[0].name == "nested.mp3"

    def test_entries_child_parent_pointers(self, tmp_path: Path) -> None:
        (tmp_path / "file1.mp3").touch()
        (tmp_path / "subdir").mkdir()

        parent = FileSystemDirectoryEntry(tmp_path)
        children = parent.entries()
        for child in children:
            assert child.parent is parent

    def test_entries_empty_directory(self, tmp_path: Path) -> None:
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        entry = FileSystemDirectoryEntry(empty_dir)
        children = entry.entries()
        assert children == []

    def test_entries_includes_hidden_files(self, tmp_path: Path) -> None:
        (tmp_path / ".hidden").touch()
        (tmp_path / "visible.mp3").touch()

        entry = FileSystemDirectoryEntry(tmp_path)
        children = entry.entries()
        child_names = {c.name for c in children}
        assert ".hidden" in child_names
        assert "visible.mp3" in child_names

    def test_children_returns_only_files(self, tmp_path: Path) -> None:
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir2").mkdir()
        (tmp_path / "file1.mp3").touch()

        entry = FileSystemDirectoryEntry(tmp_path)
        children = entry.file_children()
        assert len(children) == 1
        assert isinstance(children[0], FileSystemFileEntry)
        assert children[0].name == "file1.mp3"

    def test_children_empty_directory(self, tmp_path: Path) -> None:
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        entry = FileSystemDirectoryEntry(empty_dir)
        assert entry.file_children() == []

    def test_children_excludes_subdirectories(self, tmp_path: Path) -> None:
        (tmp_path / "subdir").mkdir()
        (tmp_path / "file1.mp3").touch()
        (tmp_path / "file2.flac").touch()

        entry = FileSystemDirectoryEntry(tmp_path)
        children = entry.file_children()
        assert len(children) == 2
        for child in children:
            assert isinstance(child, FileSystemFileEntry)

    def test_children_includes_all_file_types(self, tmp_path: Path) -> None:
        (tmp_path / "song.mp3").touch()
        (tmp_path / "track.flac").touch()
        (tmp_path / "midi.mka").touch()
        (tmp_path / "nobinary").touch()

        entry = FileSystemDirectoryEntry(tmp_path)
        children = entry.file_children()
        assert len(children) == 4
        names = {c.name for c in children}
        assert names == {"song.mp3", "track.flac", "midi.mka", "nobinary"}


# ---- Integration / mixed scenarios ----


class TestFileTreeIntegration:
    """Integration tests combining multiple entry types."""

    def test_hierarchical_tree(self, hier_tmp_path: Path) -> None:
        """Test a multi-level directory structure."""
        root = FileSystemDirectoryEntry(hier_tmp_path)

        top_children = root.entries()
        # loose-song1.mp3, loose-song2.m4a, Seasons_artist/, Artist_formerly_known_as_Jester/
        assert len(top_children) == 4
        assert len(top_children) == 4
        assert len(top_children) == 4
        assert len(top_children) == 4
        assert len(top_children) == 4
        assert root.name == hier_tmp_path.name

        seasons_entry = [c for c in top_children if c.name == "Seasons_artist"][0]
        assert isinstance(seasons_entry, FileSystemDirectoryEntry)
        assert seasons_entry.parent is root

        seasons_children = seasons_entry.entries()
        assert len(seasons_children) == 2  # album1_spring/, album2_fall/

        album1_entry = [c for c in seasons_children if c.name == "album1_spring"][0]
        assert isinstance(album1_entry, FileSystemDirectoryEntry)
        assert album1_entry.parent is seasons_entry

        album1_children = album1_entry.entries()
        # track-rainy-day-01.mp3, track-night-02.mp3, track-before-the-dawn-03.mp3
        assert len(album1_children) == 3
        album1_names = {c.name for c in album1_children}
        expected = {"track-rainy-day-01.mp3", "track-night-02.mp3", "track-before-the-dawn-03.mp3"}
        assert album1_names == expected

        album2_entry = [c for c in seasons_children if c.name == "album2_fall"][0]
        assert isinstance(album2_entry, FileSystemDirectoryEntry)
        assert album2_entry.parent is seasons_entry

        album2_children = album2_entry.entries()
        assert len(album2_children) == 2  # track-fall-01.mp3, track-fall-02.mp3

        jester_entry = [c for c in top_children if c.name == "Artist_formerly_known_as_Jester"][0]
        assert isinstance(jester_entry, FileSystemDirectoryEntry)
        assert jester_entry.parent is root

        jester_children = jester_entry.entries()
        assert len(jester_children) == 1  # Colors/

        colors_entry = [c for c in jester_children if c.name == "Colors"][0]
        assert isinstance(colors_entry, FileSystemDirectoryEntry)
        assert colors_entry.parent is jester_entry

        colors_children = colors_entry.entries()
        assert len(colors_children) == 3  # purple-01.mp3, rain-02.mp3, bonus/

        bonus_entry = [c for c in colors_children if c.name == "bonus"][0]
        assert isinstance(bonus_entry, FileSystemDirectoryEntry)
        assert bonus_entry.parent is colors_entry

        bonus_children = bonus_entry.entries()
        assert len(bonus_children) == 1
        assert bonus_children[0].name == "hidden_colors.ogg"
        assert bonus_children[0].parent is bonus_entry

    def test_file_size_reflects_actual_content(self, tmp_path: Path) -> None:
        with tempfile.NamedTemporaryFile(
            dir=str(tmp_path), mode="w", delete=False
        ) as f:
            f.write("A" * 500)
            content_path = Path(f.name)

        entry = FileSystemFileEntry(content_path)
        assert entry.size == 500

    def test_entry_inherits_parent_name_via_parent(self, tmp_path: Path) -> None:
        subdir = tmp_path / "parent_dir"
        subdir.mkdir()
        file_path = subdir / "song.mp3"
        file_path.touch()

        parent = FileSystemDirectoryEntry(subdir)
        file_entry = FileSystemFileEntry(file_path, parent=parent)

        assert file_entry.parent is not None and file_entry.parent.name == "parent_dir"

    def test_multiple_files_same_directory(self, tmp_path: Path) -> None:
        files = [f"track{i:02d}.mp3" for i in range(10)]
        for name in files:
            (tmp_path / name).touch()

        entry = FileSystemDirectoryEntry(tmp_path)
        children = entry.file_children()
        assert len(children) == 10
        names = {c.name for c in children}
        assert names == set(files)

    def test_deeply_nested_structure(self, tmp_path: Path) -> None:
        """Test 6 levels deep: root > level0 > ... > level4 > file."""
        current = tmp_path
        for i in range(5):
            sub = current / f"level{i}"
            sub.mkdir()
            current = sub

        (current / "deepest.mp3").touch()

        root = FileSystemDirectoryEntry(tmp_path)

        def find_deepest(e, depth=0):
            if depth == 6:
                assert isinstance(e, FileSystemFileEntry)
                assert e.name == "deepest.mp3"
                children = e.parent.entries() if e.parent else []
                assert len(children) == 1
                return
            children = e.entries()
            for child in children:
                find_deepest(child, depth + 1)

        find_deepest(root)

    def test_file_in_accessing_undetermined_entry(self, tmp_path: Path) -> None:
        """Test that entries on dir without parent returns own name."""
        (tmp_path / "file1").touch()
        (tmp_path / "dir").mkdir()

        root = FileSystemDirectoryEntry(tmp_path)
        assert root.name == tmp_path.name
        for child in root.entries():
            assert child.parent is root


# ---- descendants() ----


class TestFileSystemDirectoryEntryDescendants:
    """Tests for the FileSystemDirectoryEntry.descendants() method."""

    def test_descendants_count_full_tree(self, hier_tmp_path: Path) -> None:
        """All descendants across the full hierarchy (files and directories)."""
        root = FileSystemDirectoryEntry(hier_tmp_path)
        all_desc = root.descendants()
        assert len(all_desc) == 16

    def test_descendants_includes_files_and_directories(self, hier_tmp_path: Path) -> None:
        """descendants() returns both file and directory entries mixed."""
        root = FileSystemDirectoryEntry(hier_tmp_path)
        all_desc = root.descendants()
        files = [e for e in all_desc if isinstance(e, FileSystemFileEntry)]
        dirs = [e for e in all_desc if isinstance(e, FileSystemDirectoryEntry)]
        assert len(files) == 10
        assert len(dirs) == 6
        assert isinstance(dirs[0], FileSystemDirectoryEntry)
        assert isinstance(files[0], FileSystemFileEntry)

    def test_descendants_of_subdirectory(self, hier_tmp_path: Path) -> None:
        """Descendants of a subdirectory should not include sibling or root entries."""
        root = FileSystemDirectoryEntry(hier_tmp_path)
        seasons = [e for e in root.entries() if e.name == "Seasons_artist"][0]
        assert isinstance(seasons, FileSystemDirectoryEntry)
        expected_names = {"album1_spring", "album2_fall",
                          "track-rainy-day-01.mp3", "track-night-02.mp3",
                          "track-before-the-dawn-03.mp3", "track-fall-01.mp3",
                          "track-fall-02.mp3"}
        assert names == expected_names
        assert len(desc) == 7  # album1_spring(dir) + 3 files + album2_fall(dir) + 2 files
        names = {e.name for e in desc}
        assert names == {"album1_spring", "album2_fall", "track-rainy-day-01.mp3", "track-night-02.mp3", "track-before-the-dawn-03.mp3", "track-fall-01.mp3", "track-fall-02.mp3"}

    def test_descendants_parent_pointers(self, hier_tmp_path: Path) -> None:
        """Each descendant should point to its immediate parent, not the root."""
        root = FileSystemDirectoryEntry(hier_tmp_path)
        all_desc = root.descendants()
        for entry in all_desc:
            assert entry.parent is not None
            assert isinstance(entry.parent, FileSystemDirectoryEntry)

    def test_descendants_deep_nesting(self, hier_tmp_path: Path) -> None:
        jester_dir = FileSystemDirectoryEntry(jester.path)
        colors = [e for e in jester_dir.entries() if e.name == "Colors"][0]
        root = FileSystemDirectoryEntry(hier_tmp_path)
        jester = [e for e in root.entries() if e.name == "Artist_formerly_known_as_Jester"][0]
        colors = [e for e in FileSystemDirectoryEntry(jester.path).entries() if e.name == "Colors"][0]
        assert isinstance(colors, FileSystemDirectoryEntry)
        all_colors_desc = colors.descendants()
        assert len(all_colors_desc) == 4  # purple-01.mp3, rain-02.mp3, bonus/dir, hidden_colors.ogg
        file_desc = [e for e in all_colors_desc if isinstance(e, FileSystemFileEntry)]
        dir_desc = [e for e in all_colors_desc if isinstance(e, FileSystemDirectoryEntry)]
        assert len(file_desc) == 3  # purple-01.mp3, rain-02.mp3, hidden_colors.ogg
        assert len(dir_desc) == 1
        bonus = dir_desc[0]
        bonus_desc = bonus.descendants()
        assert len(bonus_desc) == 1
        assert bonus_desc[0].name == "hidden_colors.ogg"

    def test_descendants_empty_directory(self, tmp_path: Path) -> None:
        """An empty directory returns no descendants."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        entry = FileSystemDirectoryEntry(empty_dir)
        assert entry.descendants() == []

    def test_descendants_flat_structure(self, tmp_path: Path) -> None:
        """When a directory has only files and no subdirs, descendants = all files."""
        (tmp_path / "a.mp3").touch()
        (tmp_path / "b.flac").touch()
        (tmp_path / "c.ogg").touch()
        entry = FileSystemDirectoryEntry(tmp_path)
        desc = entry.descendants()
        assert len(desc) == 3
        assert all(isinstance(e, FileSystemFileEntry) for e in desc)

    def test_descendants_flatten_cross_branches(self, hier_tmp_path: Path) -> None:
        """Descendants should be a flat list across all branches, not grouped."""
        expected_names = ["loose-song1.mp3", "loose-song2.m4a",
                          "track-rainy-day-01.mp3", "track-fall-02.mp3",
                          "hidden_colors.ogg"]
        for name in expected_names:
        all_desc = root.descendants()
        expected_names = ["loose-song1.mp3", "loose-song2.m4a",
                          "track-rainy-day-01.mp3", "track-fall-02.mp3",
                          "hidden_colors.ogg"]
        for name in expected_names:
            assert any(e.name == name for e in all_desc)
