#!/usr/bin/env python3
import json
from collections import defaultdict
from datetime import datetime

with open('tiktok_data/user_data_tiktok.json', 'r') as f:
    data = json.load(f)

# 1. Profile Info
prof_map = data.get('Profile And Settings', {}).get('Profile Info', {}).get('ProfileMap', {})
print("=" * 60)
print("             TIKTOK ACCOUNT AUDIT REPORT")
print("=" * 60)
print(f"Username:        @{prof_map.get('userName')}")
print(f"Display Name:    {prof_map.get('displayName')}")
print(f"Account Region:  {prof_map.get('accountRegion')}")
print(f"Followers:       {prof_map.get('followerCount'):,}")
print(f"Total Likes:     {int(prof_map.get('likesReceived', 0)):,}")
print(f"Bio:             {prof_map.get('bioDescription')}")
print(f"YouTube Link:    {prof_map.get('youtubeLink') or 'None set'}")
print(f"Instagram Link:  {prof_map.get('instagramLink') or 'None set'}")
print("-" * 60)

# 2. Video Analysis
video_list = data.get('Post', {}).get('Posts', {}).get('VideoList', [])
print(f"Total Videos in Export: {len(video_list):,}")

monthly_posts = defaultdict(int)
monthly_likes = defaultdict(int)
likes_distribution = []

for v in video_list:
    d_str = v.get('Date')
    likes = int(v.get('Likes', 0))
    likes_distribution.append((likes, d_str, v.get('Link')))
    if d_str:
        dt = datetime.strptime(d_str, '%Y-%m-%d %H:%M:%S')
        month_key = dt.strftime('%Y-%m')
        monthly_posts[month_key] += 1
        monthly_likes[month_key] += likes

print("\n--- POSTING VOLUME & LIKES BY MONTH ---")
for m in sorted(monthly_posts.keys()):
    posts = monthly_posts[m]
    likes = monthly_likes[m]
    avg_l = (likes / posts) if posts else 0
    print(f"{m}:  {posts:>4} posts  |  {likes:>7,} likes  |  avg: {avg_l:>5.1f} likes/post")

# Sort videos by likes
likes_distribution.sort(key=lambda x: x[0], reverse=True)
print("\n--- TOP 10 HIGHEST LIKED VIDEOS ---")
for i, (l, d, link) in enumerate(likes_distribution[:10], 1):
    print(f"{i:>2}. {l:>6,} likes | Date: {d} | Link: {link[:80]}...")

# 3. Follower Growth Velocity
fans_list = data.get('Profile And Settings', {}).get('Follower', {}).get('FansList', [])
print(f"\n--- FOLLOWER GROWTH VELOCITY (Total fans recorded: {len(fans_list):,}) ---")
monthly_fans = defaultdict(int)
for fan in fans_list:
    d_str = fan.get('Date')
    if d_str:
        dt = datetime.strptime(d_str, '%Y-%m-%d %H:%M:%S')
        month_key = dt.strftime('%Y-%m')
        monthly_fans[month_key] += 1

for m in sorted(monthly_fans.keys()):
    print(f"{m}: +{monthly_fans[m]:>5,} new followers")

# 4. Comments Analysis
comments_list = data.get('Comment', {}).get('Comments', {}).get('CommentsList', [])
print(f"\n--- CREATOR COMMENTS POSTED: {len(comments_list):,} ---")

print("=" * 60)
