#!/usr/bin/env python3
"""
16:9 High-CTR YouTube Compilation Thumbnail Generator for @TiktokPlaysGames
- Generates 1920x1080 (16:9) high-contrast YouTube thumbnails.
- Features prominent dark-mode Reddit post card, custom high-upvote badges, and duration pill.
- Complies with YouTube thumbnail standards (max CTR for compilation videos).
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    curr = []
    for w in words:
        test = " ".join(curr + [w])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            curr.append(w)
        else:
            if curr:
                lines.append(" ".join(curr))
            curr = [w]
    if curr:
        lines.append(" ".join(curr))
    return lines

def generate_compilation_thumbnail(
    subreddit: str = "r/AmItheAsshole",
    title_hook: str = "AITA for making my girlfriend's brother pay for his own $400 steak after he ordered it behind my back?",
    upvotes: str = "54.8k",
    comments: str = "4.2k",
    duration_badge: str = "45 MIN COMPILATION",
    vol_str: str = "VOL. 1 • NO PARTS",
    bg_image_path: str = None,
    output_path: str = "/home/jeremy/PhoneShare/youtube_compilations/thumbnail_vol1.png"
):
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. Base Canvas (1920x1080)
    if bg_image_path and os.path.exists(bg_image_path):
        bg = Image.open(bg_image_path).convert("RGBA").resize((1920, 1080))
        bg = bg.filter(ImageFilter.GaussianBlur(radius=12))
        enhancer = ImageEnhance.Brightness(bg)
        bg = enhancer.enhance(0.55)
    else:
        # Sleek dark radial gradient backdrop
        bg = Image.new("RGBA", (1920, 1080), (14, 16, 22, 255))
        draw_bg = ImageDraw.Draw(bg)
        # Subtle glow circles in background
        draw_bg.ellipse((-100, -100, 800, 800), fill=(30, 45, 75, 120))
        draw_bg.ellipse((1200, 400, 2100, 1300), fill=(55, 30, 30, 100))
        
    draw = ImageDraw.Draw(bg)
    
    font_badge = ImageFont.truetype(FONT_BOLD, 42)
    font_vol = ImageFont.truetype(FONT_BOLD, 36)
    font_sub = ImageFont.truetype(FONT_BOLD, 38)
    font_meta = ImageFont.truetype(FONT_REGULAR, 30)
    font_title = ImageFont.truetype(FONT_BOLD, 52)
    font_footer = ImageFont.truetype(FONT_BOLD, 34)
    
    # 2. Draw Top Pill Badges
    # Duration Badge (Hormozi / YouTube High-CTR Neon Yellow)
    badge_x, badge_y = 100, 90
    draw.rounded_rectangle([badge_x, badge_y, badge_x + 520, badge_y + 80], radius=16, fill=(255, 230, 0, 255))
    draw.text((badge_x + 260, badge_y + 40), duration_badge, font=font_badge, fill=(10, 10, 10, 255), anchor="mm")
    
    # Volume Tag (Clean Translucent Grey)
    vol_x = badge_x + 550
    draw.rounded_rectangle([vol_x, badge_y, vol_x + 440, badge_y + 80], radius=16, fill=(35, 42, 54, 230), outline=(70, 80, 100, 255), width=2)
    draw.text((vol_x + 220, badge_y + 40), vol_str, font=font_vol, fill=(255, 255, 255, 255), anchor="mm")
    
    # 3. Main Center Reddit Post Card
    card_x = 100
    card_y = 230
    card_w = 1720
    
    # Calculate wrapped title lines
    title_lines = wrap_text(title_hook, font_title, card_w - 120, draw)
    line_h = 66
    title_block_h = len(title_lines) * line_h
    card_h = 110 + title_block_h + 100 # header + title + footer + margins
    
    # Card Shadow
    draw.rounded_rectangle([card_x + 12, card_y + 12, card_x + card_w + 12, card_y + card_h + 12], radius=24, fill=(0, 0, 0, 160))
    # Card Background (Authentic Reddit Dark Mode: #1A1A1B)
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=24, fill=(26, 26, 27, 250), outline=(52, 53, 54, 255), width=3)
    
    # Subreddit Icon Circle
    icon_x = card_x + 60
    icon_y = card_y + 55
    sub_color = (255, 69, 0, 255) if "asshole" in subreddit.lower() else (0, 121, 211, 255)
    draw.ellipse([icon_x - 30, icon_y - 30, icon_x + 30, icon_y + 30], fill=sub_color)
    draw.text((icon_x, icon_y), "r/", font=ImageFont.truetype(FONT_BOLD, 30), fill=(255, 255, 255, 255), anchor="mm")
    
    # Subreddit & Meta Header
    draw.text((icon_x + 50, icon_y - 12), subreddit, font=font_sub, fill=(215, 218, 220, 255), anchor="lm")
    draw.text((icon_x + 50, icon_y + 24), f"Posted by u/TopStory • 12 hr. ago", font=font_meta, fill=(129, 131, 132, 255), anchor="lm")
    
    # Title Text
    curr_y = card_y + 125
    for line in title_lines:
        draw.text((card_x + 60, curr_y), line, font=font_title, fill=(245, 245, 245, 255), anchor="la")
        curr_y += line_h
        
    # Footer Stats (Upvotes & Comments)
    footer_y = card_y + card_h - 45
    # Upvotes Pill
    draw.rounded_rectangle([card_x + 60, footer_y - 32, card_x + 280, footer_y + 32], radius=32, fill=(38, 38, 39, 255))
    draw.text((card_x + 105, footer_y), "⬆", font=font_footer, fill=(255, 69, 0, 255), anchor="mm")
    draw.text((card_x + 175, footer_y), upvotes, font=font_footer, fill=(255, 255, 255, 255), anchor="mm")
    draw.text((card_x + 245, footer_y), "⬇", font=font_footer, fill=(129, 131, 132, 255), anchor="mm")
    
    # Comments Pill
    draw.rounded_rectangle([card_x + 310, footer_y - 32, card_x + 540, footer_y + 32], radius=32, fill=(38, 38, 39, 255))
    draw.text((card_x + 355, footer_y), "💬", font=ImageFont.truetype(FONT_REGULAR, 26), fill=(215, 218, 220, 255), anchor="mm")
    draw.text((card_x + 445, footer_y), f"{comments} Comments", font=ImageFont.truetype(FONT_BOLD, 28), fill=(215, 218, 220, 255), anchor="mm")
    
    # Save Image
    bg.convert("RGB").save(out_p, "PNG", quality=95)
    print(f"🖼️ High-CTR YouTube Thumbnail Generated: {out_p}")
    return str(out_p)

if __name__ == "__main__":
    generate_compilation_thumbnail()
