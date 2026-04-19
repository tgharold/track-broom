# track-broom — Agent Instructions

## Setup
- `.venv/` is gitignored

## Run

## Lint

## Test
- `uv run pytest` — run all tests

## Architecture
- `src/track_broom/cli.py` — Typer CLI, 5 commands
- `src/track_broom/scanner.py` — recursive file scanning, supports 8 music extensions
- `src/track_broom/tags.py` — mutagen-based tag reader/writer for MP3/FLAC/M4A/OGG/WMA

## Gotchas
- `ffmpeg` binary must be on PATH (ffmpeg-python is a thin wrapper, no bundled FFmpeg)
- `test_mp3s/` is gitignored; regenerate via `scripts/generate_test_tones.py`
- `000-enhance-genres` is a TODO placeholder — genre detection and enhancement
- Hyphen vs underscore: CLI branding is `track-broom`, Python package name is `track_boom` (see `docs/naming-convention.md`)
