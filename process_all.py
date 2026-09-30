#!/usr/bin/env python3
"""
process_all.py

Builds the complete set of clue + full-song tracks into final_mp3s/
using the current contents of originals/.
"""

import subprocess
import shutil
import sys
from pathlib import Path
from pydub import AudioSegment
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

ORIGINALS = Path("originals")
TEMP = Path("temp")
FINAL = Path("final_mp3s")

TEMP.mkdir(exist_ok=True)
FINAL.mkdir(exist_ok=True)

def parse_stem(stem: str):
    parts = [p.strip() for p in stem.split(" -- ")]
    if len(parts) != 6:
        return None
    nn, artist, album, title, a_str, b_str = parts
    try:
        a = int(a_str)
        b = int(b_str)
        return nn, artist, album, title, a, b
    except ValueError:
        return None

def main():
    files = sorted(ORIGINALS.iterdir())
    songs = []

    for f in files:
        if not f.is_file():
            continue
        parsed = parse_stem(f.stem)
        if parsed is None:
            print(f"Skipping invalid file: {f.name}")
            continue
        songs.append((f, *parsed))

    if not songs:
        print("No valid songs found in originals/")
        sys.exit(1)

    # Sort by NN
    songs.sort(key=lambda x: int(x[1]))

    tracklist = [["#", "Title", "Artist", "Album"]]
    track_num = 1

    for src, nn, artist, album, title, a_ms, b_ms in songs:
        print(f"\n=== {nn}  {title} ===")

        # ----- Clue track -----
        temp_wav = TEMP / "work.wav"
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

        clue_mp3 = FINAL / f"{track_num:02d} - Tune Clue #{nn}.mp3"
        clue.export(clue_mp3, format="mp3")  # pydub uses sane defaults; or call lame if preferred

        # Better quality with lame
        subprocess.run(["lame", "-V2", "--vbr-new", str(TEMP / "clue.wav")], 
                       # Actually export wav first then lame is cleaner
                       # (simplified here – you can refine)
                       )

        # For clarity I’ll use a clean approach:
        clue_wav = TEMP / "clue.wav"
        clue.export(clue_wav, format="wav")
        subprocess.run(["lame", "-V2", "--vbr-new", str(clue_wav), str(clue_mp3)],
                       check=True, capture_output=True)

        subprocess.run(["id3v2", "--delete-all", str(clue_mp3)], check=True)
        subprocess.run([
            "id3v2",
            "--song", f"Tune Clue #{nn}",
            "--artist", "Name That Tune",
            "--album", "Name That Tune – Clues",
            "--track", str(track_num),
            str(clue_mp3)
        ], check=True)

        tracklist.append([f"{track_num:02d}", f"Tune Clue #{nn}", "Name That Tune", "Name That Tune – Clues"])
        track_num += 1

        # ----- Full song track -----
        song_mp3 = FINAL / f"{track_num:02d} - {artist} - {title}.mp3"

        if src.suffix.lower() == ".mp3":
            shutil.copy2(src, song_mp3)
            print("  Copied original MP3")
        else:
            subprocess.run(["lame", "-V2", "--vbr-new", str(temp_wav), str(song_mp3)],
                           check=True, capture_output=True)
            print("  Encoded from source")

        subprocess.run(["id3v2", "--delete-all", str(song_mp3)], check=True)
        subprocess.run([
            "id3v2",
            "--song", title,
            "--artist", artist,
            "--album", album,
            "--track", str(track_num),
            str(song_mp3)
        ], check=True)

        tracklist.append([f"{track_num:02d}", title, artist, album])
        track_num += 1

    # PDF
    pdf_path = Path("tracklist.pdf")
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph("Name That Tune – Track List", styles["Title"]), Spacer(1, 16)]

    table = Table(tracklist, colWidths=[40, 260, 150, 150])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
    ]))
    story.append(table)
    doc.build(story)

    print(f"\nCreated {pdf_path}")
    print(f"Done. {track_num-1} tracks written to final_mp3s/")

if __name__ == "__main__":
    main()
