#!/usr/bin/env python3
"""
16:9 Long-Form YouTube Compilation Engine for @TiktokPlaysGames
- Renders 30-to-60-minute horizontal 1920x1080 compilations from curated Reddit stories.
- Generates 16:9 horizontal ASS subtitles, centered Reddit title cards, and story transition bumpers.
- Produces exact YouTube chapter timestamps and SEO-optimized upload metadata.
- Enables qualifying for high-RPM YouTube long-form mid-roll ads ($6-$14 RPM).
"""

import os
import sys
import json
import re
import time
import shutil
import subprocess
from pathlib import Path

# Add toolkit dir to path
TOOLKIT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(TOOLKIT_DIR))

from reddit_card_generator import generate_reddit_card
from automated_video_engine import load_env, normalize_spoken_text, synthesize_with_elevenlabs, vtt_to_ass, EDGE_TTS_BIN

load_env()

DEFAULT_OUTPUT_DIR = Path("/home/jeremy/PhoneShare/youtube_compilations")
DEFAULT_STORIES_FILE = TOOLKIT_DIR / "batch_stories_20.json"
DEFAULT_VERTICAL_BG = "/home/jeremy/PhoneShare/minecraft_gameplay.mp4"
BRANDING_BUMPER = TOOLKIT_DIR.parent / "assets" / "branding" / "intro_bumper_ready.mp4"

