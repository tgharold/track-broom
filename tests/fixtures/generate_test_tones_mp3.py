#!/usr/bin/env python3
"""Generate standard test MP3 tone files."""

from pathlib import Path

from tests.fixtures.builders import generate_sample_dir


def main() -> int:
    """Generate all test files in test_files/ containing all 5 format subdirs."""
    output_dir = Path("test_files")
    count = generate_sample_dir(output_dir)
    print(f"All {count} tones generated in {output_dir}/")
    return count


if __name__ == "__main__":
    main()
