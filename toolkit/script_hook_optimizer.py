#!/usr/bin/env python3
"""
TikTok 60s+ Script & Hook Optimizer (Creator Rewards & Monetization Engine)
Generates high-retention video scripts that pass the 60-second threshold
while driving affiliate conversions, digital product downloads, or Creator Rewards RPM.
"""

import argparse

def generate_script(topic, goal, target_offer, pain_point):
    hooks = [
        f'Option 1 (The Contrarian Warning): "Stop trying to fix {topic} the normal way. If you have been doing this in 2026, you are wasting hours and leaving money on the table."',
        f'Option 2 (The Secret Discovery): "Most people think you need expensive tools for {topic}, but this exact method took me from zero to solving {pain_point} in under 2 minutes."',
        f'Option 3 (The Step-by-Step Teardown): "I tested 7 different ways to handle {topic}, and literally only one delivered actual results without {pain_point}."'
    ]

    if goal == "tiktok_shop":
        cta = f'CTA (TikTok Shop): "I linked the exact {target_offer} I use in the orange cart right down below. Grab it while the flash sale is still live."'
    elif goal == "digital_product":
        cta = f'CTA (Digital Product / Lead Magnet): "I put the entire step-by-step framework and checklist inside the free guide at the link in my bio. Go download your copy before I close it."'
    elif goal == "creator_rewards":
        cta = f'CTA (Creator Rewards / High Engagement): "Drop your biggest question about {topic} in the comments, and save this video so you can reference the full breakdown when you set this up."'
    else:
        cta = f'CTA: "Check the link in my bio for the complete walkthrough, and follow for daily breakdowns on {topic}."'

    if goal == "tiktok_shop":
        visual_cta = "[Visual Cue]: Point finger toward lower-left corner toward the orange shopping cart."
    elif goal == "digital_product":
        visual_cta = "[Visual Cue]: Flash profile arrow pointing to bio link."
    else:
        visual_cta = "[Visual Cue]: Text prompt on screen asking question to drive comments."

    script = f"""================================================================
           TIKTOK HIGH-RETENTION SCRIPT (65-75 SECONDS)
================================================================
TOPIC: {topic}
MONETIZATION FOCUS: {goal.upper()}
TARGET OFFER / ASSET: {target_offer}
TARGET DURATION: ~68 seconds (~160 spoken words at 140 wpm)
----------------------------------------------------------------

[00:00 - 00:03] THE HOOK (Select one):
{hooks[0]}

[Visual Cue]: Fast zoom-in, bold 3-word title on screen, pattern-interrupt sound effect.

[00:03 - 00:15] THE CONTEXT & STAKES:
"Here is the problem: almost everyone struggling with {pain_point} makes the exact same mistake. They focus on the surface symptoms instead of addressing the core bottleneck. But when you flip the approach, everything changes."

[Visual Cue]: B-roll / screen recording illustrating the frustration or mistake.

[00:15 - 00:45] CORE VALUE DELIVERY (3 High-Impact Steps):
"Step number one: eliminate the friction. Instead of manually handling every detail, automate or batch the process right here.

Step number two: focus on leverage. Notice how doing this one small adjustment cuts down 80% of the friction with {topic}.

And step number three: never skip the verification. Test this on a small scale first to ensure your baseline remains solid."

[Visual Cue]: Cut camera angle or text card every 3 seconds to keep eyes locked on screen.

[00:45 - 00:60] PROOF & PAYOFF (Crossing the 60s Monetization Threshold):
"Look at the difference this made for me over the past 30 days. Consistent results, zero guesswork, and none of the headaches caused by {pain_point}. If you implement this today, you will immediately see why this structure outperforms everything else."

[Visual Cue]: Proof screenshot, analytics graph, before/after demonstration.

[00:60 - 00:72] THE MONETIZATION ENGINE (Call to Action):
"{cta}"

{visual_cta}
================================================================
"""
    try:
        from toolkit.script_compliance import audit_script
    except ImportError:
        from script_compliance import audit_script

    audit = audit_script(script, is_tiktok_shop=(goal == "tiktok_shop"))
    script += """================================================================
COMPLIANCE & HEALTH AUDIT (CHR / PPS SHIELD):
- Policy Compliant: """ + ('PASSED (SAFE)' if audit['is_compliant'] else 'FAILED (RISK DETECTED)') + f"""
- Spoken Word Count: ~{audit['word_count']} words (~{audit['estimated_duration_sec']}s)
- Creator Rewards Threshold (>60s): {'PASSED' if audit['estimated_duration_sec'] >= 60.0 else 'FAILED'}
- Passed Checks:
  * """ + "\n  * ".join(audit['passed_checks'])

    if audit['warnings']:
        script += "\n- Warnings:\n  ! " + "\n  ! ".join(audit['warnings'])
    if audit['violations']:
        script += "\n- VIOLATIONS:\n  X " + "\n  X ".join(audit['violations'])

    script += "\n================================================================\n"
    return script

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate 60s+ TikTok Script & Hooks")
    parser.add_argument("--topic", type=str, default="budgeting and saving money", help="Video topic")
    parser.add_argument("--goal", choices=["tiktok_shop", "digital_product", "creator_rewards", "general"], default="creator_rewards", help="Monetization objective")
    parser.add_argument("--offer", type=str, default="Free Financial Blueprint", help="Target product or freebie")
    parser.add_argument("--pain-point", type=str, default="living paycheck to paycheck", help="Audience pain point")
    args = parser.parse_args()

    output = generate_script(args.topic, args.goal, args.offer, args.pain_point)
    print(output)
