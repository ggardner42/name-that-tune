#!/usr/bin/env python3
"""
Full pipeline using params.yaml
Creates final_mp3s/ + tracklist.pdf
"""

import subprocess
from pathlib import Path
import yaml
from pydub import AudioSegment
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

ORIGINALS = Path("originals")
WAVS = Path("wavs")
NTT = Path("ntt_wavs")
FINAL = Path("final_mp3s")
PARAMS_FILE = Path("params.yaml")

FINAL.mkdir(exist_ok=True)
NTT.mkdir(exist_ok=True)

def load_params():
    with open(PARAMS_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    data = load_params()
    songs = data.get("songs", {})
    defaults = data.get("defaults", {"a": 1.0, "b": 3.0, "silence": 5.0})

    # Sort by NN
    sorted_songs = sorted(songs.items(), key=lambda x: x[1].get("nn", "99"))

    tracklist_data = [["#", "Title", "Artist", "Album"]]

    for stem, info in sorted_songs:
        nn = info.get("nn", "00")
        artist = info.get("artist", "Unknown")
        album = info.get("album", "")
        title = info.get("title", stem)
        a = info.get("a", defaults["a"])
        b = info.get("b", defaults["b"])
        silence = info.get("silence", defaults.get("silence", 5.0))

        print(f"\n=== {nn}  {title} ===")

        # Ensure WAV exists
        wav = WAVS / f"{stem}.wav"
        if not wav.exists():
            orig = next(ORIGINALS.glob(f"{stem}.*"), None)
            if not orig:
                print("  Skipping – original not found")
                continue
            print("  Converting to WAV...")
            subprocess.run([
                "ffmpeg", "-y", "-i", str(orig),
                "-ar", "44100", "-ac", "2", "-sample_fmt", "s16",
                str(wav)
            ], check=True, capture_output=True)

        # Create NTT version
        ntt_wav = NTT / f"{stem}_ntt.wav"
        audio = AudioSegment.from_file(wav)
        clip1 = audio[:int(a * 1000)]
        clip2 = audio[:int(b * 1000)]
        sil = AudioSegment.silent(duration=int(silence * 1000))
        result = clip1 + sil + clip2 + sil + audio
        result.export(ntt_wav, format="wav")

        # Encode with LAME -V2
        mp3 = FINAL / f"{nn} - {artist} - {title}.mp3"
        print(f"  Encoding → {mp3.name}")
        subprocess.run([
            "lame", "-V2", "--vbr-new",
            str(ntt_wav), str(mp3)
        ], check=True, capture_output=True)

        # Tag with id3v2
        subprocess.run([
            "id3v2",
            "--song", title,
            "--artist", artist,
            "--album", album or "Name That Tune",
            "--track", nn,
            str(mp3)
        ], check=True)

        tracklist_data.append([nn, title, artist, album])

    # Generate PDF
    pdf_path = Path("tracklist.pdf")
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph("Name That Tune – Track List", styles["Title"]), Spacer(1, 16)]

    table = Table(tracklist_data, colWidths=[40, 220, 150, 150])
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
    print("All done. Final files are in final_mp3s/")

if __name__ == "__main__":
    main()
