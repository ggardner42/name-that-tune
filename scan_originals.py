#!/usr/bin/env python3
"""
scan_originals.py

- Validates every file in originals/
- Expected format:
  NN -- Artist -- Album -- Title -- A -- B.ext
  (A and B are integers in milliseconds)

- If A/B are missing, renames the file using the current defaults
- Checks that all NN values are unique
- Warns about holes in the sequence (starting from 01)
"""

import re
import sys
from pathlib import Path
import yaml

ORIGINALS = Path("originals")
PARAMS_FILE = Path("params.yaml")
TEMP = Path("temp")

TEMP.mkdir(exist_ok=True)

DEFAULTS = {"a": 1000, "b": 3000}  # milliseconds

def load_defaults():
    if PARAMS_FILE.exists():
        with open(PARAMS_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return data.get("defaults", DEFAULTS)
    return DEFAULTS

def save_defaults(defaults):
    data = {"defaults": defaults}
    with open(PARAMS_FILE, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

def parse_stem(stem: str):
    """
    Returns (nn, artist, album, title, a, b) or None if invalid.
    a and b are ints in milliseconds (or None if missing).
    """
    parts = [p.strip() for p in stem.split(" -- ")]

    if len(parts) == 6:
        nn, artist, album, title, a_str, b_str = parts
        try:
            a = int(a_str)
            b = int(b_str)
            return nn, artist, album, title, a, b
        except ValueError:
            return None

    if len(parts) == 4:
        nn, artist, album, title = parts
        return nn, artist, album, title, None, None

    return None

def main():
    defaults = load_defaults()
    save_defaults(defaults)  # ensure file exists

    if not ORIGINALS.exists():
        print("originals/ folder not found")
        sys.exit(1)

    files = sorted(ORIGINALS.iterdir())
    seen_nn = {}
    problems = []
    renamed = 0

    for f in files:
        if not f.is_file():
            continue
        if f.suffix.lower() not in {".mp3", ".flac", ".wav", ".ogg", ".m4a", ".aac"}:
            continue

        parsed = parse_stem(f.stem)
        if parsed is None:
            problems.append(f"Invalid filename format: {f.name}")
            continue

        nn, artist, album, title, a, b = parsed

        # Validate NN
        if not re.fullmatch(r"\d{1,3}", nn):
            problems.append(f"Invalid NN '{nn}' in {f.name}")
            continue

        nn_int = int(nn)
        if nn in seen_nn:
            problems.append(f"Duplicate NN '{nn}': {seen_nn[nn]} and {f.name}")
        else:
            seen_nn[nn] = f.name

        # Fill in missing A/B by renaming
        if a is None or b is None:
            a = defaults["a"]
            b = defaults["b"]
            new_stem = f"{nn} -- {artist} -- {album} -- {title} -- {a} -- {b}"
            new_path = f.with_name(new_stem + f.suffix)
            print(f"Renaming (adding defaults): {f.name}")
            print(f"          → {new_path.name}")
            f.rename(new_path)
            renamed += 1

    if problems:
        print("\nErrors found:")
        for p in problems:
            print("  •", p)
        print("\nPlease fix the above problems and run again.")
        sys.exit(1)

    # Check for holes in sequence
    if seen_nn:
        numbers = sorted(int(n) for n in seen_nn)
        expected = list(range(1, max(numbers) + 1))
        missing = [n for n in expected if n not in numbers]
        if missing:
            print("\nWarning: gaps in NN sequence:")
            print("  Missing:", ", ".join(f"{n:02d}" for n in missing))

    print(f"\nScan complete. {len(seen_nn)} songs found.", end="")
    if renamed:
        print(f" {renamed} file(s) renamed with default a/b values.")
    else:
        print()

if __name__ == "__main__":
    main()
