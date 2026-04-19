# Audio Format Tagging Support

## mutagen format coverage

### Full support (read + write tags)
| Format | Extensions | Mutagen module | Tag standard |
|--------|-----------|----------------|--------------|
| MP3 | `.mp3` | `mutagen.mp3` + `mutagen.id3` | ID3v2.3/2.4 |
| FLAC | `.flac` | `mutagen.flac` | Vorbis comments |
| M4A/MP4 | `.m4a` | `mutagen.mp4` | MP4/3GPP |
| OGG Vorbis | `.ogg` | `mutagen.oggvorbis` | Vorbis comments |
| WMA | `.wma` | `mutagen.asf` | ASF/Windows Media |

### Read-only / no embedded tag support
| Format | Extensions | Mutagen module | Notes |
|--------|-----------|----------------|-------|
| AAC | `.aac`, `.m4a` (ADTS raw) | `mutagen.aac` | **Tagging not supported** by mutagen |
| AC3 | `.ac3`, `.eac3` | `mutagen.ac3` | **Tagging not supported** by mutagen |
| M4A (ALAC) | `.m4a` | `mutagen.mp4` | Full support (uses 3GPP/MP4 tags) |

## AAC tagging limitation

Mutagen's `AAC` class (`mutagen.aac`) and `AC3` class (`mutagen.ac3`) support **reading** file metadata (codec info, duration, sample rate) but neither has any embedded tag writing capability.

Mutagen's own docstrings explicitly state:
> Tagging is not supported. Use the ID3/APEv2 classes directly instead.

This is because raw ADTS AAC and raw AC3 streams do not have a standard container format for embedding tags.

### Workaround options

1. **Use M4A container for AAC** — FFmpeg can encode AAC as ALAC inside an MP4 container (`.m4a`) which supports full ID3/MP4 tagging via `mutagen.mp4`. This is the simplest path if you need AAC with tags.

2. **External sidecar files** — Store tags in separate `.yaml`, `.json`, or `.nfo` files.

3. **Generate test files** — To create test AAC/AC3 audio without tags, use ffmpeg directly. Tag writing via mutagen will always fail.

## ffmpeg codec availability

| Codec | ffmpeg encoder | mutagen tag support | Recommended mutagen module |
|-------|---------------|---------------------|---------------------------|
| AAC | `libfdk_aac` or default `aac` | No (raw ADTS) | `mutagen.aac` (read-only) |
| AAC | `alac` inside MP4 container (`.m4a`) | Yes | `mutagen.mp4` |
| AC3 | `ac3` | No | `mutagen.ac3` (read-only) |
| MP3 | `libmp3lame` or default `libfdk_lame` | Yes | `mutagen.mp3` |
| FLAC | `flac` (lossless) | Yes | `mutagen.flac` |
| OGG Vorbis | `libvorbis` | Yes | `mutagen.oggvorbis` |
| WMA | `wmav2` | Yes | `mutagen.asf` |
