#!/usr/bin/env python3
"""Simple encoding fixer - converts all HTML files to UTF-8"""
import os
import glob

def fix_file(filepath):
    """Fix encoding of a single file"""
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                content = f.read()
            # Write as UTF-8
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except:
            continue
    return False

# Find all HTML files
files = glob.glob(r'backend\**\*.html', recursive=True)
print(f"Found {len(files)} HTML files\n")

fixed = 0
for f in files:
    if fix_file(f):
        fixed += 1
        print(f"✓ {f}")

print(f"\nDone! Fixed {fixed}/{len(files)} files")
