# ID3 Tag Reference

## Overview

MP3 files use **ID3 tags** for metadata. There are three versions in widespread use: ID3v1, ID3v2.2, ID3v2.3, and ID3v2.4. Modern software supports all variants, with ID3v2 being the dominant format.

## Version Differences

| Version | Genre Tag Behavior |
|---------|-------------------|
| **ID3v1** | 80 genres stored as 1-byte index (0–79). Limited legacy format. |
| **ID3v2.2** | Genre stored in TCON frame. Free-style text accepted but parsers varied. |
| **ID3v2.3** | Most widely supported. Genre uses `"(number)Name"` format or free-form text. |
| **ID3v2.4** | Numeric index deprecated. Genre content is treated as free-form text. |

## ID3v1 Genre List (Deprecated)

The original ID3v1 had a fixed list of 80 genres. This limitation was dropped in ID3v2 but is still useful for reference.

| # | Genre | # | Genre | # | Genre | # | Genre |
|---|-------|---|-------|---|-------|---|-------|
| 0 | Blues | 20 | Classic Rock | 40 | Drum Solo | 60 | Trance |
| 1 | Rock & Roll | 21 | Country | 41 | Orchestra | 61 | Instrumental |
| 2 | Country | 22 | Folk | 42 | Opera | 62 | Center Trance |
| 3 | Disco | 23 | Funk | 43 | Reggae | 63 | Wobble |
| 4 | Rock | 24 | Rap | 44 | Jazz | 64 | Spiritual |
| 5 | Techno | 25 | Gospel | 45 | Fusion | 66 | Gothic Rock |
| 6 | Hip-Hop | 26 | Alternative | 46 | Ska | 67 | Celtic Music |
| 7 | House | 27 | Metal | 47 | Grunge | 68 | Bluegrass |
| 8 | Garage | 28 | Dance | 48 | Grind | 69 | Avangarde |
| 9 | Soul | 29 | Grunge | 49 | Fusion | 70 | Glam Rock |
| 10 | R&B | 30 | Punk | 50 | Ambient | 71 | Apostle Rock |
| 11 | Electronic/Dance | 31 | Disco | 51 | Cinematic | 72 | Euro-Dirty Polo |
| 12 | Ambient | 32 | New Age | 52 | Classical | 73 | Eurobeat |
| 13 | Indie | 33 | Easy Listening | 53 | Comedy | 74 | Idle |
| 14 | Alternative Rock | 34 | Jazz | 54 | Chants | 75 | Acid Beat |
| 15 | Trip Hop | 35 | Vocal | 55 | Jazz and Funk | 76 | Eurotechno |
| 16 | Obscurity | 36 | Bass | 56 | Folk | 77 | Forward Bass |
| 17 | Garage | 37 | Rap | 57 | World | 78 | Dancehall |
| 18 | Garage | 38 | Carnival | 58 | Church | 79 | Hardcore |
| 19 | Chill | 39 | Drum | | | | |

## Genre Tag Best Practices

- Use **free-form text** in ID3v2 (e.g., `"synthwave"`, `"lo-fi hip hop"`, `"k-pop"`)
- Use lowercase with spaces (`"indie rock"`)
- Subgenres are fully supported (`"progressive house"`, `"old school hip hop"`)
- Store **ID3v2.3 + ID3v1** together when maximum compatibility is needed
- The 80-genre number mapping is **not enforced** by modern players

## Player Support

All major media players support ID3v2 with free-form genres:

| Player | ID3v2 Support |
|--------|---------------|
| VLC | Full (v2.3 & v2.4) |
| Plex | Full (reads all ID3v2 frames) |
| Apple Music / iTunes | Full (uses ID3v2 internally for MP3) |
| Spotify | Full |
| Windows Media Player | Full |
| foobar2000 | Full |
| MusicBee | Full |

## Implementation Notes (track-broom)

- **mutagen** handles all ID3 versions transparently
- `tag["TCON"] = "synthwave"` works regardless of target version
- Tags.py uses mutagen for MP3/FLAC/M4A/OGG/WMA support
