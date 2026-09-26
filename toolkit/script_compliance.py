#!/usr/bin/env python3
"""
TikTok Shop Script Compliance & Account Health Validator
Audits scripts against TikTok Shop Affiliate policies to prevent:
1. Creator Health Rating (CHR) point deductions
2. Promotion Performance Score (PPS) drops
3. "Ineligible for For You Feed" (FYP) suppression
4. Mismatched or irrelevant promotion penalties
"""

import re
from typing import Dict, List, Any

# Prohibited / Risky words on TikTok Shop
PROHIBITED_WORDS = [
    "dupe", "knockoff", "knock-off", "replica", "fake",
    "guaranteed", "guarantee", "miracle", "cure", "100% effective",
    "cheapest ever", "cheapest in the world", "best in the world",
    "better than airpods", "better than apple", "better than sony",
]

# External redirection phrases that violate TikTok Shop policy when an orange cart is attached
EXTERNAL_REDIRECT_PHRASES = [
    "link in bio", "link in my bio", "check my bio", "check the bio",
    "bio link", "check my profile link", "visit my website",
    "link in comments", "link in description", "dm me for the link"
]

# Compliant TikTok Shop CTA phrases
COMPLIANT_CART_TERMS = [
    "orange cart", "orange shopping cart", "yellow cart", "shopping cart below",
    "cart down below", "cart below", "orange basket", "yellow basket"
]

