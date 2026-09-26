#!/usr/bin/env python3
"""
Pre-Flight TikTok Shop & Creator Rewards Compliance Validator
Runs automated checks on video file, subtitles, and transcript before tablet deployment.
Fails with non-zero exit code if any critical violation is detected.
"""

import sys
import json
import re
import subprocess
from pathlib import Path

# Prohibited / Dangerous patterns in commercial affiliate content
PROHIBITED_PATTERNS = [
    (r'\$\s*\d+', "Specific dollar price mention ($)"),
    (r'\b\d+\s*(dollars?|cents?)\b', "Spoken/written currency amount"),
    (r'\b\d+%\s*(off)?\b', "Percentage discount claim"),
    (r'\bpercent\s*off\b', "Spoken percentage discount claim"),
    (r'\bflash\s*(sale|deal)\b', "Unsupported flash sale/deal claim"),
    (r'\blimited\s*time\s*deal\b', "Unsupported limited-time urgency claim"),
    (r'\b(cheapest|lowest\s*price)\s*(ever|in\s*the\s*world|online)\b', "Unsupported superlative pricing claim"),
    (r'\b(cure|cures|miracle|prevent\s*infection)\b', "Unsubstantiated medical/health claim"),
    (r'\b(link\s*in\s*(my\s*)?bio|bio\s*link|check\s*(the|my)\s*bio)\b', "External redirect away from TikTok Shop"),
]

MANDATORY_CTA_PATTERNS = [
    r'\borange\s*cart\b',
    r'\bcart\s*(down\s*)?below\b',
    r'\bshopping\s*cart\b',
]

def check_text_compliance(text_content: str, source_name: str) -> list:
    errors = []
    text_lower = text_content.lower()

    for pattern, reason in PROHIBITED_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            errors.append(f"[{source_name}] Prohibited pattern detected: '{match.group()}' -> {reason}")

    return errors

def check_video_file(video_path: Path) -> list:
    errors = []
    if not video_path.exists():
        return [f"Video file not found: {video_path}"]

    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size:stream=width,height,r_frame_rate,codec_type,codec_name",
        "-of", "json",
        str(video_path)
    ]
    try:
        output = subprocess.check_output(probe_cmd).decode()
        data = json.loads(output)
    except Exception as e:
        return [f"Failed to probe video: {e}"]

    # 1. Duration check
    duration = float(data.get("format", {}).get("duration", 0.0))
    if duration < 60.0:
        errors.append(f"Duration failure: {duration:.2f}s is less than 60.0s (Ineligible for Creator Rewards)")
    else:
        print(f"  ✓ Duration: {duration:.2f}s (>= 60.0s qualified)")

    # 2. Streams check
    v_streams = [s for s in data.get("streams", []) if s.get("codec_type") == "video"]
    a_streams = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]

    if not v_streams:
        errors.append("No video stream found.")
    else:
        v = v_streams[0]
        w = int(v.get("width", 0))
        h = int(v.get("height", 0))
        if w != 1080 or h != 1920:
            errors.append(f"Resolution mismatch: {w}x{h} (Must be 1080x1920 vertical 9:16)")
        else:
            print(f"  ✓ Resolution: {w}x{h} (Vertical 9:16 verified)")

    if not a_streams:
        errors.append("No audio stream found (Video must have clear narration).")
    else:
        a = a_streams[0]
        codec = a.get("codec_name")
        print(f"  ✓ Audio stream present: {codec}")

    return errors

def main():
    video_path = Path("/home/jeremy/PhoneShare/monster_ac530_product_showcase.mp4")
    ass_path = Path("/home/jeremy/Documents/antigravity/keen-rutherford/assets/monster_ac530/captions_compliant.ass")
    align_path = Path("/home/jeremy/Documents/antigravity/keen-rutherford/assets/monster_ac530/voiceover_compliant_align.json")

    print("==================================================")
    print("  TIKTOK SHOP PRE-FLIGHT COMPLIANCE VERIFICATION  ")
    print("==================================================")

    all_errors = []

    # Check 1: Audio Transcript / Alignment Text
    print("\n[1/4] Verifying Spoken Voiceover Script...")
    if align_path.exists():
        with open(align_path, "r", encoding="utf-8") as f:
            words_data = json.load(f)
        spoken_text = " ".join([w[0] for w in words_data])
        t_errors = check_text_compliance(spoken_text, "Voiceover Transcript")
        all_errors.extend(t_errors)

        has_cta = any(re.search(p, spoken_text.lower()) for p in MANDATORY_CTA_PATTERNS)
        if not has_cta:
            all_errors.append("[Voiceover Transcript] Missing mandatory Orange Cart CTA.")
        else:
            print("  ✓ Spoken Orange Cart CTA verified.")

        if not t_errors:
            print("  ✓ Zero prohibited words / price claims in voiceover.")
    else:
        all_errors.append(f"Voiceover alignment file not found: {align_path}")

    # Check 2: Subtitle File (ASS)
    print("\n[2/4] Verifying On-Screen Subtitles (ASS)...")
    if ass_path.exists():
        sub_text = ass_path.read_text(encoding="utf-8")
        s_errors = check_text_compliance(sub_text, "Captions ASS")
        all_errors.extend(s_errors)
        if not s_errors:
            print("  ✓ Zero prohibited words / price claims in subtitles.")
    else:
        all_errors.append(f"ASS subtitle file not found: {ass_path}")

    # Check 3: Video File Specs
    print("\n[3/4] Verifying Rendered Video Specs...")
    v_errors = check_video_file(video_path)
    all_errors.extend(v_errors)

    # Check 4: Summary Result
    print("\n--------------------------------------------------")
    if all_errors:
        print(f"❌ COMPLIANCE CHECK FAILED ({len(all_errors)} errors):")
        for err in all_errors:
            print(f"   - {err}")
        print("--------------------------------------------------")
        sys.exit(1)
    else:
        print("✅ 100% COMPLIANCE VERIFIED: Video is safe to upload.")
        print("   - No hardcoded prices or unauthorized sale claims.")
        print("   - Compliant Orange Cart CTA confirmed.")
        print("   - Creator Rewards duration threshold met (>60s).")
        print("   - 1080x1920 9:16 vertical standard confirmed.")
        print("--------------------------------------------------")
        sys.exit(0)

if __name__ == "__main__":
    main()
