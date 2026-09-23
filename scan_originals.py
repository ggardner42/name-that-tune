#!/usr/bin/env python3
"""
scan_originals.py
- Reads everything in originals/
- Updates / creates params.yaml (preserves existing defaults and song settings)
- Converts any missing files to wavs/
"""

import re
import subprocess
from pathlib import Path
import yaml

ORIGINALS = Path("originals")
WAVS = Path("wavs")
PARAMS_FILE = Path("params.yaml")

WAVS.mkdir(exist_ok=True)

def parse_filename(stem: str):
    """Parse 'NN -- Artist -- Album -- Title' """
    parts = [p.strip() for p in stem.split(" -- ")]
    if len(parts) >= 4:
        nn, artist, album, title = parts[0], parts[1], parts[2], " -- ".join(parts[3:])
    elif len(parts) == 3:
        nn, artist, title = parts
        album = ""
    else:
        nn = parts[0] if parts else "00"
        artist = album = ""
        title = stem
    return nn, artist, album, title

def load_params():
    if PARAMS_FILE.exists():
        with open(PARAMS_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

def save_params(data):
    with open(PARAMS_FILE, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

def main():
    data = load_params()

    # Ensure defaults exist (but never overwrite if user already set them)
    if "defaults" not in data:
        data["defaults"] = {"a": 1.0, "b": 3.0, "silence": 5.0}
    defaults = data["defaults"]

    if "songs" not in data:
        data["songs"] = {}

    songs = data["songs"]
    changed = False

    for f in sorted(ORIGINALS.iterdir()):
        if f.suffix.lower() not in {".flac", ".mp3", ".wav", ".ogg", ".m4a", ".aac"}:
            continue

        stem = f.stem
        nn, artist, album, title = parse_filename(stem)

        # Add missing entry
        if stem not in songs:
            songs[stem] = {
                "nn": nn,
                "artist": artist,
                "album": album,
                "title": title,
                "a": defaults["a"],
                "b": defaults["b"],
                "silence": defaults.get("silence", 5.0),
            }
            print(f"Added new song: {stem}")
            changed = True

        # Convert to WAV if missing
        wav_path = WAVS / f"{stem}.wav"
        if not wav_path.exists():
            print(f"Converting → {wav_path.name}")
            subprocess.run([
                "ffmpeg", "-y", "-i", str(f),
                "-ar", "44100", "-ac", "2", "-sample_fmt", "s16",
                str(wav_path)
            ], check=True, capture_output=True)

    if changed:
        save_params(data)
        print("params.yaml updated.")
    else:
        print("No new songs found. params.yaml unchanged.")

if __name__ == "__main__":
    main()
