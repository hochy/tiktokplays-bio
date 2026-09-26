#!/usr/bin/env python3
"""
Fully Automated Reddit Story Video Engine for @tiktokplaygames.
Combines:
- Viral Reddit story narrative
- Cold-Open Hook: Frame 0:00 starts immediately on the Reddit Dark Mode Card
  (guaranteeing TikTok automatically uses it as the profile grid thumbnail cover)
- Branding Stinger: 1.5s "TikTok Plays Original" bumper flashes as a cinematic transition into the story
- Dual TTS Engine: ElevenLabs (with word timestamps & local cache) + Edge-TTS fallback
- Option 4 Captions: Clean pure white text with 6px black outline & 5px deep drop shadow
- 1080x1920 60fps Minecraft parkour background
- Automated CapCut / mobile compatible MP4 export
"""

import os
import sys
import json
import re
import base64
import hashlib
import shutil
import subprocess
from pathlib import Path
from reddit_card_generator import generate_reddit_card

VENV_PYTHON = "/home/jeremy/Documents/antigravity/keen-rutherford/toolkit/venv/bin/python3"
EDGE_TTS_BIN = "/home/jeremy/Documents/antigravity/keen-rutherford/toolkit/venv/bin/edge-tts"
REPO_ROOT = Path(__file__).parent.parent
LOCAL_BUMPER = REPO_ROOT / "assets" / "branding" / "intro_bumper_ready.mp4"
INTRO_BUMPER = str(LOCAL_BUMPER) if LOCAL_BUMPER.exists() else "/home/jeremy/PhoneShare/tiktok_working/branding/intro_bumper_ready.mp4"
OUTPUT_DIR = "/home/jeremy/PhoneShare"

def load_env():
    env_file = Path("/home/jeremy/Documents/antigravity/keen-rutherford/.env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("\"'"))

load_env()

# Acronyms with case sensitivity to prevent collisions with normal words like "so"
ACRONYM_MAP_CASE_SENSITIVE = {
    r"\bSO\b": "partner",
    r"\bS/O\b": "partner",
    r"\bS\.O\.\b": "partner",
    r"\bOP\b": "the original poster",
}

ACRONYM_MAP_CASE_INSENSITIVE = {
    r"\bTIFU\b": "Today I messed up",
    r"\bAITA\b": "Am I the jerk",
    r"\bWIBTA\b": "Would I be the bad guy",
    r"\bAIO\b": "Am I overreacting",
    r"\bTL;?DR\b": "Too long didn't read",
    r"\bMIL\b": "mother-in-law",
    r"\bFIL\b": "father-in-law",
    r"\bSIL\b": "sister-in-law",
    r"\bBIL\b": "brother-in-law",
}

def normalize_spoken_text(text):
    """Replaces Reddit acronyms with natural spoken English for voiceover and subtitles."""
    for pattern, replacement in ACRONYM_MAP_CASE_SENSITIVE.items():
        text = re.sub(pattern, replacement, text)
    for pattern, replacement in ACRONYM_MAP_CASE_INSENSITIVE.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

CAPTION_STYLES = {
    "white_shadow": {
        "name": "StyleWhiteShadow",
        "label": "CLEAN WHITE + DEEP SHADOW",
        "style_def": "Style: StyleWhiteShadow,Liberation Sans,62,&H00FFFFFF,&H00000000,&H00000000,&HFF000000,-1,0,0,0,100,100,0,0,1,6,5,2,40,40,780,1"
    },
    "yellow": {
        "name": "StyleYellow",
        "label": "CLASSIC TIKTOK YELLOW",
        "style_def": "Style: StyleYellow,Liberation Sans,62,&H0000FFFF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5.5,2,2,40,40,780,1"
    },
    "green": {
        "name": "StyleGreen",
        "label": "HORMOZI NEON GREEN",
        "style_def": "Style: StyleGreen,Liberation Sans,62,&H0032FF7E,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5.5,2,2,40,40,780,1"
    },
    "box": {
        "name": "StyleBoxPill",
        "label": "TRANSLUCENT BOXED PILL",
        "style_def": "Style: StyleBoxPill,Liberation Sans,58,&H00FFFFFF,&H00000000,&H00000000,&HD0000000,-1,0,0,0,100,100,0,0,3,16,0,2,40,40,780,1"
    }
}

