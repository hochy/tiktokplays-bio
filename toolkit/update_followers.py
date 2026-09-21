#!/usr/bin/env python3
import sys
import re
import subprocess

if len(sys.argv) < 2:
    print("Usage: python3 toolkit/update_followers.py <count_str>")
    print("Example: python3 toolkit/update_followers.py 64.2K")
    sys.exit(1)

new_count = sys.argv[1].strip()
if not new_count.upper().endswith("COMMUNITY"):
    new_label = f"{new_count} Community"
else:
    new_label = new_count

files = ['index.html', 'bio_link/index.html']
pattern = re.compile(r'([0-9]+(?:\.[0-9]+)?K\+?\s+Community)')

updated = False
for fpath in files:
    with open(fpath, 'r') as f:
        content = f.read()
    
    new_content, count = pattern.subn(new_label, content)
    if count > 0:
        with open(fpath, 'w') as f:
            f.write(new_content)
        print(f"Updated {fpath} -> {new_label}")
        updated = True

if updated:
    subprocess.run(["git", "add"] + files, check=True)
    subprocess.run(["git", "commit", "-m", f"feat: Update follower badge to {new_label}"], check=True)
    subprocess.run(["git", "push", "origin", "master"], check=True)
    print("Pushed to GitHub Pages successfully!")
else:
    print("No matching follower badge pattern found.")
