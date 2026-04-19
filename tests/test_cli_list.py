"""Tests for the CLI list command (list_files_cmd)."""

from pathlib import Path
from typer.testing import CliRunner

from track_broom.cli import app

runner = CliRunner()

FIXTURE_DIR = Path("test_files")


def _parse_output(output: str) -> list[str]:
    """Parse CLI list output into individual filenames, excluding dotfiles."""
    lines = [l.strip() for l in output.splitlines() if l.strip()]
    return [l for l in lines if not l.lstrip("/").startswith(".")]


class TestListFilesCmd:
    """Tests for the 'list' CLI command."""

    def test_list_all_files(self):
        """list_files_cmd without --ext lists all fixture files."""
        result = runner.invoke(app, ["list", str(FIXTURE_DIR)])
        assert result.exit_code == 0, result.exception
        lines = _parse_output(result.stdout)
        assert len(lines) == 15

    def test_list_files_extensions(self):
        """list_files_cmd lists files with correct extensions."""
        result = runner.invoke(app, ["list", str(FIXTURE_DIR)])
        assert result.exit_code == 0, result.exception
        lines = _parse_output(result.stdout)
        exts = {f.rsplit(".", 1)[-1] for f in lines}
        assert exts == {"mp3", "flac", "m4a", "ogg", "wma"}

    def test_list_with_ext_filter(self):
        """list_files_cmd with --ext filters to matching files only."""
        result = runner.invoke(app, ["list", str(FIXTURE_DIR), "--ext", "mp3"])
        assert result.exit_code == 0, result.exception
        lines = _parse_output(result.stdout)
        assert len(lines) == 3
        for line in lines:
            assert line.endswith(".mp3")

    def test_list_with_ext_short_flag(self):
        """list_files_cmd with -e short flag works same as --ext."""
        result = runner.invoke(app, ["list", str(FIXTURE_DIR), "-e", "m4a"])
        assert result.exit_code == 0, result.exception
        lines = _parse_output(result.stdout)
        assert len(lines) == 3

    def test_list_with_nonexistent_ext(self):
        """list_files_cmd with non-existent ext prints 'No files found'."""
        result = runner.invoke(app, ["list", str(FIXTURE_DIR), "--ext", "zip"])
        assert result.exit_code == 0, result.exception
        assert "No files found" in result.stdout