HEADER_BADGE_STYLE = "Style: HeaderBadge,Liberation Sans,38,&H00FFFFFF,&H00000000,&H00000000,&HB0000000,-1,0,0,0,100,100,0,0,3,12,0,8,40,40,320,1"

SAMPLE_STORIES = {
    "wave_doubling_down": {
        "subreddit": "r/tifu",
        "author": "u/RedditWaveGuy",
        "time_str": "8 hr. ago",
        "upvotes": "28.4k",
        "comments": "1.6k",
        "voice": "en-US-BrianNeural",
        "rate": "+5%",
        "eleven_voice_id": "pNInz6obpgDQGcFmaJgB", # Adam (classic viral TikTok narrator)
        "title": "TIFU by waving back at someone who was waving at the person behind me, and doubling down for three years",
        "body": (
            "So about three years ago, I was walking across my college campus when a guy in a bright red hoodie "
            "made direct eye contact with me, smiled, and gave a huge, enthusiastic wave. "
            "Without thinking, I smiled back, waved with both hands, and shouted, 'Hey man, good to see you!' "
            "Right as the words left my mouth, he walked straight past my shoulder and gave a massive bro-hug to a dude "
            "standing directly behind me. I had never seen either of them in my entire life. "
            "Instead of laughing it off like a normal human being, my brain completely panicked. "
            "I didn't want to look like an idiot, so every single time I saw Red Hoodie on campus for the next three years, "
            "I committed to the bit. I gave him a nod, said 'What's up bro,' and he started nodding back, clearly thinking "
            "we were friends who met at a party he forgot about. "
            "Fast forward to graduation day yesterday. We were standing in line waiting for our diplomas, and he taps my shoulder "
            "and goes, 'Hey man, real talk, what's your name? I've felt too awkward to ask for three years.' "
            "I told him the truth about the wave from freshman year, and he laughed so hard he dropped his cap. "
            "We're getting drinks this weekend."
        )
    },
    "wedding_photographer": {
        "subreddit": "r/AmItheAsshole",
        "author": "u/LensCrafter99",
        "time_str": "12 hr. ago",
        "upvotes": "34.1k",
        "comments": "3.8k",
        "voice": "en-US-GuyNeural",
        "rate": "+5%",
        "eleven_voice_id": "VR6AewLTigWG4xSOukaG", # Josh (conversational, expressive)
        "title": "AITA for deleting all the wedding photos in front of the groom after he refused to feed me or let me drink water?",
        "body": (
            "I am not a professional photographer, but a friend of mine was getting married and was on a razor-thin budget. "
            "I told him I’d shoot their entire eight-hour wedding for just two hundred and fifty dollars, which is basically free. "
            "On the day of the wedding, I was on my feet from eleven in the morning until seven at night with zero breaks. "
            "Around seven-thirty, the food was served. I walked over to the catering table, and the groom stopped me. "
            "He literally told me I wasn't allowed to eat because I was hired help, and if I wanted to sit down or drink water, "
            "I had to deduct thirty minutes of pay. The reception was in a barn in ninety-degree heat with no AC. "
            "I was completely dehydrated and exhausted. I looked the groom straight in the eye and said, 'Either you let me eat a plate "
            "and drink water for twenty minutes, or I leave right now.' "
            "He laughed in my face and told me to get back to shooting or he wouldn't pay me a cent. "
            "So right in front of him, I went into my camera settings, hit 'Select All', pressed 'Delete', and walked out to my car. "
            "His new mother-in-law called me screaming, but half the wedding party texted me saying the groom had it coming."
        )
    },
    "monster_headset": {
        "subreddit": "r/gaming",
        "author": "u/NightShiftGamer",
        "time_str": "7 hr. ago",
        "upvotes": "38.9k",
        "comments": "2.4k",
        "voice": "en-US-BrianNeural",
        "rate": "+5%",
        "eleven_voice_id": "pNInz6obpgDQGcFmaJgB", # Adam (classic viral TikTok narrator)
        "title": "I was clutching a 1v3 in Discord at 3 AM when my teammate asked who was standing behind my chair",
        "body": (
            "I was testing out this new Monster AC530 open-ear gaming headset. The mic noise cancellation is insane "
            "and because it's open-ear you can hear your actual room while still getting full surround sound. "
            "I put the link down below if you need a gaming headset while the sale is active. "
            "Anyway, it was 3:15 AM and I was the last one alive in a 1v3 clutch. My whole squad was dead in Discord "
            "listening to my stream. All of a sudden, through the open-ear mic, my teammate screams: 'Bro, who is standing behind your chair?' "
            "I thought he was just trolling to make me lose focus. But then my other friend said, 'Dude I'm not kidding, "
            "someone just walked past your bedroom doorway.' "
            "I live completely alone on the third floor of an apartment complex. "
            "I pulled off the headset, turned around slowly, and the deadbolt on my front door was turned completely vertical. "
            "Check the link down below for the headset with 100-hour battery, and follow for what the security cameras caught in the hallway."
        )
    }
}


