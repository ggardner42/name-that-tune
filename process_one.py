#!/usr/bin/env python3
"""
process_one.py NN [--a SECONDS] [--b SECONDS]

- Creates temp/Current Tune Clue.mp3 for easy listening
- If -a or -b are given, updates the filename in originals/
  with the new values (in milliseconds)
"""

import argparse
import subprocess
import sys
from pathlib import Path
from pydub import AudioSegment

ORIGINALS = Path("originals")
TEMP = Path("temp")
TEMP.mkdir(exist_ok=True)

def find_song(nn: str):
    nn = nn.zfill(2) if nn.isdigit() else nn
    matches = list(ORIGINALS.glob(f"{nn} -- *"))
    if not matches:
        matches = list(ORIGINALS.glob(f"{int(nn)} -- *"))
    if len(matches) == 0:
        print(f"No song found with NN={nn}")
        sys.exit(1)
    if len(matches) > 1:
        print("Multiple matches:")
        for m in matches:
            print(" ", m.name)
        sys.exit(1)
    return matches[0]

def parse_stem(stem: str):
    parts = [p.strip() for p in stem.split(" -- ")]
    if len(parts) == 6:
        nn, artist, album, title, a_str, b_str = parts
        try:
            return nn, artist, album, title, int(a_str), int(b_str)
        except ValueError:
            pass
    if len(parts) == 4:
        nn, artist, album, title = parts
        return nn, artist, album, title, None, None
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("nn", help="Song number (e.g. 01 or 1)")
    parser.add_argument("-a", type=float, help="First clip length in seconds")
    parser.add_argument("-b", type=float, help="Second clip length in seconds")
    args = parser.parse_args()

    src = find_song(args.nn)
    parsed = parse_stem(src.stem)

    if parsed is None:
        print(f"Cannot parse filename: {src.name}")
        print("Run scan_originals.py first.")
        sys.exit(1)

    nn, artist, album, title, file_a, file_b = parsed

    # Determine the values we will use
    a_ms = int(round(args.a * 1000)) if args.a is not None else file_a
    b_ms = int(round(args.b * 1000)) if args.b is not None else file_b

    if a_ms is None or b_ms is None:
        print("Missing a/b values. Provide -a and -b or run scan_originals.py first.")
        sys.exit(1)

    print(f"Source : {src.name}")
    print(f"Using  : a={a_ms} ms, b={b_ms} ms")

    # Rename the original file if the values changed
    if (args.a is not None or args.b is not None) and (a_ms != file_a or b_ms != file_b):
        new_stem = f"{nn} -- {artist} -- {album} -- {title} -- {a_ms} -- {b_ms}"
        new_path = src.with_name(new_stem + src.suffix)

        if new_path.exists():
            print(f"ERROR: Target filename already exists:\n  {new_path.name}")
            sys.exit(1)

        print(f"Renaming:\n  {src.name}\n  → {new_path.name}")
        src.rename(new_path)
        src = new_path          # continue with the new path

    # Create the clue for listening
    temp_wav = TEMP / "current.wav"
    subprocess.run([
        "ffmpeg", "-y", "-i", str(src),
        "-ar", "44100", "-ac", "2", "-sample_fmt", "s16",
        str(temp_wav)
    ], check=True, capture_output=True)

    audio = AudioSegment.from_file(temp_wav)
    clip1 = audio[:a_ms]
    clip2 = audio[:b_ms]
    silence = AudioSegment.silent(duration=5000)

    clue = clip1 + silence + clip2 + silence

    out_mp3 = TEMP / "Current Tune Clue.mp3"
    # Quick encode for listening (you can change to lame -V2 if you prefer)
    clue.export(out_mp3, format="mp3", bitrate="192k")

    print(f"\nCreated: {out_mp3}")
    print("Listen to this file to check the timing.")

if __name__ == "__main__":
    main()
