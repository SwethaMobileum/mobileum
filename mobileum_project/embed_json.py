"""
embed_json.py
Run this AFTER the 3 pipeline scripts.
It takes master_telecom.json and embeds it into mobileum_platform_template.html
to produce the final mobileum_platform.html
"""
import os, sys

JSON_FILE = 'master_telecom.json'
TEMPLATE_FILE = 'mobileum_platform_template.html'
OUTPUT_FILE = 'mobileum_platform.html'

# Check files exist
if not os.path.exists(JSON_FILE):
    print(f"ERROR: {JSON_FILE} not found. Run build_master_json.py first.")
    sys.exit(1)
if not os.path.exists(TEMPLATE_FILE):
    print(f"ERROR: {TEMPLATE_FILE} not found.")
    sys.exit(1)

print("Reading JSON data...")
with open(JSON_FILE, 'r', encoding='utf-8') as f:
    json_data = f.read()

print("Reading HTML template...")
with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
    template = f.read()

# Replace placeholder with actual data
PLACEHOLDER = '/*DATA_PLACEHOLDER*/'
if PLACEHOLDER not in template:
    print("ERROR: Placeholder not found in template.")
    sys.exit(1)

print("Embedding data into HTML...")
final_html = template.replace(PLACEHOLDER, json_data + ';')

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(final_html)

size_mb = len(final_html) / 1_000_000
print(f"\nDone! {OUTPUT_FILE} created ({size_mb:.1f} MB)")
print(f"   Double-click {OUTPUT_FILE} to open in your browser.")
