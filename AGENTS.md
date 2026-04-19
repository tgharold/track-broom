# track-broom — Agent Instructions

## Setup
- `uv sync` — install deps (requires uv; Python >= 3.11)
- `.venv/` is gitignored, but excluded from uv lockfiles via the `=*` prefix workaround
- Always run within the venv: activate it with `source .venv/bin/activate`

## Run
- `.venv/bin/track-broom scan <path>` — scan music files and display metadata table
- `.venv/bin/track-broom list <path>` — list files, optional `--extension` filter
- `.venv/bin/track-broom 000-enhance-genres <path>` — **skeleton, not implemented** (see TODO in source)
- `.venv/bin/track-broom generate-tone` — generate test MP3 with hardcoded values per CLI args
- `.venv/bin/python -m track_broom` — same as `track-broom`

## Lint
- `.venv/bin/ruff check --line-length=100 .` — linter (config in `pyproject.toml`)
- `.venv/bin/ruff format .` — formatter (config in `pyproject.toml`)

## Test
- `.venv/bin/python -m pytest tests/` — run all 28 tests
  - `tests/test_scanner.py` (13 tests) — file discovery
  - `tests/test_generate_tone.py` (14 tests) — PCM generation, ffmpeg encoding, ID3 tags (uses `tests.utils`)
  - **No `test_tags.py`** — `tags.py` has no dedicated tests despite being the core module

## Architecture
- `src/track_broom/cli.py` — Typer CLI, 5 commands
- `src/track_broom/scanner.py` — recursive file scanning, supports 8 music extensions
- `src/track_broom/tags.py` — mutagen-based tag reader/writer for MP3/FLAC/M4A/OGG/WMA

## Gotchas
- `ffmpeg` binary must be on PATH (ffmpeg-python is a thin wrapper, no bundled FFmpeg)
- `test_mp3s/` is gitignored; regenerate via `scripts/generate_test_tones.py`
- `000-enhance-genres` is a TODO placeholder — genre detection and enhancement
- Hyphen vs underscore: CLI branding is `track-broom`, Python package name is `track_boom` (see `docs/naming-convention.md`)
