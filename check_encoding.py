#!/usr/bin/env python
import os
import glob
import sys

def check_file_encoding(filepath):
    """Check if a file can be decoded as UTF-8"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read()
        return True, None
    except UnicodeDecodeError as e:
        return False, str(e)

# Find all HTML files
html_files = glob.glob('backend/**/*.html', recursive=True)
print(f"Checking {len(html_files)} HTML files for encoding issues...\n")

problem_files = []
for filepath in html_files:
    ok, error = check_file_encoding(filepath)
    if not ok:
        problem_files.append((filepath, error))
        print(f"❌ ERROR: {filepath}")
        print(f"   {error}\n")

if problem_files:
    print(f"\nFound {len(problem_files)} files with encoding issues")
    sys.exit(1)
else:
    print(f"✓ All {len(html_files)} files are UTF-8 encoded")
    sys.exit(0)
