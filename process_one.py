#!/usr/bin/env python3
"""
process_one.py  01
or
process_one.py "Hard Day"
"""

import argparse
import sys
from pathlib import Path
import yaml
from pydub import AudioSegment

WAVS = Path("wavs")
NTT = Path("ntt_wavs")
PARAMS_FILE = Path("params.yaml")

NTT.mkdir(exist_ok=True)

def load_params():
    with open(PARAMS_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def find_song(key: str, songs: dict):
    # Exact NN match first
    for stem, info in songs.items():
        if info.get("nn") == key.zfill(2) or info.get("nn") == key:
            return stem, info
    # Partial match on stem or title
    key_lower = key.lower()
    matches = [(s, i) for s, i in songs.items()
               if key_lower in s.lower() or key_lower in i.get("title", "").lower()]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print("Multiple matches:")
        for s, _ in matches:
            print("  ", s)
        sys.exit(1)
    print(f"No song found matching '{key}'")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("key", help="NN number (e.g. 01) or partial title")
    args = parser.parse_args()

    data = load_params()
    songs = data.get("songs", {})
    defaults = data.get("defaults", {"a": 1.0, "b": 3.0, "silence": 5.0})

    stem, info = find_song(args.key, songs)

    a = info.get("a", defaults["a"])
    b = info.get("b", defaults["b"])
    silence = info.get("silence", defaults.get("silence", 5.0))

    wav = WAVS / f"{stem}.wav"
    if not wav.exists():
        print(f"Missing WAV: {wav}")
        sys.exit(1)

    print(f"Processing: {stem}")
    print(f"  a={a}  b={b}  silence={silence}")

    audio = AudioSegment.from_file(wav)
    clip1 = audio[:int(a * 1000)]
    clip2 = audio[:int(b * 1000)]
    sil = AudioSegment.silent(duration=int(silence * 1000))

    result = clip1 + sil + clip2 + sil + audio

    out = NTT / f"{stem}_ntt.wav"
    result.export(out, format="wav")
    print(f"Created: {out}")

if __name__ == "__main__":
    main()
