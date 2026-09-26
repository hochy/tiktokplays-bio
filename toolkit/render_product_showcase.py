#!/usr/bin/env python3
"""
Monster AC530 Dedicated Product Showcase Video Generator
Builds a high-converting, 100% TikTok Shop compliant vertical video (1080x1920)
using official Monster assets, dynamic Ken Burns motion, Option 4 captions, and CTA pointer.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

WORKSPACE = Path("/home/jeremy/Documents/antigravity/keen-rutherford")
ASSETS_DIR = WORKSPACE / "assets/monster_ac530"
OUTPUT_PATH = Path("/home/jeremy/PhoneShare/monster_ac530_product_showcase.mp4")
FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

AUDIO_PATH = ASSETS_DIR / "voiceover_compliant.mp3"
ASS_PATH = ASSETS_DIR / "captions_compliant.ass"

# 100% Compliant Scenes with exact audio sync (75.56s total)
SCENES = [
    {
        "num": 1,
        "duration": 8.046,
        "img": "product_walmart_full.jpg",
        "badge": "WARNING: STOP SCROLLING",
        "badge_color": (254, 44, 85),
        "title": "BULKY HEADSETS VS OPEN-EAR",
        "sub": "Tired of Ear Canal Pressure & Sweat?"
    },
    {
        "num": 2,
        "duration": 8.824,
        "img": "product_banggood.jpg",
        "badge": "PAIN POINT COMPARISON",
        "badge_color": (255, 140, 0),
        "title": "THE EAR FATIGUE PROBLEM",
        "sub": "Crushed Temples • Trapped Moisture • Blocked Ears"
    },
    {
        "num": 3,
        "duration": 5.712,
        "img": "product_1.jpg",
        "badge": "TIKTOK VIRAL UPGRADE",
        "badge_color": (254, 44, 85),
        "title": "MONSTER AC530 OPEN-EAR",
        "sub": "Official Monster Air Conduction Audio"
    },
    {
        "num": 4,
        "duration": 8.069,
        "img": "product_2.png",
        "badge": "ALL-DAY ERGONOMIC COMFORT",
        "badge_color": (0, 200, 150),
        "title": "0-GRAVITY TITANIUM EARHOOK",
        "sub": "Rests Outside Ear • Zero Canal Pressure"
    },
    {
        "num": 5,
        "duration": 8.184,
        "img": "product_gallery_2.jpg",
        "badge": "PRO ACOUSTIC SOUND",
        "badge_color": (0, 180, 255),
        "title": "14.2MM DYNAMIC DRIVERS",
        "sub": "Directional Sound • Rich Bass • Zero Fatigue"
    },
    {
        "num": 6,
        "duration": 9.067,
        "img": "product_article_3.jpg",
        "badge": "GAMING & DISCORD READY",
        "badge_color": (140, 80, 255),
        "title": "BLUETOOTH 6.0 LOW LATENCY",
        "sub": "Instant Audio Sync • No Lag Footsteps"
    },
    {
        "num": 7,
        "duration": 6.769,
        "img": "product_walmart_full.jpg",
        "badge": "PATENTED FOLDING CASE",
        "badge_color": (255, 170, 0),
        "title": "DUAL-FOLD POCKET DESIGN",
        "sub": "Ultra Compact • Type-C Fast Charging"
    },
    {
        "num": 8,
        "duration": 6.350,
        "img": "product_3.jpg",
        "badge": "IPX5 SWEATPROOF BUILD",
        "badge_color": (0, 220, 200),
        "title": "IPX5 WATER RESISTANT",
        "sub": "Sweatproof • Gym & Marathon Tested"
    },
    {
        "num": 9,
        "duration": 8.255,
        "img": "product_article_1.png",
        "badge": "OFFICIAL TIKTOK SHOP",
        "badge_color": (0, 200, 150),
        "title": "OFFICIAL MONSTER STORE",
        "sub": "Verified Seller • Fast Free Shipping"
    },
    {
        "num": 10,
        "duration": 6.281,
        "img": "product_1.jpg",
        "badge": "TAP ORANGE CART",
        "badge_color": (255, 107, 0),
        "title": "TAP ORANGE CART BELOW",
        "sub": "Check Available Deals & Current Stock",
        "cta": True
    },
]

def render_scene_base(scene):
    """Renders the static layers (background, shadows, pill, badges)."""
    w, h = 1080, 1920
    img_path = ASSETS_DIR / scene["img"]
    prod = Image.open(img_path).convert("RGBA")

    # 1. Ambient Background (heavy blur + darkened)
    bg = prod.resize((w, h), Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(55))
    dark_overlay = Image.new("RGBA", (w, h), (12, 14, 20, 210))
    bg.alpha_composite(dark_overlay)

    card_w, card_h = 980, 720
    card_x = (w - card_w) // 2
    card_y = 230

    # Shadow for Card
    shadow = Image.new("RGBA", (card_w + 40, card_h + 40), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([(20, 20), (card_w + 20, card_h + 20)], radius=32, fill=(0, 0, 0, 190))
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))
    bg.alpha_composite(shadow, (card_x - 20, card_y - 12))

    # Fonts
    font_header = ImageFont.truetype(FONT_PATH, 30)
    font_title = ImageFont.truetype(FONT_PATH, 42)
    font_sub = ImageFont.truetype(FONT_PATH, 26)
    font_cta = ImageFont.truetype(FONT_PATH, 34)

    draw = ImageDraw.Draw(bg)

    # 2. Top Badge
    badge_text = scene["badge"]
    bbox = font_header.getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 60
    bh = 56
    bx = (w - bw) // 2
    by = 130
    draw.rounded_rectangle([(bx, by), (bx + bw, by + bh)], radius=28, fill=scene["badge_color"] + (240,))
    draw.text((w // 2, by + bh // 2), badge_text, font=font_header, fill=(255, 255, 255), anchor="mm")

    # 3. Spec Pill
    pill_y = card_y + card_h + 28
    pill_h = 100
    pill_w = 980
    pill_x = (w - pill_w) // 2
    draw.rounded_rectangle([(pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h)], radius=24, fill=(20, 24, 34, 230), outline=(255, 255, 255, 120), width=2)
    draw.text((w // 2, pill_y + 32), scene["title"], font=font_title, fill=(255, 255, 255), anchor="mm")
    draw.text((w // 2, pill_y + 72), scene["sub"], font=font_sub, fill=(0, 229, 255), anchor="mm")

    # 4. Orange Cart CTA Callout (Final Scene)
    if scene.get("cta"):
        cta_y = 1520
        cta_w = 700
        cta_h = 76
        cta_x = 40
        draw.rounded_rectangle([(cta_x, cta_y), (cta_x + cta_w, cta_y + cta_h)], radius=20, fill=(255, 107, 0, 245), outline=(255, 255, 255, 230), width=3)
        draw.text((cta_x + cta_w // 2, cta_y + cta_h // 2), "TAP ORANGE CART BELOW", font=font_cta, fill=(255, 255, 255), anchor="mm")
        
        arrow_tip_x = 180
        arrow_tip_y = 1630
        arrow_points = [
            (arrow_tip_x, arrow_tip_y),
            (arrow_tip_x - 30, arrow_tip_y - 35),
            (arrow_tip_x - 12, arrow_tip_y - 35),
            (arrow_tip_x - 12, arrow_tip_y - 65),
            (arrow_tip_x + 12, arrow_tip_y - 65),
            (arrow_tip_x + 12, arrow_tip_y - 35),
            (arrow_tip_x + 30, arrow_tip_y - 35),
        ]
        draw.polygon(arrow_points, fill=(255, 215, 0, 255), outline=(0, 0, 0, 200))

    return bg, prod, (card_x, card_y, card_w, card_h)

def generate_video_stream(ffmpeg_stdin):
    """Generates continuous 30fps frames with Ken Burns zoom motion and pipes raw RGB24 to FFmpeg."""
    fps = 30
    mask = Image.new("L", (980, 720), 0)
    ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (980, 720)], radius=32, fill=255)

    total_frames = 0
    for scene in SCENES:
        base_bg, prod, (cx, cy, cw, ch) = render_scene_base(scene)
        num_frames = int(round(scene["duration"] * fps))
        total_frames += num_frames
        
        orig_w, orig_h = prod.size
        # Pre-crop aspect fit
        aspect_card = cw / ch
        aspect_prod = orig_w / orig_h
        if aspect_prod > aspect_card:
            fit_h = orig_h
            fit_w = int(orig_h * aspect_card)
        else:
            fit_w = orig_w
            fit_h = int(orig_w / aspect_card)
        
        crop_x = (orig_w - fit_w) // 2
        crop_y = (orig_h - fit_h) // 2
        prod_cropped = prod.crop((crop_x, crop_y, crop_x + fit_w, crop_y + fit_h))

        for frame_idx in range(num_frames):
            # Ken Burns zoom: 1.00 -> 1.05
            progress = frame_idx / max(1, num_frames - 1)
            zoom = 1.0 + 0.05 * progress
            
            # Zoom crop
            zw = int(fit_w / zoom)
            zh = int(fit_h / zoom)
            zx = (fit_w - zw) // 2
            zy = (fit_h - zh) // 2
            
            frame_prod = prod_cropped.crop((zx, zy, zx + zw, zy + zh))
            frame_prod = frame_prod.resize((cw, ch), Image.Resampling.BILINEAR)

            card = Image.new("RGBA", (cw, ch), (18, 22, 30, 255))
            card.paste(frame_prod, (0, 0))

            frame_img = base_bg.copy()
            frame_img.paste(card, (cx, cy), mask)

            # Draw card outline
            draw = ImageDraw.Draw(frame_img)
            draw.rounded_rectangle([(cx, cy), (cx + cw, cy + ch)], radius=32, outline=scene["badge_color"] + (200,), width=4)

            # Convert to RGB24 bytes and write directly to pipe
            raw_bytes = frame_img.convert("RGB").tobytes()
            ffmpeg_stdin.write(raw_bytes)

    print(f"Piped {total_frames} animated frames ({total_frames/fps:.2f}s) to FFmpeg.")

def main():
    print("Step 1: Starting FFmpeg encoding process with rawvideo stdin...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", "1080x1920",
        "-r", "30",
        "-i", "-",
        "-i", str(AUDIO_PATH),
        "-filter_complex", f"[0:v]ass={ASS_PATH}:fontsdir=/usr/share/fonts/truetype/liberation[vout]",
        "-map", "[vout]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(OUTPUT_PATH)
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    
    print("Step 2: Generating and streaming dynamic Ken Burns frames...")
    try:
        generate_video_stream(proc.stdin)
        proc.stdin.close()
    except Exception as e:
        proc.kill()
        raise e

    _, stderr = proc.communicate()
    if proc.returncode != 0:
        print("FFmpeg error:", stderr.decode()[-800:])
        sys.exit(1)

    print(f"\n✅ Video successfully exported to: {OUTPUT_PATH}")

    # Inspect specs
    ffprobe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size,bit_rate:stream=width,height,r_frame_rate,nb_read_frames,codec_name",
        "-count_frames",
        "-of", "json",
        str(OUTPUT_PATH)
    ]
    probe_output = subprocess.check_output(ffprobe_cmd).decode()
    print("Video Specs:")
    print(probe_output)

if __name__ == "__main__":
    main()