def parse_vtt_timestamp(ts):
    parts = ts.strip().split(':')
    h = int(parts[0])
    m = int(parts[1])
    s_parts = parts[2].replace(',', '.').split('.')
    sec = int(s_parts[0])
    ms = int(s_parts[1]) if len(s_parts) > 1 else 0
    return h * 3600 + m * 60 + sec + ms / 1000.0

def sec_to_ass_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def split_cue_into_phrases(cue_text, start_sec, end_sec, words_per_phrase=4):
    words = cue_text.split()
    if not words:
        return []
    total_dur = end_sec - start_sec
    total_chars = sum(len(w) for w in words)
    if total_chars == 0:
        return []
    phrases = []
    chunk = []
    for w in words:
        chunk.append(w)
        if len(chunk) >= words_per_phrase or w.endswith(('.', '!', '?', ',')):
            phrases.append(chunk)
            chunk = []
    if chunk:
        if len(chunk) <= 2 and len(phrases) > 0:
            phrases[-1].extend(chunk)
        else:
            phrases.append(chunk)
    result = []
    curr_time = start_sec
    for p in phrases:
        phrase_text = " ".join(p)
        phrase_chars = sum(len(w) for w in p)
        dur = total_dur * (phrase_chars / total_chars)
        p_start = curr_time
        p_end = curr_time + dur
        curr_time = p_end
        result.append((p_start, p_end, phrase_text))
    return result

