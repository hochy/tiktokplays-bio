#!/usr/bin/env python3
"""
Generates compliant Option 4 ASS subtitles from word alignment JSON.
"""

import json
from pathlib import Path

ALIGN_PATH = Path("/home/jeremy/Documents/antigravity/keen-rutherford/assets/monster_ac530/voiceover_compliant_align.json")
ASS_PATH = Path("/home/jeremy/Documents/antigravity/keen-rutherford/assets/monster_ac530/captions_compliant.ass")

def sec_to_ass(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h}:{m:02d}:{sec:05.2f}"

def main():
    with open(ALIGN_PATH, "r", encoding="utf-8") as f:
        words = json.load(f)

    # Chunk into 3-4 words or split on punctuation
    chunks = []
    curr = []
    for item in words:
        w, start, end = item
        curr.append(item)
        if len(curr) >= 4 or w.endswith(('.', '!', '?', ',')):
            chunks.append(curr)
            curr = []
    if curr:
        chunks.append(curr)

    lines = [
        "[Script Info]",
        "Title: TikTok Compliant Product Captions",
        "ScriptType: v4.00+",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: TV.601",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: StyleWhiteShadow,Liberation Sans,62,&H00FFFFFF,&H00000000,&H00000000,&HFF000000,-1,0,0,0,100,100,0,0,1,6,5,2,40,40,580,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]

    for chunk in chunks:
        start_time = chunk[0][1]
        end_time = chunk[-1][2]
        text = " ".join([w[0] for w in chunk]).upper()
        # Clean double spaces
        text = " ".join(text.split())
        lines.append(f"Dialogue: 0,{sec_to_ass(start_time)},{sec_to_ass(end_time)},StyleWhiteShadow,,0,0,0,,{text}")

    with open(ASS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Generated {len(chunks)} caption dialogue events in {ASS_PATH}")

if __name__ == "__main__":
    main()
