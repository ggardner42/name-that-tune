# Name That Tune – Audio Preparation Tools

A small set of Python scripts to create “Name That Tune” style audio tracks for cognitive stimulation / rehabilitation (or just for fun).

Each final track contains:
1. A very short clip of the song (default 1 second)
2. 5 seconds of silence
3. A slightly longer clip (default 3 seconds)
4. 5 seconds of silence
5. The full song

This format lets a listener try to name the song from the short openings before hearing the complete track.

The scripts were written by **Grok** (xAI).

---

## Features

- Easy per-song tuning of the two clip lengths
- Human-editable YAML configuration
- Batch or single-song processing
- Automatic conversion from FLAC/MP3/etc. → WAV → final MP3
- ID3 tagging and a printable track list PDF
- Designed for iterative work (tune one song at a time by ear)

---

## Requirements

- Ubuntu / Debian (or any Linux with the tools below)
- Python 3.10+
- `ffmpeg`
- `lame`
- `id3v2`
- Python packages: `pydub`, `pyyaml`, `reportlab`  
  (and `audioop-lts` if you are on Python 3.13+)

```bash
sudo apt install ffmpeg lame id3v2 python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip install pydub pyyaml reportlab audioop-lts
```

## Folder Structure

NameThatTune/
├── originals/          # Put your source files here
├── wavs/               # Intermediate clean WAVs (auto-created)
├── ntt_wavs/           # Name-That-Tune WAV versions (auto-created)
├── final_mp3s/         # Final tagged MP3s ready for a data CD
├── params.yaml         # All settings (auto-created / updated)
├── tracklist.pdf       # Generated track list
├── scan_originals.py
├── process_one.py
└── process_all.py

## Source Filename Format

Name your files in original/ like this:
(Track -- Artist -- Album -- Title.suffix)

01 -- The Beatles -- A Hard Day's Night -- A Hard Day's Night.flac
02 -- The Beatles -- Help! -- Yesterday.mp3

(The "NN --" prefix controls the final order)
(I chose two dashes -- because an artist of title might have a single dash.)

## Typical Workflow

1. Add songs
``` bash
# Drop files into originals/ using the naming format above
./scan_originals.py
```

This updates params.yaml and creates the corresponding WAV files in the wavs/ directory.

2. Tune one song at a time (optional, assuming default is often wrong due to leading silence or your ear demands something else
``` bash
./process_one.py 01
# Listen to ntt_wavs/..._ntt.wav
# Edit the a / b values in params.yaml
./process_one.py 01          # regenerate just that song
```

3. When happy with the whole set
``` bash
./process_all.py
```

This produces:
* Fully tagged MP3s in final_mp3s/
* tracklist.pdf

You can burn the contents of final_mp3s/ + tracklist.pdf onto a data CD.

## params.yaml
Example:
``` yaml
defaults:
  a: 1.0
  b: 3.0
  silence: 5.0

songs:
  "01 -- The Beatles -- A Hard Day's Night -- A Hard Day's Night":
    nn: "01"
    artist: The Beatles
    album: Please Please Me
    title: A Hard Day's Night
    a: 1.15
    b: 3.4
    silence: 5.0
```

* Change the global defaults at the top if you want.
* Individual song values always override the defaults.
* Existing entries are never overwritten by scan_originals.py.

## Scripts Overview

| Script              | Purpose                                              |
|---------------------|------------------------------------------------------|
| `scan_originals.py` | Discover new files, update YAML, create WAVs         |
| `process_one.py`    | Generate / regenerate one Name-That-Tune track       |
| `process_all.py`    | Full pipeline → final MP3s + PDF                     |

## Credits
* Scripts written by Grok (built by xAI).
* Feel free to use, modify, and share.
