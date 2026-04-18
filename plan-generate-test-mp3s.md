# Plan: Generate Test MP3 Files

## Goal
Create MP3 test files with synthetic tones and ID3 tags.

## Approach
1. Generate raw PCM audio samples using Python stdlib (`struct`, `math`)
2. Encode PCM → MP3 using **`ffmpeg-python`** (Python wrapper, avoids manual subprocess plumbing)
3. Add ID3 tags using `mutagen` (already a dependency)

## Implementation Steps

### 1. Add `ffmpeg-python` dependency
```
uv add --dev ffmpeg-python>=0.2.0
```

### 2. Create `src/trackoon/util.py` with 3 functions:

**`tone_samples(freq: int = 440, duration: float = 3.0, samplerate: int = 44100) -> bytes`**
- Generates raw PCM samples for a sine wave at the given frequency
- Uses `struct.pack` with `<h` (signed 16-bit little-endian)
- Formula: `amplitude * sin(2 * pi * freq * t)`
- Applies a 50ms fade-in/fade-out to avoid clicks
- Normalizes sample data to fit 16-bit range (-32768..32767)

**`encode_mp3(pcm_data: bytes, output_path: str, samplerate: int = 44100,
             channels: int = 1, bitrate: int = 128) -> str`**
- Encodes raw PCM bytes to MP3 using `ffmpeg-python`:
  ```python
  import ffmpeg

  ffmpeg \
    .input('pipe:0', format='s16le', ar=samplerate, ac=channels) \
    .output(output_path, ar=samplerate, **{'b:a': f'{bitrate}k'}) \
    .overwrite_output() \
    .run(input=pcm_data, capture_stdout=True, capture_stderr=True)
  ```
- Writes PCM bytes to ffmpeg's stdin via `input=pcm_data`
- Returns output_path on success, raises `ffmpeg.Error` on failure

**`add_id3_tags(filepath: str, title: str, artist: str = "", album: str = "",
               genre: str = "", tracknumber: int = 1) -> None`**
- Loads MP3 with `mutagen.mp3.MP3(filepath)`
- Sets ID3 tags: `TIT2` (title), `TPE1` (artist), `TALB` (album),
  `TCON` (genre), `TRCK` (track), all UTF-8 encoded
- Writes tags to file

### 3. Add CLI command `generate-tone` in `src/trackoon/cli.py`

```
trackoon generate-tone [OPTIONS]

Options:
  --freq FLOAT           Tone frequency in Hz (default: 440)
  --duration FLOAT       Duration in seconds (default: 5.0)
  --output PATH          Output file (default: ./tone_<freq>Hz_<duration>s.mp3)
  --samplerate INT       Sample rate Hz (default: 44100)
  --channels INT         Mono=1 / Stereo=2 (default: 1)
  --bitrate INT          MP3 bitrate kbps (default: 128)
  --title TEXT           Title tag
  --artist TEXT          Artist tag
  --genre TEXT           Genre tag
  --tracknumber INT      Track number (default: 1)
```

### 4. Add tests in `tests/test_generate_tone.py`
- `test_tone_samples_440hz_5s` — verify sample count matches expected duration
- `test_tone_samples_fade` — verify fade-in/fade-out values
- `test_encode_mp3_file_created` — verify ffmpeg produces an MP3 file
- `test_encode_mp3_invalid_input` — verify error on bad PCM data
- `test_add_id3_tags_written` — verify tags appear in file metadata

### 5. Auto-generate test MP3s
- Create `scripts/generate_test_tones.py` to produce:

| # | File | Freq | Duration | Title | Artist/Album | Genre |
|---|------|------|----------|-------|-------------|-------|
| 1 | `note_C.mp3` | 261.63 Hz | 3s | "C" | Harmonics / C | Classical |
| 2 | `note_A.mp3` | 440 Hz | 3s | "A" | Harmonics / A | Classical |
| 3 | `note_H.mp3` | 415.30 Hz | 3s | "H" | Humore / H | Classical |

- Uses `tone_samples()` → `encode_mp3()` → `add_id3_tags()` pipeline
- Outputs to `test_mp3s/` directory
- Does **not** require system ffmpeg directly (all via `ffmpeg-python` wrapper)

### 6. Update `.gitignore`
```
test_mp3s/
```
Do **not** commit generated MP3 files.

## Notes
- `ffmpeg` binary must be on PATH (`ffmpeg-python` is a thin wrapper, no FFmpeg bundled)
- `mutagen` handles ID3 tags via its Python API (no ffmpeg tag args)
- ~90 lines in `util.py`, ~50 lines CLI, ~50 lines tests, ~40 lines script
- MP3s ~30-50KB each (128kbps, 3s, mono)