def build_ass_subtitles(phrases, ass_path, caption_style="white_shadow", time_offset=0.0):
    """
    Builds the ASS subtitle file.
    time_offset: subtracted from phrase timestamps when applied to a trimmed body segment.
    """
    if caption_style == "showcase":
        style_lines = [
            HEADER_BADGE_STYLE,
            CAPTION_STYLES["yellow"]["style_def"],
            CAPTION_STYLES["green"]["style_def"],
            CAPTION_STYLES["box"]["style_def"],
            CAPTION_STYLES["white_shadow"]["style_def"]
        ]
    else:
        st = CAPTION_STYLES.get(caption_style, CAPTION_STYLES["white_shadow"])
        style_lines = [st["style_def"]]

    ass_header = f"""[Script Info]
Title: TikTok Automated Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{chr(10).join(style_lines)}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    n = len(phrases)
    if caption_style == "showcase" and n > 0:
        quarters = [
            ("yellow", 0, n // 4),
            ("green", n // 4, 2 * (n // 4)),
            ("box", 2 * (n // 4), 3 * (n // 4)),
            ("white_shadow", 3 * (n // 4), n)
        ]
        for idx, (st_key, start_idx, end_idx) in enumerate(quarters):
            if start_idx >= end_idx or start_idx >= n:
                continue
            section_phrases = phrases[start_idx:min(end_idx, n)]
            sec_start = max(0.0, section_phrases[0][0] - time_offset)
            sec_end = max(0.0, section_phrases[-1][1] - time_offset)
            st_info = CAPTION_STYLES[st_key]
            
            # Header badge dialogue
            header_text = f"OPTION {idx+1}: {st_info['label']}"
            events.append(f"Dialogue: 0,{sec_to_ass_time(sec_start)},{sec_to_ass_time(sec_end)},HeaderBadge,,0,0,0,,{header_text}\n")
            
            # Phrase dialogues
            for p_start, p_end, p_text in section_phrases:
                p_s = max(0.0, p_start - time_offset)
                p_e = max(0.0, p_end - time_offset)
                formatted_text = p_text.upper()
                events.append(f"Dialogue: 0,{sec_to_ass_time(p_s)},{sec_to_ass_time(p_e)},{st_info['name']},,0,0,0,,{formatted_text}\n")
    else:
        st_name = CAPTION_STYLES.get(caption_style, CAPTION_STYLES["white_shadow"])["name"]
        for p_start, p_end, p_text in phrases:
            p_s = max(0.0, p_start - time_offset)
            p_e = max(0.0, p_end - time_offset)
            formatted_text = p_text.upper()
            events.append(f"Dialogue: 0,{sec_to_ass_time(p_s)},{sec_to_ass_time(p_e)},{st_name},,0,0,0,,{formatted_text}\n")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header)
        f.writelines(events)
        
    print(f"Generated ASS subtitle file: {ass_path} ({len(events)} events, style: {caption_style.upper()}, offset: {time_offset:.2f}s)")

def vtt_to_ass(vtt_path, ass_path, title_end_time, caption_style="white_shadow", time_offset=0.0):
    with open(vtt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    cues = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "-->" in line:
            parts = line.split("-->")
            start = parse_vtt_timestamp(parts[0])
            end = parse_vtt_timestamp(parts[1])
            i += 1
            text_lines = []
            while i < len(lines) and lines[i].strip() != "" and not lines[i].strip().isdigit():
                text_lines.append(lines[i].strip())
                i += 1
            cue_text = " ".join(text_lines)
            cues.append((start, end, cue_text))
        else:
            i += 1
            
    phrases = []
    for idx, (start, end, text) in enumerate(cues):
        if idx == 0:
            continue
        if start < title_end_time:
            start = title_end_time
        sub_phrases = split_cue_into_phrases(text, start, end, words_per_phrase=4)
        phrases.extend(sub_phrases)
        
    build_ass_subtitles(phrases, ass_path, caption_style=caption_style, time_offset=time_offset)

def synthesize_with_elevenlabs(full_text, title_word_count, voice_id, audio_path, ass_path, caption_style="white_shadow", time_offset=0.0, force_tts=False, model_id="eleven_flash_v2_5"):
    temp_dir = Path("/tmp/video_engine")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    text_hash = hashlib.md5(f"{voice_id}_{model_id}_{full_text}".encode()).hexdigest()[:10]
    cached_audio = temp_dir / f"eleven_{text_hash}.mp3"
    cached_align = temp_dir / f"eleven_{text_hash}_align.json"
    
    if cached_audio.exists() and cached_align.exists() and not force_tts:
        print(f"⚡ Reusing cached ElevenLabs audio & timestamps ({text_hash})...")
        words = json.loads(cached_align.read_text(encoding="utf-8"))
        with open(cached_audio, "rb") as src, open(audio_path, "wb") as dst:
            dst.write(src.read())
    else:
        from elevenlabs.client import ElevenLabs
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY is not set.")
            
        client = ElevenLabs(api_key=api_key)
        print(f"🎙️ Synthesizing voiceover with ElevenLabs Flash (Voice ID: {voice_id}, Model: {model_id})...")
        
        resp = client.text_to_speech.convert_with_timestamps(
            voice_id=voice_id,
            text=full_text,
            model_id=model_id,
            voice_settings={
                "stability": 0.45,
                "similarity_boost": 0.85,
                "style": 0.35,
                "use_speaker_boost": True
            }
        )
        
        audio_bytes = base64.b64decode(resp.audio_base_64)
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)
        with open(cached_audio, "wb") as f:
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
                    words.append(("".join(curr_word), w_start, w_end))
                    curr_word = []
                    w_start, w_end = None, None
            else:
                if w_start is None:
                    w_start = s
                w_end = e
                curr_word.append(c)
        if curr_word:
            words.append(("".join(curr_word), w_start, w_end))
            
        cached_align.write_text(json.dumps(words), encoding="utf-8")
        
    title_end_time = words[title_word_count - 1][2] if title_word_count <= len(words) else 5.0
    body_words = words[title_word_count:]
    
    phrases = []
    chunk = []
    for item in body_words:
        w, s, e = item
        chunk.append(item)
        if len(chunk) >= 4 or w.endswith(('.', '!', '?', ',')):
            p_text = " ".join([x[0] for x in chunk])
            phrases.append((chunk[0][1], chunk[-1][2], p_text))
            chunk = []
    if chunk:
        p_text = " ".join([x[0] for x in chunk])
        phrases.append((chunk[0][1], chunk[-1][2], p_text))
        
    build_ass_subtitles(phrases, ass_path, caption_style=caption_style, time_offset=time_offset)
    return title_end_time

def build_automated_video(story_key="wave_doubling_down", story_data=None, output_filename="reddit_story_production.mp4", voice=None, rate=None, engine=None, caption_style="white_shadow", include_intro=True, force_tts=False, model="eleven_flash_v2_5", bg_offset=0.0):
    if story_data:
        story = story_data
    else:
        story = SAMPLE_STORIES.get(story_key)
        if not story:
            raise ValueError(f"Unknown story key: {story_key}")
        
    has_eleven = bool(os.environ.get("ELEVENLABS_API_KEY"))
    if engine is None:
        engine = "elevenlabs" if has_eleven else "edge"
        
    temp_dir = Path("/tmp/video_engine")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    card_path = str(temp_dir / "title_card.png")
    audio_path = str(temp_dir / "narration.mp3")
    vtt_path = str(temp_dir / "narration.vtt")
    ass_path = str(temp_dir / "captions.ass")
    
    out_p = Path(output_filename)
    if out_p.is_absolute():
        final_output = str(out_p)
        cover_dir = out_p.parent / "covers"
    else:
        final_output = str(Path(OUTPUT_DIR) / output_filename)
        cover_dir = Path(OUTPUT_DIR) / "covers"
    out_p.parent.mkdir(parents=True, exist_ok=True)
    
    has_intro = include_intro and os.path.exists(INTRO_BUMPER)
    
    print("\n=======================================================")
    print(f"🎬 BUILDING AUTOMATED TIKTOK/SHORTS VIDEO: {story['subreddit']}")
    print(f"📖 Title: {story['title']}")
    print(f"🎙️ Engine: {engine.upper()} (Model: {model})")
    print(f"🎨 Caption Style: {caption_style.upper()}")
    print(f"💥 Cold-Open Branding Stinger: {has_intro}")
    print(f"⏱️ Background Offset: {bg_offset:.2f}s")
    print("=======================================================\n")
    
    # 1. Generate Reddit Title Card
    print("Step 1/5: Generating pixel-perfect Reddit title card...")
    generate_reddit_card(
        subreddit=story["subreddit"],
        author=story["author"],
        time_str=story["time_str"],
        title=story["title"],
        upvotes=story["upvotes"],
        comments=story["comments"],
        output_path=card_path
    )
    
    # Also save dedicated high-res cover image in covers directory
    cover_dir.mkdir(parents=True, exist_ok=True)
    cover_file = cover_dir / f"{out_p.stem}_cover.png"
    shutil.copyfile(card_path, str(cover_file))
    print(f"🖼️ Saved high-res cover image: {cover_file}")
    
    # 2. Normalize Text
    spoken_title = normalize_spoken_text(story["title"])
    spoken_body = normalize_spoken_text(story["body"])
    full_text = f"{spoken_title}. {spoken_body}"
    title_word_count = len(spoken_title.split())
    
    print(f"Step 2/5: Synthesizing voiceover ({engine})...")
    print(f"🗣️ Normalized Spoken Hook: \"{spoken_title}\"")
    
    if engine == "elevenlabs":
        voice_id = voice or story.get("eleven_voice_id", "pNInz6obpgDQGcFmaJgB") # Adam
        # First get title_end_time
        title_end_time = synthesize_with_elevenlabs(
            full_text=full_text,
            title_word_count=title_word_count,
            voice_id=voice_id,
            audio_path=audio_path,
            ass_path=ass_path,
            caption_style=caption_style,
            time_offset=0.0,
            force_tts=force_tts,
            model_id=model
        )
    else:
        voice = voice or story.get("voice", "en-US-BrianNeural")
        rate = rate or story.get("rate", "+5%")
        story_txt_path = temp_dir / "story.txt"
        story_txt_path.write_text(full_text, encoding="utf-8")
        tts_cmd = [
            EDGE_TTS_BIN,
            "--file", str(story_txt_path),
            "--write-media", audio_path,
            "--write-subtitles", vtt_path,
            "--voice", voice,
            "--rate", rate
        ]
        subprocess.run(tts_cmd, check=True)
        with open(vtt_path, "r", encoding="utf-8") as f:
            vtt_content = f.read()
        m = re.search(r"-->\s*([0-9:,.]+)", vtt_content)
        title_end_time = parse_vtt_timestamp(m.group(1)) if m else 6.0
        vtt_to_ass(vtt_path, ass_path, title_end_time, caption_style=caption_style, time_offset=0.0)
        
    # Measure audio duration
    ffprobe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    audio_dur = float(subprocess.check_output(ffprobe_cmd).decode().strip())
    
    hook_dur = round(title_end_time + 0.25, 2)
    total_est = audio_dur + (1.5 if has_intro else 0.0)
    print(f"🎙️ Narration duration: {audio_dur:.2f}s | Hook: {hook_dur:.2f}s | Total video duration: ~{total_est:.2f}s")
    print(f"🃏 Cold-Open Reddit Card displays at 0:00 (guaranteeing auto-cover on TikTok profile grid)")
    
    # If Cold-Open Stinger is active, re-generate ASS subtitles with time_offset=hook_dur
    if has_intro:
        if engine == "elevenlabs":
            synthesize_with_elevenlabs(
                full_text=full_text,
                title_word_count=title_word_count,
                voice_id=voice_id,
                audio_path=audio_path,
                ass_path=ass_path,
                caption_style=caption_style,
                time_offset=hook_dur,
                force_tts=False,
                model_id=model
            )
        else:
            vtt_to_ass(vtt_path, ass_path, title_end_time, caption_style=caption_style, time_offset=hook_dur)
            
    # 5. Assemble Video via FFmpeg
    print(f"\nStep 4/5: Assembling video with FFmpeg...")
    
    if has_intro:
        print(f"🎬 Cold-Open Flow: Hook (0.00s-{hook_dur:.2f}s) -> Bumper (1.50s) -> Body Subtitles...")
        vf = (
            f"[0:v]trim={bg_offset:.2f}:{bg_offset + hook_dur:.2f},setpts=PTS-STARTPTS,fps=30,setsar=1:1,format=yuv420p[hook_bg];"
            f"[1:v]format=rgba[card];"
            f"[hook_bg][card]overlay=(W-w)/2:(H-h)/2 - 120[hook_v];"
            f"[2:a]atrim=0:{hook_dur:.2f},asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo:sample_rates=44100[hook_a];"
            f"[3:v]fps=30,setsar=1:1,format=yuv420p[bumper_v];"
            f"[3:a]aformat=channel_layouts=stereo:sample_rates=44100[bumper_a];"
            f"[0:v]trim={bg_offset + hook_dur:.2f}:{bg_offset + audio_dur + 0.5:.2f},setpts=PTS-STARTPTS,fps=30,setsar=1:1,format=yuv420p[body_bg];"
            f"[body_bg]subtitles={ass_path}:fontsdir=/usr/share/fonts/truetype/liberation[body_v];"
            f"[2:a]atrim={hook_dur:.2f}:{audio_dur + 0.5:.2f},asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo:sample_rates=44100[body_a];"
            f"[hook_v][hook_a][bumper_v][bumper_a][body_v][body_a]concat=n=3:v=1:a=1[vout][aout]"
        )
        cmd_inputs = [
            "-stream_loop", "-1",
            "-i", BACKGROUND_VIDEO,
            "-i", card_path,
            "-i", audio_path,
            "-i", INTRO_BUMPER,
        ]
        map_args = ["-map", "[vout]", "-map", "[aout]"]
    else:
        card_fade_start = max(0.5, title_end_time - 0.5)
        vf = (
            f"[0:v]trim={bg_offset:.2f}:{bg_offset + audio_dur + 0.5:.2f},setpts=PTS-STARTPTS,setsar=1:1[bg];"
            f"[1:v]format=rgba,fade=t=out:st={card_fade_start:.2f}:d=0.4:alpha=1[card];"
            f"[bg][card]overlay=(W-w)/2:(H-h)/2 - 120:enable='between(t,0,{title_end_time:.2f})'[v_card];"
            f"[v_card]subtitles={ass_path}:fontsdir=/usr/share/fonts/truetype/liberation[vout]"
        )
        cmd_inputs = [
            "-stream_loop", "-1",
            "-i", BACKGROUND_VIDEO,
            "-i", card_path,
            "-i", audio_path,
        ]
        map_args = ["-map", "[vout]", "-map", "2:a"]
        
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        *cmd_inputs,
        "-filter_complex", vf,
        *map_args,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-threads", "0",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        final_output
    ]
    
    subprocess.run(ffmpeg_cmd, check=True)
    print(f"\n✅ Video generated successfully: {final_output}")
    return final_output

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Automated Reddit Story Video Generator")
    parser.add_argument("--story", default="wave_doubling_down", choices=list(SAMPLE_STORIES.keys()), help="Story key to render")
    parser.add_argument("--engine", default=None, choices=["elevenlabs", "edge"], help="TTS engine (default: elevenlabs if key set, else edge)")
    parser.add_argument("--voice", default=None, help="Voice name or ID")
    parser.add_argument("--rate", default=None, help="Speech rate adjustment")
    parser.add_argument("--caption-style", default="white_shadow", choices=["yellow", "green", "box", "white_shadow", "showcase"], help="Caption style (default: white_shadow)")
    parser.add_argument("--no-intro", action="store_true", help="Disable channel branding bumper")
    parser.add_argument("--force-tts", action="store_true", help="Force re-synthesis with TTS even if cached")
    parser.add_argument("--model", default="eleven_flash_v2_5", help="ElevenLabs model ID (default: eleven_flash_v2_5 for 50 percent credit discount)")
    parser.add_argument("--output", default="reddit_story_production.mp4", help="Output MP4 filename in PhoneShare")
    args = parser.parse_args()
    build_automated_video(
        story_key=args.story,
        output_filename=args.output,
        voice=args.voice,
        rate=args.rate,
        engine=args.engine,
        caption_style=args.caption_style,
        include_intro=not args.no_intro,
        force_tts=args.force_tts,
        model=args.model
    )
