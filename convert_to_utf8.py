#!/usr/bin/env python
"""Convert template files to UTF-8 encoding"""
import os

files_to_fix = [
    'backend\\templates\\organization\\partials\\chart.html',
    'backend\\templates\\components\\audit_timeline.html'
]

for filepath in files_to_fix:
    print(f"\nProcessing: {filepath}")
    
    # Common encodings to try
    encodings_to_try = ['latin-1', 'cp1252', 'iso-8859-1', 'utf-8-sig']
    
    content = None
    used_encoding = None
    
    for encoding in encodings_to_try:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
            used_encoding = encoding
            print(f"  Read with encoding: {encoding}")
            break
        except (UnicodeDecodeError, LookupError) as e:
            continue
    
    if content is None:
        # Last resort: read as binary and try to recover
        with open(filepath, 'rb') as f:
            raw = f.read()
        try:
            content = raw.decode('utf-8', errors='replace')
            used_encoding = 'utf-8 (with errors replaced)'
            print(f"  Read as UTF-8 with error replacement")
        except:
            print(f"  ✗ Failed to read {filepath}")
            continue
    
    # Write as UTF-8
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Converted to UTF-8")
    except Exception as e:
        print(f"  ✗ Failed to write: {e}")

print("\n✓ All files converted to UTF-8")
