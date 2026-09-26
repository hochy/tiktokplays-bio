#!/usr/bin/env python3
"""
Generates an authentic Reddit dark-mode post card image for short-form video overlays.
"""

import os
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def generate_reddit_card(
    subreddit="r/tifu",
    author="u/RedditStoryteller",
    time_str="8 hr. ago",
    title="TIFU by waving back at someone who was waving at the person behind me, and doubling down for three years",
    upvotes="24.8k",
    comments="1.4k",
    output_path="/tmp/reddit_card.png"
):
    card_width = 980
    padding_x = 44
    padding_y = 36
    
    font_sub = ImageFont.truetype(FONT_BOLD, 30)
    font_meta = ImageFont.truetype(FONT_REGULAR, 24)
    font_title = ImageFont.truetype(FONT_BOLD, 38)
    font_footer = ImageFont.truetype(FONT_BOLD, 24)
    
    # Calculate title height
    dummy_img = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)
    title_lines = wrap_text(title, font_title, card_width - (padding_x * 2), dummy_draw)
    
    line_height = 48
    title_total_h = len(title_lines) * line_height
    
    header_h = 56
    footer_h = 52
    spacing = 24
    
    card_height = padding_y + header_h + spacing + title_total_h + spacing + footer_h + padding_y
    
    # Create image with transparent background
    img = Image.new("RGBA", (card_width, card_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw rounded card background (#1A1A1B) with border (#343536)
    radius = 24
    bg_color = (26, 26, 27, 245)
    border_color = (60, 62, 65, 255)
    draw.rounded_rectangle(
        [(0, 0), (card_width - 1, card_height - 1)],
        radius=radius,
        fill=bg_color,
        outline=border_color,
        width=2
    )
    
    # Draw Subreddit Icon (Circle with orange background & Snoo/r/)
    icon_radius = 24
    icon_center = (padding_x + icon_radius, padding_y + icon_radius)
    draw.ellipse(
        [
            (icon_center[0] - icon_radius, icon_center[1] - icon_radius),
            (icon_center[0] + icon_radius, icon_center[1] + icon_radius)
        ],
        fill=(255, 69, 0, 255) # Reddit orange #FF4500
    )
    # Simple 'r/' in icon
    icon_font = ImageFont.truetype(FONT_BOLD, 22)
    draw.text((icon_center[0] - 10, icon_center[1] - 13), "r/", font=icon_font, fill=(255, 255, 255, 255))
    
    # Subreddit Name & Metadata
    sub_x = icon_center[0] + icon_radius + 18
    sub_y = padding_y + 4
    draw.text((sub_x, sub_y), subreddit, font=font_sub, fill=(255, 255, 255, 255))
    
    sub_bbox = draw.textbbox((sub_x, sub_y), subreddit, font=font_sub)
    meta_x = sub_bbox[2] + 12
    meta_text = f"• Posted by {author} • {time_str}"
    draw.text((meta_x, sub_y + 5), meta_text, font=font_meta, fill=(129, 131, 132, 255))
    
    # Draw Title Lines
    curr_y = padding_y + header_h + spacing
    for line in title_lines:
        draw.text((padding_x, curr_y), line, font=font_title, fill=(215, 218, 220, 255))
        curr_y += line_height
        
    # Draw Footer
    foot_y = curr_y + spacing
    
    # 1. Upvote pill
    upvote_w = 170
    draw.rounded_rectangle(
        [(padding_x, foot_y), (padding_x + upvote_w, foot_y + footer_h)],
        radius=20,
        fill=(39, 41, 43, 255)
    )
    # Up arrow polygon
    arrow_pts = [
        (padding_x + 28, foot_y + 16),
        (padding_x + 20, foot_y + 32),
        (padding_x + 36, foot_y + 32)
    ]
    draw.polygon(arrow_pts, fill=(215, 218, 220, 255))
    draw.text((padding_x + 48, foot_y + 12), upvotes, font=font_footer, fill=(215, 218, 220, 255))
    
    # Down arrow
    down_pts = [
        (padding_x + upvote_w - 28, foot_y + 34),
        (padding_x + upvote_w - 36, foot_y + 18),
        (padding_x + upvote_w - 20, foot_y + 18)
    ]
    draw.polygon(down_pts, fill=(129, 131, 132, 255))
    
    # 2. Comment pill
    comm_x = padding_x + upvote_w + 16
    comm_w = 200
    draw.rounded_rectangle(
        [(comm_x, foot_y), (comm_x + comm_w, foot_y + footer_h)],
        radius=20,
        fill=(39, 41, 43, 255)
    )
    # Comment icon bubble
    draw.rounded_rectangle(
        [(comm_x + 20, foot_y + 16), (comm_x + 42, foot_y + 32)],
        radius=4,
        fill=(129, 131, 132, 255)
    )
    draw.polygon([(comm_x + 22, foot_y + 30), (comm_x + 20, foot_y + 38), (comm_x + 28, foot_y + 30)], fill=(129, 131, 132, 255))
    draw.text((comm_x + 52, foot_y + 12), f"{comments} Comments", font=font_footer, fill=(215, 218, 220, 255))
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Reddit card saved to {output_path} ({card_width}x{card_height})")
    return output_path

if __name__ == "__main__":
    generate_reddit_card()
