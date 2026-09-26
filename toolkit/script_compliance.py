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

def audit_script(script_text: str, is_tiktok_shop: bool = True) -> Dict[str, Any]:
    """
    Performs a strict compliance audit on a video script.
    Returns audit status, violations, warnings, and scoring metrics.
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

    # 6. Word Count & Duration Pacing
    # If the script contains quoted dialogue, measure spoken words; otherwise measure all text
    quoted_parts = re.findall(r'"([^"]+)"', script_text)
    spoken_text = " ".join(quoted_parts) if quoted_parts else script_text
    words = len(re.findall(r'\b\w+\b', spoken_text))
    estimated_duration_sec = round(words / 2.4, 1)

    if estimated_duration_sec < 60.0:
        warnings.append(
            f"PACING WARNING: Script is ~{words} words (~{estimated_duration_sec}s). "
            "Videos under 60 seconds do not qualify for Creator Rewards Program RPM pool."
        )
    else:
        passed_checks.append(f"Duration target met: ~{words} words (~{estimated_duration_sec}s > 60s qualified).")

    is_compliant = len(violations) == 0

    return {
        "is_compliant": is_compliant,
        "violations": violations,
        "warnings": warnings,
        "passed_checks": passed_checks,
        "word_count": words,
        "estimated_duration_sec": estimated_duration_sec
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
