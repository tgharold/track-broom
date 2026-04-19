"""pytest fixtures for sample audio files."""

from pathlib import Path

import pytest

from tests.fixtures.builders import EXPECTED_TOTAL_FILES, generate_sample_dir


@pytest.fixture(scope="session")
def sample_fixture_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Generate sample audio files in a unique temp directory for the test session.

    Creates 15 files (5 formats x 3 tones) across format subdirectories
    under a temp base.  Asserts the total file count is 15.
    """
    test_dir = tmp_path_factory.mktemp("sample_audio", numbered=False)

    created = generate_sample_dir(test_dir)
    expected = EXPECTED_TOTAL_FILES

    assert created == expected, (
        f"Expected {expected} sample files, but only {created} were created"
    )

    return test_dir
