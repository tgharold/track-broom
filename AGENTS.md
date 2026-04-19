# track-broom — Agent Instructions

## Setup
- `uv sync` — install deps (use `.[dev]` for pyright/pytest/ruff)
- `.venv/` and `uv.lock` are gitignored

## Lint & Typecheck
- `ruff check` — lint (configured: E,F,W,I,N,UP,B; ignore B008; line-length 100)
- `ruff format --check` — format check
- `pyright` — typecheck

## Test
- `uv run pytest` — run all tests
- Test fixtures in `tests/utils/` — uses `ffmpeg-python` + `mutagen` to generate synthetic audio; `ffmpeg` binary must be on PATH

## Architecture
- `src/track_broom/cli.py` — Typer CLI with 3 commands: `scan`, `list`, `000-enhance-genres` (stub)
- `src/track_broom/scanner.py` — recursive scanning for 8 music extensions + a generic `list_files`
- `src/track_broom/tags.py` — mutagen-based tag reader/writer for MP3/FLAC/M4A/OGG/WMA
- `src/track_broom/__main__.py` — enables `python -m track_broom`

## Gotchas
- `ffmpeg` binary must be on PATH (ffmpeg-python is a thin wrapper, no bundled FFmpeg)
- `test_files/` is gitignored; regenerate via `scripts/generate_test_tones_mp3.py`, `scripts/generate_test_tones_m4a.py`, `scripts/generate_test_tones_flac.py`, `scripts/generate_test_tones_ogg.py`, and `scripts/generate_test_tones_wma.py`
- `000-enhance-genres` is a TODO placeholder — genre detection logic is not implemented
- Package name is `track_broom`; CLI entry point in `pyproject.toml` maps `"track-broom"` → `track_broom.cli:app`