def audit_script(script_text: str, is_tiktok_shop: bool = True, target_mode: str = "both") -> Dict[str, Any]:
    """
    Performs a strict compliance audit on a video script.
    target_mode:
      - "both": Audits for both TikTok Creator Rewards (>60s) and YouTube Shorts (<60s).
      - "tiktok_rewards": Enforces 65s–120s sweet spot for TikTok Creator Rewards RPM ($0.40–$1.50/1k views).
      - "youtube_shorts": Enforces 48s–58s (<60.0s hard ceiling) for YouTube Shorts algorithm retention.
    """
    text_lower = script_text.lower()
    violations: List[str] = []
    warnings: List[str] = []
    passed_checks: List[str] = []

    # 1. External Redirection Audit
    if is_tiktok_shop:
        found_redirects = [p for p in EXTERNAL_REDIRECT_PHRASES if p in text_lower]
        if found_redirects:
            violations.append(
                f"CRITICAL: Found external redirection phrasing {found_redirects}. "
                "TikTok Shop policy strictly bans directing traffic away from the orange cart (e.g. 'link in bio')."
            )
        else:
            passed_checks.append("No external redirect phrases found (100% in-app compliant).")

    # 2. Prohibited Words Audit
    found_prohibited = []
    for word in PROHIBITED_WORDS:
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, text_lower):
            found_prohibited.append(word)

    if found_prohibited:
        violations.append(
            f"CRITICAL: Found prohibited or high-risk claims {found_prohibited}. "
            "Remove counterfeit/dupe references or unsubstantiated guarantees to prevent automated CHR penalties."
        )
    else:
        passed_checks.append("Zero prohibited/dupe/miracle claims detected.")

    # 3. Orange Cart CTA Audit
    if is_tiktok_shop:
        has_cart_cta = any(term in text_lower for term in COMPLIANT_CART_TERMS)
        if not has_cart_cta:
            violations.append(
                "CRITICAL: Missing explicit Orange Cart CTA. "
                "The script must verbally direct viewers to the orange shopping cart (e.g., 'tap the orange cart below')."
            )
        else:
            passed_checks.append("Compliant Orange Cart CTA verified.")

    # 4. Exact Price Claim Warning
    if re.search(r'\$\d+(\.\d{2})?', script_text) or re.search(r'\b\d+\s+dollars\b', text_lower):
        warnings.append(
            "WARNING: Exact dollar price mentioned in script. "
            "If the seller updates their price, your video may be flagged for mismatched pricing. "
            "Use relative terms like 'heavily discounted', 'flash sale price', or 'check the cart'."
        )
    else:
        passed_checks.append("No hardcoded dollar prices detected (safe against seller price changes).")

    # 5. Visual Demonstration / B-Roll Cue Audit
    has_broll_cue = any(kw in text_lower for kw in ["[visual cue]", "b-roll", "cutaway", "hands-on", "product footage", "demo"])
    if not has_broll_cue:
        warnings.append(
            "WARNING: No explicit visual B-roll or hands-on demonstration cue indicated. "
            "Posting pure gameplay without at least 5-7 seconds of visual product footage will trigger "
            "the 'Irrelevant Promotional Content' filter and suppress FYP reach."
        )
    else:
        passed_checks.append("Explicit visual product demonstration / B-roll cue present.")

    # 6. Word Count & Duration Pacing (Dual-Target Engine)
    quoted_parts = re.findall(r'"([^"]+)"', script_text)
    spoken_text = " ".join(quoted_parts) if quoted_parts else script_text
    words = len(re.findall(r'\b\w+\b', spoken_text))
    estimated_duration_sec = round(words / 2.4, 1)

    tiktok_qualified = estimated_duration_sec > 60.0
    shorts_qualified = estimated_duration_sec < 60.0

    # Mode A: TikTok Creator Rewards Audit
    if target_mode in ("tiktok_rewards", "both"):
        if not tiktok_qualified:
            warnings.append(
                f"TIKTOK REWARDS INELIGIBLE: Script is ~{words} words (~{estimated_duration_sec}s). "
                "TikTok Creator Rewards strictly requires videos to be strictly > 60 seconds (target: 65s–120s) "
                "to qualify for RPM payouts ($0.40–$1.50/1k views). Videos <= 60s earn $0.00 from the Rewards pool."
            )
        elif 61.0 <= estimated_duration_sec <= 120.0:
            passed_checks.append(
                f"TikTok Creator Rewards Qualified: ~{words} words (~{estimated_duration_sec}s, "
                "within 65s–120s sweet spot for maximum retention and RPM monetization)."
            )
        else:
            passed_checks.append(
                f"TikTok Creator Rewards Qualified (Extended Cut): ~{words} words (~{estimated_duration_sec}s > 60s)."
            )

    # Mode B: YouTube Shorts Audit
    if target_mode in ("youtube_shorts", "both"):
        if not shorts_qualified:
            warnings.append(
                f"YOUTUBE SHORTS OVERSIZED: Script is ~{words} words (~{estimated_duration_sec}s). "
                "YouTube Shorts has a strict 60.0s hard ceiling. Videos >= 60s forfeit Shorts shelf looping."
            )
        elif 45.0 <= estimated_duration_sec < 60.0:
            passed_checks.append(
                f"YouTube Shorts Optimized: ~{words} words (~{estimated_duration_sec}s, within 48s–58s Shorts target)."
            )
        else:
            passed_checks.append(
                f"YouTube Shorts Valid: ~{words} words (~{estimated_duration_sec}s < 60s)."
            )

    is_compliant = len(violations) == 0

    return {
        "is_compliant": is_compliant,
        "violations": violations,
        "warnings": warnings,
        "passed_checks": passed_checks,
        "word_count": words,
        "estimated_duration_sec": estimated_duration_sec,
        "tiktok_rewards_qualified": tiktok_qualified,
        "youtube_shorts_qualified": shorts_qualified,
        "target_mode": target_mode
    }

if __name__ == "__main__":
    test_sample = """
    My roommate thought I was passed out, but what I overheard him whisper froze my blood.
    [Visual Cue: Cut to 5s dynamic B-roll of Monster earbuds case opening and LEDs lighting up]
    I usually sleep with these open-ear Monster earbuds because of the zero-gravity hook.
    I linked them in the orange cart down below.
    Suddenly he stepped in and whispered about moving the gear.
    Tap the orange shopping cart down below to grab them before the discount ends, and follow for part two.
    """
    result = audit_script(test_sample, is_tiktok_shop=True)
    print("Compliant:", result["is_compliant"])
    print("Violations:", result["violations"])
    print("Warnings:", result["warnings"])
    print("Passed:", result["passed_checks"])
