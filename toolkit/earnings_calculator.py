#!/usr/bin/env python3
"""
TikTok Monetization Earnings Calculator (62k Follower Benchmark)
Calculates projected monthly revenue across Creator Rewards, TikTok Shop Affiliate,
Brand Sponsorships, and Digital Product Funnels.
"""

import argparse
import sys

def calculate_earnings(
    monthly_views: int = 500_000,
    rpm: float = 0.85,
    eligible_view_ratio: float = 0.50,
    shop_video_views: int = 80_000,
    shop_conversion_rate: float = 0.0025,
    avg_product_price: float = 26.0,
    avg_commission_rate: float = 0.18,
    sponsored_posts: int = 2,
    rate_per_post: float = 550.0,
    bio_link_clicks: int = 1_500,
    lead_magnet_optin_rate: float = 0.20,
    digital_product_price: float = 27.0,
    digital_conversion_rate: float = 0.035,
):
    # 1. Creator Rewards
    eligible_views = monthly_views * eligible_view_ratio
    creator_rewards_income = (eligible_views / 1_000) * rpm

    # 2. TikTok Shop Affiliate
    shop_orders = shop_video_views * shop_conversion_rate
    shop_gross_sales = shop_orders * avg_product_price
    shop_commission_income = shop_gross_sales * avg_commission_rate

    # 3. Brand Sponsorships
    sponsorship_income = sponsored_posts * rate_per_post

    # 4. Digital Product / Owned Funnel
    optins = bio_link_clicks * lead_magnet_optin_rate
    digital_buyers = optins * digital_conversion_rate
    digital_income = digital_buyers * digital_product_price

    total_low = (
        (creator_rewards_income * 0.6) +
        (shop_commission_income * 0.5) +
        (sponsorship_income * 0.5) +
        (digital_income * 0.5)
    )
    total_expected = (
        creator_rewards_income +
        shop_commission_income +
        sponsorship_income +
        digital_income
    )
    total_high = (
        (creator_rewards_income * 1.5) +
        (shop_commission_income * 1.8) +
        (sponsorship_income * 1.6) +
        (digital_income * 1.8)
    )

    return {
        "monthly_views": monthly_views,
        "creator_rewards": creator_rewards_income,
        "tiktok_shop": shop_commission_income,
        "sponsorships": sponsorship_income,
        "digital_products": digital_income,
        "total_low": total_low,
        "total_expected": total_expected,
        "total_high": total_high,
    }

def print_report(results):
    print("=" * 64)
    print("      TIKTOK MONETIZATION EARNINGS PROJECTION (62k FOLLOWERS)")
    print("=" * 64)
    print(f"Total Monthly Views Model:         {results['monthly_views']:,}")
    print("-" * 64)
    print(f"1. Creator Rewards (1min+ videos): ${results['creator_rewards']:>8.2f} / month")
    print(f"2. TikTok Shop Affiliate:          ${results['tiktok_shop']:>8.2f} / month")
    print(f"3. Brand Sponsorships (2 posts):   ${results['sponsorships']:>8.2f} / month")
    print(f"4. Digital Products / Bio Funnel:  ${results['digital_products']:>8.2f} / month")
    print("-" * 64)
    print(f"CONSERVATIVE SCENARIO:             ${results['total_low']:>8.2f} / month")
    print(f"EXPECTED TARGET SCENARIO:          ${results['total_expected']:>8.2f} / month")
    print(f"OPTIMIZED / AGGRESSIVE SCENARIO:   ${results['total_high']:>8.2f} / month")
    print("=" * 64)
    print("Key Action Items:")
    print(" • Ensure >60% of content exceeds 60 seconds for Creator Rewards.")
    print(" • Test 2-3 TikTok Shop physical products with 15-20% commission.")
    print(" • Create a 1-page media kit to pitch brands for $500-$750/post.")
    print(" • Set up a free lead magnet to capture emails in your bio.")
    print("=" * 64)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate TikTok monetization earnings.")
    parser.add_argument("--views", type=int, default=500_000, help="Monthly video views")
    parser.add_argument("--rpm", type=float, default=0.85, help="Expected RPM ($ per 1,000 views)")
    parser.add_argument("--posts", type=int, default=2, help="Sponsored posts per month")
    parser.add_argument("--rate", type=float, default=550.0, help="Price per sponsored post ($)")
    args = parser.parse_args()

    res = calculate_earnings(
        monthly_views=args.views,
        rpm=args.rpm,
        sponsored_posts=args.posts,
        rate_per_post=args.rate
    )
    print_report(res)
