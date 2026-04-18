# Plan: Generate Test MP3 Files

## Goal
Create MP3 test files with synthetic tones and ID3 tags without using ffmpeg.

## Approach
1. Generate raw PCM audio samples using Python stdlib (`struct`, `math`)
2. Encode PCM → MP3 using `lameenc` (pure-Python LAME binding, no ffmpeg)
3. Add ID3 tags using `mutagen` (already a dependency)

## Implementation Steps

### 1. Add `lameenc` dependency
```
uv add --dev lameenc>=1.7.0
```

### 2. Create `src/trackoon/util.py` with 3 functions:

**`tone_samples(freq: int, duration: float, samplerate: int = 44100) -> bytes`**
- Generates n-channel raw PCM samples at a given frequency
- Uses `struct.pack` with `<h` (signed 16-bit little-endian)
- Formula: `amplitude * sin(2 * pi * freq * t)`
- Applies a short fade-in/out (50ms) to avoid clicks
- Normalizes sample data to fit 16-bit range (-32768..32767)

**`encode_mp3(samples: bytes, freq: int, duration: float, samplerate: int = 44100,
              channels: int = 1, bitrate: int = 128) -> bytes`**
- Uses `lameenc.Encoder` from the `lameenc` package
- Sets sample rate, channels, bitrate, VBR mode
- Encodes raw PCM samples to MP3 bytes

**`add_id3_tags(mp3_bytes: bytes, title: str, artist: str = "", album: str = "",
               genre: str = "", tracknumber: int = 1) -> bytes`**
- Loads MP3 data with `mutagen.mp3.MP3(file_obj=BytesIO(mp3_bytes))`
- Sets `MP3.tags["TIT2"] = title`, `"TPE1"` = artist, etc. via mutagen's `id3`
- Encodes all Unicode tags with UTF-8
- Returns MP3 bytes with embedded ID3v2 tags

### 3. Add CLI command `generate-tone` in `src/trackoon/cli.py`

```
trackoon generate-tone [OPTIONS]

Options:
  --freq INT           Tone frequency in Hz (default: 440)
  --duration FLOAT     Duration in seconds (default: 5.0)
  --output PATH        Output file path (default: stdout or generated filename)
  --bitrate INT        MP3 bitrate in kbps (default: 128)
  --title TEXT         Title tag
  --artist TEXT        Artist tag
  --genre TEXT         Genre tag
```

### 4. Add tests in `tests/test_generate_tone.py`
- `test_tone_samples_length` — verify sample count matches expected duration
- `test_tone_samples_fade` — verify fade-in/out samples are within range
- `test_encode_mp3_output` — verify `lameenc` encodes to valid MP3 bytes
- `test_add_id3_tags` — verify tags get written correctly

### 5. Auto-generate test MP3s
- Create a low-level script `scripts/generate_test_tones.py` that:
  - Generates `a4_440hz.mp3` — 5s 440Hz tone (A4)
  - Generates `c4_261hz.mp3` — 5s 261.63Hz tone (middle C)
  - Generates `note_C.mp3` — C note tag set (Harmonics)
  - Generates `note_A.mp3` — A note tag set (Harmonics)
  - Generates `note_H.mp3` — H note tag set (Humore)
  - All with `lameenc` encoding and `mutagen` ID3 tags
  - Does **not** call ffmpeg or external encoders

### 6. Update `.gitignore`
```
*.mp3
test_mp3s/
```
Do **not** commit generated MP3 files.

## Notes
- `lameenc` is a pure-Python wrapper around libmp3lame installed via pip (Rust/Python bindings)
- No system ffmpeg/lame dependency required
- Total code is ~120 lines in `util.py` + ~60 lines for CLI + ~60 lines for tests
- Generated MP3s are ~80-100KB each (128kbps, 5s, mono)
