"""Validate the sample_fixture_dir session-scoped fixture."""

from pathlib import Path

from tests.fixtures.builders import EXPECTED_TOTAL_FILES, FORMATS

class TestFixtureDirSmoke:
    """Smoke test that sample_fixture_dir generates the right structure."""

    def test_fixture_exposes_directory(self, sample_fixture_dir: Path) -> None:
        assert sample_fixture_dir.is_dir()

    def test_correct_number_of_format_dirs(self, sample_fixture_dir: Path) -> None:
        actual = {d.name for d in sample_fixture_dir.iterdir() if d.is_dir()}
        assert actual == set(FORMATS.keys()), f"Expected {set(FORMATS.keys())}, got {actual}"

    def test_total_files_matches_expected_count(self, sample_fixture_dir: Path) -> None:
        total = sum(1 for f in sample_fixture_dir.rglob("*") if f.is_file())
        assert total == EXPECTED_TOTAL_FILES, (
            f"Expected {EXPECTED_TOTAL_FILES} files, found {total}"
        )

    def test_all_files_nonempty(self, sample_fixture_dir: Path) -> None:
        for f in sample_fixture_dir.rglob("*"):
            if f.is_file():
                assert f.stat().st_size > 0, f"{f} is empty"
