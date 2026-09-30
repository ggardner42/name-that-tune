# Name That Tune – Audio Preparation Tools

A set of Python scripts that create “Name That Tune” style audio tracks.

For every song you get **two** final MP3 files:

1. A **clue track** containing:
   - a short opening clip
   - 5 seconds of silence
   - a slightly longer opening clip
   - 5 seconds of silence

2. The **full original song**

This format is useful for cognitive stimulation, rehabilitation activities, parties, or just for fun.

The scripts were written by **Grok** (xAI).

---

## Features

- Two tracks per song with clean sequential numbering
- Clip lengths (`a` and `b`) are stored directly in the source filename
- Easy single-song tuning by ear
- Original MP3 files are copied (no re-encoding) whenever possible
- Other formats are converted with high-quality LAME VBR
- Automatic ID3v2 tagging (ID3v1 tags are removed)
- Generates a printable track list PDF
- Works on Linux, macOS, and Windows (once the required tools are installed)

---

## Requirements

- Python 3.10 or newer
- `ffmpeg`
- `lame`
- `id3v2`

Install the Python packages:

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install pydub pyyaml reportlab audioop-lts
```

---

## Folder Structure

```
name-that-tune/
├── originals/          # Your source files (ground truth)
├── temp/               # Temporary working files (safe to delete)
├── final_mp3s/         # Final tagged MP3s ready for a data CD
├── params.yaml         # Global default a/b values
├── tracklist.pdf       # Generated track list
├── scan_originals.py
├── process_one.py
└── process_all.py
```

---

## Source Filename Format

Every file in `originals/` must follow this exact pattern:

```
NN -- Artist -- Album -- Title -- A -- B.ext
```

- `NN` = track order number (01, 02, 03…)
- `A`  = first clip length in **milliseconds**
- `B`  = second clip length in **milliseconds**

Example:

```
01 -- The Beatles -- A Hard Day's Night -- A Hard Day's Night -- 1200 -- 3500.mp3
04 -- Jimi Hendrix Experience -- Electric Ladyland -- All Along the Watchtower -- 800 -- 2800.flac
```

Supported extensions: `.mp3`, `.flac`, `.wav`, `.ogg`, `.m4a`, `.aac`

---

## Typical Workflow

1. **Add or change songs**

   Place files in the `originals/` folder using the naming format above.  
   You can omit the `-- A -- B` part at first.

2. **Scan and validate**

   ```bash
   ./scan_originals.py
   ```

   - Checks that every filename is valid
   - Ensures all NN values are unique
   - Warns about gaps in the sequence
   - Automatically adds default `A` and `B` values (and renames the file) when they are missing

3. **Tune one song at a time**

   ```bash
   ./process_one.py 05
   ```

   This creates `temp/Current Tune Clue.mp3`.  
   Listen to it, then adjust:

   ```bash
   ./process_one.py 05 -a 1.3 -b 3.8
   ```

   The script will automatically rename the file in `originals/` with the new millisecond values and regenerate the clue.

4. **Build the final set**

   ```bash
   ./process_all.py
   ```

   This produces:
   - All clue + full-song MP3s in `final_mp3s/`
   - `tracklist.pdf`

You can then burn the contents of `final_mp3s/` together with `tracklist.pdf` onto a data CD.

---

## Final Track Numbering

| Track # | Content              | Title example              | Artist          | Album                      |
|---------|----------------------|----------------------------|-----------------|----------------------------|
| 01      | Clue for song 01     | Tune Clue #01              | Name That Tune  | Name That Tune – Clues     |
| 02      | Full song 01         | A Hard Day's Night         | The Beatles     | A Hard Day's Night         |
| 03      | Clue for song 02     | Tune Clue #02              | Name That Tune  | Name That Tune – Clues     |
| 04      | Full song 02         | I Feel the Earth Move      | Carole King     | Tapestry                   |
| …       | …                    | …                          | …               | …                          |

---

## params.yaml

This file only stores the global defaults (in milliseconds):

```yaml
defaults:
  a: 1000
  b: 3000
```

Individual song values live in the filenames themselves.

---

## Scripts Overview

| Script              | Purpose                                              |
|---------------------|------------------------------------------------------|
| `scan_originals.py` | Validate filenames, fill in missing A/B values       |
| `process_one.py`    | Create a clue for one song and optionally update A/B |
| `process_all.py`    | Build the complete set of final MP3s + PDF           |

---

## Credits

Scripts written by **Grok** (built by xAI).

Feel free to use, modify, and share.
