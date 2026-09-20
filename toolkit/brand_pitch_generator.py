#!/usr/bin/env python3
"""
TikTok Brand Pitch & Rate Card Generator (62k Follower Benchmark)
Generates high-converting brand outreach emails, follow-up sequences, and rate cards.
"""

import argparse

def generate_pitch(creator_handle, niche, followers, avg_views, engagement_rate, brand_name, product_name):
    cold_email = f"""Subject: Collaboration idea for {brand_name} x @{creator_handle} ({followers:,} TikTok community)

Hi {brand_name} Marketing Team,

I've been following {brand_name} and really admire how you approached {product_name or "your recent product launches"}.

I run @{creator_handle} on TikTok, where I share content focused on {niche} with an engaged community of {followers:,} followers. Over the past 30 days, our videos average {avg_views:,} views with a {engagement_rate}% engagement rate—primarily reaching US/tier-1 audiences who are actively interested in {niche}.

I'd love to partner with {brand_name} on an organic-style video concept that naturally integrates {product_name or brand_name} to demonstrate how it solves a key problem for our audience. 

In addition to feed placement, I also offer 30-to-60 day Spark Ad authorization codes so your team can boost the highest-performing creative directly through your TikTok Ads Manager.

Would you be open to me sending over 2 quick creative concepts and my current media kit?

Best regards,

@{creator_handle}
TikTok: tiktok.com/@{creator_handle}
Media Kit: [Link to your media kit]
"""

    follow_up = f"""Subject: Re: Collaboration idea for {brand_name} x @{creator_handle}

Hi {brand_name} Team,

Following up on my note from earlier this week. I know your team is busy, so I put together two quick organic concepts for {product_name or brand_name}:

1. The "Problem/Solution" Hook: Highlighting the #1 frustration our audience faces in {niche} and revealing how {product_name or brand_name} solves it in under 60 seconds.
2. The "Honest Review / Day in the Life": Seamlessly incorporating {product_name or brand_name} into a natural routine video to drive organic comments and click-throughs.

Let me know if either angle aligns with your current marketing push and I can share my availability and rate card.

Best,
@{creator_handle}
"""

    # Estimated pricing based on 62k followers & avg views
    base_cpm_rate = max(350, int((avg_views / 1000) * 35))
    package_1 = base_cpm_rate
    package_2 = int(base_cpm_rate * 1.5)
    package_3 = int(base_cpm_rate * 2.8)

    rate_card = f"""================================================================
           TIKTOK SPONSORSHIP RATE CARD & PACKAGES
================================================================
Creator: @{creator_handle} | Community: {followers:,} | Avg Views: {avg_views:,}
----------------------------------------------------------------
TIER 1: ESSENTIAL SPONSORSHIP - ${package_1}
 • 1 Dedicated 60-75s TikTok Video
 • Brand tag & custom discount code in caption
 • Active link in bio for 7 days
 • Organic analytics report provided at Day 7

TIER 2: AMPLIFIED GROWTH (RECOMMENDED) - ${package_2}
 • 1 Dedicated TikTok Video + 1 Organic Cross-Post to IG Reels / Shorts
 • 30-Day Spark Ad Authorization Code (use video for paid ads)
 • Active link in bio for 14 days
 • 1 round of revisions included

TIER 3: HIGH-IMPACT CAMPAIGN - ${package_3}
 • 3 Dedicated TikTok Videos posted across 4 weeks
 • 60-Day Spark Ad Authorization Code across all creatives
 • 30-Day Category Exclusivity (no direct competitors mentioned)
 • Link in bio pinned for full campaign duration (30 days)
================================================================
"""

    return cold_email, follow_up, rate_card

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate TikTok Brand Pitch and Rate Card")
    parser.add_argument("--handle", type=str, default="your_handle", help="TikTok username")
    parser.add_argument("--niche", type=str, default="tech & productivity", help="Channel niche")
    parser.add_argument("--followers", type=int, default=62_000, help="Follower count")
    parser.add_argument("--avg-views", type=int, default=25_000, help="Average views per video")
    parser.add_argument("--engagement", type=float, default=7.4, help="Engagement rate percentage")
    parser.add_argument("--brand", type=str, default="Acme Co", help="Target brand name")
    parser.add_argument("--product", type=str, default="their productivity app", help="Product name")
    args = parser.parse_args()

    email, follow_up, rates = generate_pitch(
        args.handle, args.niche, args.followers, args.avg_views, args.engagement, args.brand, args.product
    )

    print("--- 1. INITIAL COLD PITCH EMAIL ---")
    print(email)
    print("--- 2. DAY 4 FOLLOW-UP EMAIL ---")
    print(follow_up)
    print("--- 3. CUSTOM RATE CARD ---")
    print(rates)
