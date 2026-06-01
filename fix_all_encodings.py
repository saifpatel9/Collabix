#!/usr/bin/env python
"""Scan all HTML files and convert to UTF-8"""
import os
import glob

def fix_file_encoding(filepath):
    """Try to read and convert a file to UTF-8"""
    encodings_to_try = ['latin-1', 'cp1252', 'iso-8859-1', 'utf-8-sig', 'utf-8']
    
    try:
        # First try to read as UTF-8
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read()
        return True, "Already UTF-8"
    except UnicodeDecodeError:
        pass
    
    # Try other encodings
    for encoding in encodings_to_try:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Write as UTF-8
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, f"Converted from {encoding}"
        except (UnicodeDecodeError, LookupError):
            continue
    
    # Last resort
    try:
        with open(filepath, 'rb') as f:
            content = f.read().decode('utf-8', errors='replace')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, "Converted with error replacement"
    except Exception as e:
        return False, str(e)

# Find all HTML files
html_files = glob.glob(r'backend\**\*.html', recursive=True)
print(f"Found {len(html_files)} HTML files\n")

fixed = 0
errors = 0

for filepath in sorted(html_files):
    success, message = fix_file_encoding(filepath)
    if success:
        print(f"✓ {filepath}")
        print(f"  {message}")
        fixed += 1
    else:
        print(f"✗ {filepath}")
        print(f"  ERROR: {message}")
        errors += 1

print(f"\n{'='*60}")
print(f"Fixed: {fixed}, Errors: {errors}")
