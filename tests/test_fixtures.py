"""Validate all 5 fixture generation scripts created sample files in test_files/."""

from pathlib import Path

EXPECTED_COUNT = 3  # Each script creates 3 tones: C, A, H

# Maps format name to (directory suffix, expected filenames)
FORMAT_MAPPINGS = {
    "mp3": ("mp3", ["note_C", "note_A", "note_H"]),
    "flac": ("flac", ["note_C", "note_A", "note_H"]),
    "m4a": ("m4a", ["note_C", "note_A", "note_H"]),
    "ogg": ("ogg", ["note_C", "note_A", "note_H"]),
    "wma": ("wma", ["note_C", "note_A", "note_H"]),
}


def _get_expected_fixtures():
    result = {}
    for fmt, (suffix, names) in FORMAT_MAPPINGS.items():
        result[fmt] = {
            "dir": Path("test_files") / suffix,
            "names": names,
            "ext": suffix,
        }
    return result


class TestTestFixtureGeneration:
    """Every generation script should have produced its expected samples."""

    def test_all_5_format_directories_exist(self) -> None:
        dirs = _get_expected_fixtures()
        for fmt, info in dirs.items():
            assert info["dir"].exists(), f"test_files/{info['ext']}/ missing"

    def test_mp3_files_created(self) -> None:
        info = _get_expected_fixtures()["mp3"]
        for name in info["names"]:
            fpath = info["dir"] / f"{name}.{info['ext']}"
            assert fpath.exists(), f"{fpath} missing"
            assert fpath.stat().st_size > 0, f"{fpath} is empty"

    def test_flac_files_created(self) -> None:
        info = _get_expected_fixtures()["flac"]
        for name in info["names"]:
            fpath = info["dir"] / f"{name}.{info['ext']}"
            assert fpath.exists(), f"{fpath} missing"
            assert fpath.stat().st_size > 0, f"{fpath} is empty"

    def test_m4a_files_created(self) -> None:
        info = _get_expected_fixtures()["m4a"]
        for name in info["names"]:
            fpath = info["dir"] / f"{name}.{info['ext']}"
            assert fpath.exists(), f"{fpath} missing"
            assert fpath.stat().st_size > 0, f"{fpath} is empty"

    def test_ogg_files_created(self) -> None:
        info = _get_expected_fixtures()["ogg"]
        for name in info["names"]:
            fpath = info["dir"] / f"{name}.{info['ext']}"
            assert fpath.exists(), f"{fpath} missing"
            assert fpath.stat().st_size > 0, f"{fpath} is empty"

    def test_wma_files_created(self) -> None:
        info = _get_expected_fixtures()["wma"]
        for name in info["names"]:
            fpath = info["dir"] / f"{name}.{info['ext']}"
            assert fpath.exists(), f"{fpath} missing"
            assert fpath.stat().st_size > 0, f"{fpath} is empty"

    def test_all_5_formats_covered(self) -> None:
        expected = {"mp3", "flac", "m4a", "ogg", "wma"}
        actual = {d.name for d in Path("test_files").iterdir() if d.is_dir()}
        assert expected == actual, (
            f"Expected {expected}, found {actual}"
        )
