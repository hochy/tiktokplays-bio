#!/usr/bin/env python3
"""
Batch Renderer for 20 YouTube Shorts for @TiktokPlaysGames
- Uses ElevenLabs Flash v2.5 (0.5x credit rate)
- Generates pixel-perfect Reddit cards
- Adds Channel Branding Stinger (1.5s)
- Option 4 Captions (White text, 6px black outline, 5px shadow)
- Staggers background gameplay offset across videos
- Outputs ready-to-upload MP4s, cover thumbnails, and upload schedule metadata
"""

import os
import sys
import json
import time
from pathlib import Path

# Add parent directory to sys.path so we can import from toolkit
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from automated_video_engine import build_automated_video, load_env

load_env()

BATCH_STORIES_FILE = SCRIPT_DIR / "batch_stories_20.json"
OUTPUT_DIR = Path("/home/jeremy/PhoneShare/youtube_shorts_batch")
COVERS_DIR = OUTPUT_DIR / "covers"

def run_batch(start_idx=0, end_idx=20, force=False):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(BATCH_STORIES_FILE, "r", encoding="utf-8") as f:
        stories = json.load(f)
        
    total_stories = len(stories)
    print(f"\n=======================================================")
    print(f"🚀 STARTING YOUTUBE SHORTS BATCH PRODUCTION ({total_stories} VIDEOS)")
    print(f"📁 Output Directory: {OUTPUT_DIR}")
    print(f"🎙️ Model: eleven_flash_v2_5 (50% credit rate)")
    print(f"🎨 Subtitle Style: Option 4 (Clean White + Deep Shadow)")
    print(f"=======================================================\n")
    
    schedule_data = []
    
    for i, story in enumerate(stories[start_idx:end_idx], start=start_idx):
        short_id = story["id"]
        output_file = OUTPUT_DIR / f"{short_id}.mp4"
        cover_file = COVERS_DIR / f"{short_id}_cover.png"
        
        # Calculate dynamic background offset so each video starts at different parkour section
        bg_offset = round((i * 14.5) % 65.0, 2)
        
        print(f"\n[{i+1}/{total_stories}] Processing {short_id}: {story['title'][:55]}...")
        
        if output_file.exists() and not force:
            print(f"⏩ Video already exists: {output_file} (Skipping render, use --force to overwrite)")
        else:
            try:
                t0 = time.time()
                build_automated_video(
                    story_data=story,
                    output_filename=str(output_file),
                    voice=story.get("voice_id", "pNInz6obpgDQGcFmaJgB"),
                    engine="elevenlabs",
                    caption_style="white_shadow",
                    include_intro=True,
                    force_tts=force,
                    model="eleven_flash_v2_5",
                    bg_offset=bg_offset
                )
                render_time = time.time() - t0
                print(f"⚡ Rendered {short_id}.mp4 in {render_time:.1f}s")
            except Exception as e:
                print(f"❌ Error rendering {short_id}: {e}")
                import traceback
                traceback.print_exc()
                continue
                
        # Prepare upload metadata
        clean_title = f"{story['title'][:85]} #shorts"
        description = (
            f"{story['title']}\n\n"
            f"Story from {story['subreddit']} by {story['author']}.\n\n"
            f"🎮 Follow @TiktokPlaysGames for daily Reddit stories and gaming highlights!\n"
            f"🔗 Check our channel header for our full gaming and audio setup.\n\n"
            f"{' '.join(story['tags'])}"
        )
        pinned_comment = (
            f"What would you have done in this situation? Let us know below! 👇\n"
            f"Check @TiktokPlaysGames bio header for our gaming headset setup!"
        )
        
        schedule_data.append({
            "index": i + 1,
            "id": short_id,
            "file_path": str(output_file),
            "cover_path": str(cover_file),
            "subreddit": story["subreddit"],
            "scheduled_slot": story["scheduled_slot"],
            "title": clean_title,
            "description": description,
            "pinned_comment": pinned_comment,
            "tags": story["tags"]
        })
        
    # Save metadata schedule JSON
    meta_json = OUTPUT_DIR / "shorts_schedule_metadata.json"
    meta_json.write_text(json.dumps(schedule_data, indent=2), encoding="utf-8")
    print(f"\n📋 Saved scheduling metadata: {meta_json}")
    
    # Save markdown schedule
    md_content = ["# 📅 YouTube Shorts 7-Day Posting Schedule (@TiktokPlaysGames)\n\n"]
    md_content.append("| Day & Time | Short ID | Title | Subreddit | Status |\n")
    md_content.append("|---|---|---|---|---|\n")
    for item in schedule_data:
        md_content.append(f"| **{item['scheduled_slot']}** | `{item['id']}` | {item['title'][:50]}... | `{item['subreddit']}` | Ready |\n")
    
    md_content.append("\n## Upload Instructions\n")
    md_content.append("1. Upload each MP4 file to [YouTube Studio](https://studio.youtube.com).\n")
    md_content.append("2. Set Title and Description from `shorts_schedule_metadata.json`.\n")
    md_content.append("3. Under Visibility, select **Schedule** and set the indicated Day & Time.\n")
    md_content.append("4. Add the pinned comment pointing to `@TiktokPlaysGames` bio link.\n")
    
    md_file = OUTPUT_DIR / "SCHEDULE.md"
    md_file.write_text("".join(md_content), encoding="utf-8")
    print(f"📋 Saved human-readable schedule: {md_file}")
    print(f"\n🎉 ALL BATCH TASKS FINISHED!\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Batch Render 20 YouTube Shorts")
    parser.add_argument("--start", type=int, default=0, help="Start story index (0-19)")
    parser.add_argument("--end", type=int, default=20, help="End story index (1-20)")
    parser.add_argument("--force", action="store_true", help="Force re-rendering of existing videos")
    args = parser.parse_args()
    
    run_batch(start_idx=args.start, end_idx=args.end, force=args.force)
