# trackoon — Agent Instructions

## Setup
- `uv sync` — install deps (requires uv; Python >= 3.11)
- `.venv/` is gitignored but excluded from lockfiles via `=*` prefix workaround

## Run
- `uv run trackoon scan <path>` — scan music files and display metadata table
- `uv run trackoon list <path>` — list files, optional `--extension` filter
- `uv run trackoon 000-enhance-genres <path>` — **skeleton, not implemented** (see TODO in source)
- `uv run trackoon generate-tone` — generate test MP3 with hardcoded values per CLI args
- `uv run python -m trackoon` — same as `trackoon`

## Test
- `PYTHONPATH=src python -m pytest tests/` — run all 27 tests
  - `tests/test_scanner.py` (13 tests) — file discovery
  - `tests/test_generate_tone.py` (14 tests) — PCM generation, ffmpeg encoding, ID3 tags
  - **No `test_tags.py`** — `tags.py` has no dedicated tests despite being the core module

## Lint
- `ruff check --line-length=100 .` — linter (config in `pyproject.toml`)
- No formatter configured (use `ruff format` if needed)

## Architecture
- `src/trackoon/cli.py` — Typer CLI, 5 commands
- `src/trackoon/scanner.py` — recursive file scanning, supports 8 music extensions
- `src/trackoon/tags.py` — mutagen-based tag reader/writer for MP3/FLAC/M4A/OGG/WMA
- `src/trackoon/util.py` — tone generation (PCM + ffmpeg encode + ID3 write), used by tests/scripts

## Gotchas
- `ffmpeg` binary must be on PATH (ffmpeg-python is a thin wrapper, no bundled FFmpeg)
- `test_mp3s/` is gitignored; regenerate via `scripts/generate_test_tones.py`
- `000-enhance-genres` is a TODO placeholder — genre detection logic is not implemented
- A deleted `test_tags.py` left a `__pycache__` artifact in `tests/__pycache__/`
