#!/usr/bin/env python3
"""
Generates 100% compliant, evergreen voiceover for Monster AC530 using ElevenLabs Adam voice.
Captures exact word timestamps for synchronized Option 4 captions.
"""

import os
import sys
import json
import base64
from pathlib import Path
from elevenlabs.client import ElevenLabs

WORKSPACE = Path("/home/jeremy/Documents/antigravity/keen-rutherford")
ENV_FILE = WORKSPACE / ".env"
ASSETS_DIR = WORKSPACE / "assets/monster_ac530"

# Load API key
if ENV_FILE.exists():
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip("\"'"))

API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not API_KEY:
    sys.exit("ERROR: ELEVENLABS_API_KEY not found in .env")

SCRIPT_TEXT = (
    "If you still use bulky gaming headsets or in-ear earbuds that give you ear pain and sweat after two hours, stop scrolling. "
    "Heavy headsets crush your temples, while normal earbuds jam deep into your ear canal, completely blocking out your room awareness. "
    "That is why everyone is switching to the Monster AC530 Open Ear Earbuds. "
    "Instead of plugging inside your ears, they rest comfortably on the outside with zero-gravity titanium earhooks. "
    "You get crystal-clear directional audio from massive fourteen-point-two millimeter drivers with zero ear fatigue. "
    "They run on Bluetooth 6.0 with ultra-low gaming latency, so your footsteps and Discord calls stay in perfect sync. "
    "The charging case features an ingenious dual-folding design that slips right into your pocket. "
    "Plus, they are IPX5 sweat-proof for gaming marathons or workouts. "
    "You can grab these directly on TikTok Shop from the verified Monster store with fast shipping and manufacturer warranty. "
    "Tap the orange cart below to check current availability and deals before they sell out."
)

def main():
    client = ElevenLabs(api_key=API_KEY)
    voice_id = "pNInz6obpgDQGcFmaJgB" # Adam

    print(f"Synthesizing compliant voiceover with ElevenLabs ({voice_id})...")
    resp = client.text_to_speech.convert_with_timestamps(
        voice_id=voice_id,
        text=SCRIPT_TEXT,
        model_id="eleven_multilingual_v2",
        voice_settings={
            "stability": 0.45,
            "similarity_boost": 0.85,
            "style": 0.35,
            "use_speaker_boost": True
        }
    )

    audio_path = ASSETS_DIR / "voiceover_compliant.mp3"
    align_path = ASSETS_DIR / "voiceover_compliant_align.json"

    audio_bytes = base64.b64decode(resp.audio_base_64)
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)

    chars = resp.alignment.characters
    starts = resp.alignment.character_start_times_seconds
    ends = resp.alignment.character_end_times_seconds

    words = []
    curr_word = []
    w_start, w_end = None, None
    for c, s, e in zip(chars, starts, ends):
        if c == " " or c == "\n":
            if curr_word:
                words.append(("".join(curr_word), round(w_start, 3), round(w_end, 3)))
                curr_word = []
                w_start, w_end = None, None
        else:
            if w_start is None:
                w_start = s
            w_end = e
            curr_word.append(c)
    if curr_word:
        words.append(("".join(curr_word), round(w_start, 3), round(w_end, 3)))

    with open(align_path, "w", encoding="utf-8") as f:
        json.dump(words, f, indent=2)

    total_duration = words[-1][2] if words else 0.0
    print(f"Generated {len(words)} words.")
    print(f"Total audio duration: {total_duration:.2f}s")
    print(f"Saved audio: {audio_path}")
    print(f"Saved alignment: {align_path}")

if __name__ == "__main__":
    main()
