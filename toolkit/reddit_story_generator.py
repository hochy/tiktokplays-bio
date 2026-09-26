#!/usr/bin/env python3
"""
Reddit Story + TikTok Shop Affiliate Script Generator for @tiktokplaygames
Generates 60-90 second retention-optimized narrative scripts for Reddit confession /
storytelling over gameplay footage with natural organic product integration.
"""

import argparse

STORIES = {
    "roommate_secret": {
        "title": "My Roommate Thought I Was Asleep (Monster Earbuds Integration)",
        "hook": "My roommate thought I was completely passed out, but what I overheard him whisper at 2 AM literally froze my blood.",
        "pacing_words": 165,
        "body": (
            "I usually sleep with these open-ear Monster wireless earbuds in because they don't dig into your ear "
            "even if you sleep directly on your side. Plus they have that titanium zero-gravity hook so they never fall out. "
            "I linked the exact pair in the orange cart down below if you need sleep or gaming earbuds—grab them while the flash sale is active.\n\n"
            "Anyway, I had paused my ambient storm sound and was just laying there with the volume off. "
            "Suddenly the bedroom door slowly creaked open. My roommate stepped in barefoot, clutching his phone to his ear. "
            "He whispered, 'He's out cold. We can move the stuff out of the garage tonight before he notices.'\n\n"
            "My stomach completely dropped. I had over three thousand dollars worth of gaming equipment and audio gear stored in boxes out there.\n\n"
            "I stayed completely still, pretending to breathe heavy. The second he stepped back into the hallway, I grabbed my phone, locked the bedroom door from the inside, and called the non-emergency police line.\n\n"
            "Part two is already posted on my profile with what the police found in his trunk."
        ),
        "cta": "Tap the orange shopping cart down below if you want those zero-gravity Monster earbuds before the discount ends, and follow for part two."
    },
    "late_night_gaming": {
        "title": "The Voice in the Headset (AC530 Open-Ear Mic Headset)",
        "hook": "If you play tactical shooters late at night with headphones on, stop scrolling because what happened to me last night was not in the game.",
        "pacing_words": 170,
        "body": (
            "I was testing out this new Monster AC530 dual-fold open-ear headset. The mic noise cancellation is insane and it's open-ear so you can hear your actual room while still getting full surround audio. "
            "I put the link in the orange cart below because TikTok has them heavily discounted right now.\n\n"
            "It was 3:15 AM and I was the last one alive in a 1v3 clutch. My whole squad was dead in Discord listening to my stream. "
            "All of a sudden, through the open-ear mic, my teammate screams: 'Bro, who is standing behind your chair?'\n\n"
            "I thought he was just trolling to make me lose focus. But then my other friend said, 'Dude I'm not kidding, someone just walked past your bedroom doorway.'\n\n"
            "I live completely alone on the third floor of an apartment complex.\n\n"
            "I pulled off the headset, turned around slowly, and the deadbolt on my front door was turned completely vertical."
        ),
        "cta": "Check the orange cart for the headset with 100-hour battery, and check my pinned video for the apartment security footage."
    },
    "mini_mic_secret": {
        "title": "The 2 AM Discord Wellness Check (Mini Mic Pro / Lavalier Integration)",
        "hook": "I was testing out this new mini wireless clip-on mic during a late-night gaming stream, and my entire Discord squad literally called the police on me because of what happened.",
        "pacing_words": 205,
        "body": (
            "I use this mini wireless lapel mic because you just plug the tiny receiver into your phone or PC and it instantly pairs with active noise cancellation. "
            "I linked the exact set in the orange cart down below if you need one for streaming or gaming.\n\n"
            "Anyway, it was 2 AM, I was in the middle of a late-night session with my headset blasted on 100%. I stepped out to the kitchen to grab a drink, completely forgetting I still had the clip-on mic on my shirt. "
            "While I was gone, my roommate’s 80-pound golden retriever barged into my room, jumped onto my desk, and knocked over an entire metal shelf holding heavy textbooks and empty glass bottles. "
            "In Discord, my friends heard a massive, violent crash, shattering glass, and then total silence because the mic's noise suppression filtered out the dog. Since I was in the kitchen with headphones on, I didn't hear a thing. "
            "My squad panicked, assumed someone had kicked in my front door, and called the police for a wellness check.\n\n"
            "Ten minutes later, I'm sitting at my desk in pajama pants playing Minecraft when two police officers are knocking on my front door shining flashlights through the window. "
            "The officers walked in, saw the dog covered in fallen books, and started cracking up while my entire Discord was dying of laughter."
        ),
        "cta": "Tap the orange shopping cart down below to check out this mini clip-on mic—just make sure your Discord friends know how good the noise cancellation is before you step away from your desk."
    }
}

try:
    from toolkit.script_compliance import audit_script
except ImportError:
    from script_compliance import audit_script

def generate_reddit_script(story_key=None):
    if not story_key or story_key not in STORIES:
        story_key = "roommate_secret"
    
    data = STORIES[story_key]
    climax_text = " ".join([line.strip() for line in data['body'].splitlines()[1:-1] if line.strip()])
    script_body = f"""TITLE: {data['title']}

[00:00 - 00:04] HOOK (Fast Pacing, Visual Gameplay cut on beat):
"{data['hook']}"

[00:04 - 00:22] ORGANIC PRODUCT PLACEMENT & VISUAL DEMONSTRATION:
[VISUAL CUE: Cut from gameplay to 5-7s of dynamic hands-on B-roll / demonstration of product]
"{data['body'].splitlines()[0]}"

[00:22 - 00:55] STORY CLIMAX (High retention suspense build):
[VISUAL CUE: Cut back to fast-paced gameplay footage]
"{climax_text}"

[00:55 - 01:10] CLIFFHANGER & QUALIFYING 60S PAYOFF:
"{data['body'].splitlines()[-1]}"

[01:10 - 01:15] DUAL CALL TO ACTION:
"{data['cta']}"
"""

    audit = audit_script(script_body, is_tiktok_shop=True)

    script = f"""================================================================
TIKTOK PLAY GAMES - NARRATIVE INTEGRATION SCRIPT (~70 SECONDS)
================================================================
Format: Reddit Confession / Suspense Narration over Gameplay (Minecraft/GTA)
Video Duration Target: 65 - 75 Seconds (Creator Rewards RPM Qualified: > 60s)
Monetization: TikTok Shop Affiliate (Orange Cart) + Creator Rewards RPM
================================================================

{script_body}
================================================================
COMPLIANCE & HEALTH AUDIT (CHR / PPS SHIELD):
- Policy Compliant: {'PASSED (SAFE)' if audit['is_compliant'] else 'FAILED (RISK DETECTED)'}
- Word Count: ~{audit['word_count']} words (~{audit['estimated_duration_sec']}s)
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
    parser = argparse.ArgumentParser(description="Generate Reddit Story Script with TikTok Shop Integration")
    parser.add_argument("--story", choices=list(STORIES.keys()), default="roommate_secret", help="Story key")
    args = parser.parse_args()
    print(generate_reddit_script(args.story))