# 16:9 Subtitle Style Definition (Clean White + Deep 6px Outline & Shadow, Lower-Third Centered)
ASS_HEADER_16X9 = """[Script Info]
Title: TikTok Plays 16:9 Long-Form Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Style16x9WhiteShadow,Liberation Sans,52,&H00FFFFFF,&H00000000,&H00000000,&HFF000000,-1,0,0,0,100,100,0,0,1,6,5,2,80,80,140,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def sec_to_timestamp(seconds: float) -> str:
    """Formats seconds into YouTube chapter timestamp format (MM:SS or HH:MM:SS)."""
    s = int(round(seconds))
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{sec:02d}"
    return f"{m:02d}:{sec:02d}"

def get_video_duration(path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path
    ]
    return float(subprocess.check_output(cmd).decode().strip())

def create_transition_stinger(output_path: str, story_index: int, total_stories: int, title: str):
    """Generates a sleek 2-second 16:9 transition card between stories."""
    temp_img = Path("/tmp/transition_card.png")
    from PIL import Image, ImageDraw, ImageFont
    
    img = Image.new("RGBA", (1920, 1080), (12, 14, 18, 255))
    draw = ImageDraw.Draw(img)
    
    font_bold = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    font_regular = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    
    f_badge = ImageFont.truetype(font_bold, 32)
    f_next = ImageFont.truetype(font_bold, 58)
    f_sub = ImageFont.truetype(font_regular, 36)
    
    # Badge
    badge_text = f"TIKTOK PLAYS • STORY {story_index} OF {total_stories}"
    draw.text((960, 420), badge_text, font=f_badge, fill=(255, 100, 50, 255), anchor="mm")
    
    # Next Story Text
    clean_title = (title[:65] + "...") if len(title) > 65 else title
    draw.text((960, 500), f"UP NEXT:", font=f_next, fill=(255, 255, 255, 255), anchor="mm")
    draw.text((960, 580), f'"{clean_title}"', font=f_sub, fill=(200, 210, 225, 255), anchor="mm")
    
    img.save(temp_img)
    
    # Generate 2.0 second 1920x1080 MP4 with silent audio
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(temp_img),
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-t", "2.0",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def render_story_segment_16x9(
    story: dict,
    output_mp4: str,
    bg_video_path: str,
    bg_offset: float = 0.0,
    force_tts: bool = False,
    engine: str = "edge"
) -> float:
    """
    Renders a single story into a 16:9 horizontal MP4 segment (1920x1080).
    Returns the exact duration of the generated segment.
    """
    temp_dir = Path("/tmp/longform_engine")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    card_path = str(temp_dir / f"card_{story['id']}.png")
    audio_path = str(temp_dir / f"audio_{story['id']}.mp3")
    ass_path = str(temp_dir / f"captions_{story['id']}.ass")
    
    # 1. Generate Reddit Title Card
    generate_reddit_card(
        subreddit=story["subreddit"],
        author=story["author"],
        time_str=story["time_str"],
        title=story["title"],
        upvotes=story["upvotes"],
        comments=story["comments"],
        output_path=card_path
    )
    
    # 2. Text Normalization
    spoken_title = normalize_spoken_text(story["title"])
    spoken_body = normalize_spoken_text(story["body"])
    full_text = f"{spoken_title}. {spoken_body}"
    title_word_count = len(spoken_title.split())
    
    # 3. Audio & Captions Synthesis
    if engine == "elevenlabs" and os.environ.get("ELEVENLABS_API_KEY"):
        voice_id = story.get("voice_id", "pNInz6obpgDQGcFmaJgB")
        title_end_time = synthesize_with_elevenlabs(
            full_text=full_text,
            title_word_count=title_word_count,
            voice_id=voice_id,
            audio_path=audio_path,
            ass_path=ass_path,
            caption_style="white_shadow",
            time_offset=0.0,
            force_tts=force_tts,
            model_id="eleven_flash_v2_5"
        )
    else:
        vtt_path = str(temp_dir / f"audio_{story['id']}.vtt")
        txt_path = temp_dir / "story.txt"
        txt_path.write_text(full_text, encoding="utf-8")
        chosen_voice = story.get("voice", "en-US-BrianNeural")
        subprocess.run([
            EDGE_TTS_BIN,
            "--file", str(txt_path),
            "--write-media", audio_path,
            "--write-subtitles", vtt_path,
            "--voice", chosen_voice,
            "--rate", "+5%"
        ], check=True)
        with open(vtt_path, "r", encoding="utf-8") as f:
            vtt_content = f.read()
        m = re.search(r"-->\s*([0-9:,.]+)", vtt_content)
        title_end_time = 5.0
        vtt_to_ass(vtt_path, ass_path, title_end_time, caption_style="white_shadow", time_offset=0.0)

    # Convert the ASS file to 16:9 PlayRes & styling
    ass_content = Path(ass_path).read_text(encoding="utf-8")
    if "[Events]" in ass_content:
        events_part = ass_content.split("[Events]")[1]
        events_part = events_part.replace("StyleWhiteShadow", "Style16x9WhiteShadow")
        new_ass = ASS_HEADER_16X9 + events_part
        Path(ass_path).write_text(new_ass, encoding="utf-8")
        
    audio_dur = get_video_duration(audio_path)
    total_dur = audio_dur + 0.5
    
    # 4. Check Background Video Aspect Ratio
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "default=noprint_wrappers=1",
        bg_video_path
    ]
    probe_out = subprocess.check_output(probe_cmd).decode()
    width = int(re.search(r'width=(\d+)', probe_out).group(1))
    height = int(re.search(r'height=(\d+)', probe_out).group(1))
    is_horizontal = (width >= height)
    
    # Video Filters for 16:9 Output
    card_fade_start = max(0.5, title_end_time - 0.5)
    
    if is_horizontal:
        # Native 16:9 gameplay: scale/crop directly to 1920x1080
        vf = (
            f"[0:v]trim=0:{total_dur:.2f},setpts=PTS-STARTPTS,fps=30,"
            f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1:1,format=yuv420p[bg];"
            f"[1:v]format=rgba,fade=t=out:st={card_fade_start:.2f}:d=0.4:alpha=1[card];"
            f"[bg][card]overlay=(W-w)/2:(H-h)/2:enable='between(t,0,{title_end_time:.2f})'[v_card];"
            f"[v_card]subtitles={ass_path}:fontsdir=/usr/share/fonts/truetype/liberation[vout]"
        )
    else:
        # Vertical gameplay (fallback): Blurred 16:9 backdrop + sharp centered 1080x1920 gameplay
        vf = (
            f"[0:v]trim=0:{total_dur:.2f},setpts=PTS-STARTPTS,fps=30[raw_bg];"
            f"[raw_bg]split=2[fg_in][blur_in];"
            f"[blur_in]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
            f"boxblur=25:25,eq=brightness=-0.12[bg_blur];"
            f"[fg_in]scale=-1:1080[fg_sharp];"
            f"[bg_blur][fg_sharp]overlay=(W-w)/2:0[stage];"
            f"[1:v]format=rgba,scale=920:-1,fade=t=out:st={card_fade_start:.2f}:d=0.4:alpha=1[card];"
            f"[stage][card]overlay=(W-w)/2:(H-h)/2:enable='between(t,0,{title_end_time:.2f})'[v_card];"
            f"[v_card]subtitles={ass_path}:fontsdir=/usr/share/fonts/truetype/liberation[vout]"
        )
        
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-ss", f"{bg_offset:.2f}",
        "-stream_loop", "-1",
        "-i", bg_video_path,
        "-i", card_path,
        "-i", audio_path,
        "-filter_complex", vf,
        "-map", "[vout]", "-map", "2:a",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-c:a", "aac", "-b:a", "192k",
        "-threads", "0", "-pix_fmt", "yuv420p",
        output_mp4
    ]
    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return get_video_duration(output_mp4)

def build_longform_compilation(
    stories_file: str = str(DEFAULT_STORIES_FILE),
    output_dir: str = str(DEFAULT_OUTPUT_DIR),
    bg_video: str = None,
    story_count: int = 10,
    volume_num: int = 1,
    force_render: bool = False,
    engine: str = "edge"
):
    """
    Compiles 8–15 stories into a single 35–50 minute 16:9 YouTube MP4 with chapters and metadata.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = Path("/tmp/longform_engine")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    with open(stories_file, "r", encoding="utf-8") as f:
        all_stories = json.load(f)
        
    selected_stories = all_stories[:story_count]
    total_selected = len(selected_stories)
    
    # Select background video
    if not bg_video:
        # Check for horizontal gameplay in PhoneShare
        candidate_16x9 = Path("/home/jeremy/PhoneShare/gameplay_16x9.mp4")
        if candidate_16x9.exists():
            bg_video = str(candidate_16x9)
        else:
            bg_video = DEFAULT_VERTICAL_BG
            
    print("\n=======================================================")
    print(f"🎬 BUILDING 16:9 YOUTUBE COMPILATION (VOLUME {volume_num})")
    print(f"📚 Stories Count: {total_selected}")
    print(f"🎙️ TTS Engine: {engine.upper()} (Zero API costs when using EDGE)")
    print(f"🎮 Background Source: {bg_video}")
    print(f"📁 Output Directory: {out_dir}")
    print("=======================================================\n")
    
    segment_files = []
    chapters = []
    cumulative_time = 0.0
    
    for i, story in enumerate(selected_stories):
        story_num = i + 1
        seg_mp4 = str(temp_dir / f"vol{volume_num}_seg_{story_num:02d}.mp4")
        stinger_mp4 = str(temp_dir / f"vol{volume_num}_stinger_{story_num:02d}.mp4")
        
        # 1. Add Chapter Timestamp
        timestamp_str = sec_to_timestamp(cumulative_time)
        clean_title = story["title"].split("?")[0].split(".")[0].strip()
        chapters.append(f"{timestamp_str} - Story {story_num}: {clean_title} ({story['subreddit']})")
        print(f"⏱️ [{timestamp_str}] Story {story_num}/{total_selected}: {clean_title[:55]}...")
        
        # 2. Render Story Segment (16:9)
        bg_offset = (i * 180.0) % 3200.0
        if not os.path.exists(seg_mp4) or force_render:
            t0 = time.time()
            dur = render_story_segment_16x9(story, seg_mp4, bg_video, bg_offset=bg_offset, engine=engine)
            print(f"   ↳ Rendered segment ({dur:.1f}s) in {time.time() - t0:.1f}s")
        else:
            dur = get_video_duration(seg_mp4)
            print(f"   ↳ Using cached segment ({dur:.1f}s)")
            
        segment_files.append(seg_mp4)
        cumulative_time += dur
        
        # 3. Add transition stinger if not last story
        if story_num < total_selected:
            next_story = selected_stories[story_num]
            create_transition_stinger(stinger_mp4, story_num + 1, total_selected, next_story["title"])
            stinger_dur = get_video_duration(stinger_mp4)
            segment_files.append(stinger_mp4)
            cumulative_time += stinger_dur
            
    total_minutes = round(cumulative_time / 60.0, 1)
    print(f"\n✅ All {total_selected} segments ready. Total run time: ~{total_minutes} mins ({cumulative_time:.1f}s)")
    
    # 4. Concatenate Segments Losslessly
    print("\nStep 4/5: Concatenating all story segments into final 16:9 compilation...")
    concat_list_file = temp_dir / f"concat_vol{volume_num}.txt"
    with open(concat_list_file, "w") as f:
        for seg in segment_files:
            f.write(f"file '{seg}'\n")
            
    final_output_mp4 = str(out_dir / f"reddit_stories_compilation_vol{volume_num}.mp4")
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        final_output_mp4
    ]
    subprocess.run(concat_cmd, check=True)
    print(f"🎉 Final 16:9 Compilation Exported: {final_output_mp4}")
    
    # 5. Generate YouTube Metadata & Chapters
    print("\nStep 5/5: Generating YouTube chapters & upload metadata...")
    yt_title = f"Best of Revenge & Entitled People Stories ({int(total_minutes)} Min Compilation) - No Parts | Vol. {volume_num}"
    
    desc_lines = [
        f"{yt_title}\n",
        "A full uninterrupted collection of the top viral stories from r/AmItheAsshole, r/maliciouscompliance, r/tifu, and r/pettyrevenge. Perfect for work, driving, gaming, or sleep listening.\n",
        "🎧 TIMESTAMPS / CHAPTERS:",
        *chapters,
        "\n=======================================================",
        "🎮 SUBSCRIBE to @TiktokPlaysGames for daily Reddit narrations & gaming highlights!",
        "🔗 Channel Bio & Gear: Check the link in our channel banner header.",
        "🎧 Featured Listener Gear: Monster AC530 Open-Ear Wireless Earbuds (Linked in bio)",
        "=======================================================\n",
        "#reddit #redditstories #aita #maliciouscompliance #compilation #askreddit #storytime"
    ]
    yt_description = "\n".join(desc_lines)
    
    meta_txt_file = out_dir / f"youtube_metadata_vol{volume_num}.txt"
    meta_txt_file.write_text(f"TITLE:\n{yt_title}\n\nDESCRIPTION:\n{yt_description}", encoding="utf-8")
    
    summary_json_file = out_dir / f"compilation_vol{volume_num}_summary.json"
    summary_data = {
        "volume": volume_num,
        "video_path": final_output_mp4,
        "total_duration_sec": cumulative_time,
        "total_minutes": total_minutes,
        "story_count": total_selected,
        "title": yt_title,
        "chapters": chapters,
        "metadata_file": str(meta_txt_file)
    }
    summary_json_file.write_text(json.dumps(summary_data, indent=2), encoding="utf-8")
    
    print(f"📋 YouTube Chapters & Metadata saved to: {meta_txt_file}")
    print(f"📊 Summary saved to: {summary_json_file}")
    print("\n🚀 16:9 COMPILATION ENGINE RUN COMPLETE!\n")
    return summary_data

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="16:9 Long-Form YouTube Compilation Runner")
    parser.add_argument("--count", type=int, default=10, help="Number of stories to include (default: 10)")
    parser.add_argument("--vol", type=int, default=1, help="Volume number (default: 1)")
    parser.add_argument("--bg", default=None, help="Path to 16:9 horizontal gameplay background")
    parser.add_argument("--engine", default="edge", choices=["edge", "elevenlabs"], help="TTS engine (default: edge for 100% free)")
    parser.add_argument("--force", action="store_true", help="Force re-rendering of story segments")
    args = parser.parse_args()
    
    build_longform_compilation(
        story_count=args.count,
        volume_num=args.vol,
        bg_video=args.bg,
        engine=args.engine,
        force_render=args.force
    )
