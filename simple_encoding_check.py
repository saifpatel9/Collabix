#!/usr/bin/env python3
"""Direct encoding detection without external dependencies"""
import os
import glob

def detect_encoding_from_bom(filepath):
    """Detect encoding from BOM (Byte Order Mark)"""
    with open(filepath, 'rb') as f:
        first_bytes = f.read(4)
    
    if first_bytes.startswith(b'\xef\xbb\xbf'):
        return 'UTF-8-BOM'
    elif first_bytes.startswith(b'\xff\xfe'):
        return 'UTF-16-LE'
    elif first_bytes.startswith(b'\xfe\xff'):
        return 'UTF-16-BE'
    elif first_bytes.startswith(b'\xff\xfe\x00\x00'):
        return 'UTF-32-LE'
    elif first_bytes.startswith(b'\x00\x00\xfe\xff'):
        return 'UTF-32-BE'
    return None

def can_decode_utf8(filepath):
    """Try to decode file as UTF-8"""
    try:
        with open(filepath, 'rb') as f:
            f.read().decode('utf-8')
        return True, None
    except UnicodeDecodeError as e:
        return False, str(e)

def analyze_encoding(filepath):
    """Analyze file encoding"""
    bom = detect_encoding_from_bom(filepath)
    if bom:
        return bom, "detected from BOM"
    
    can_utf8, error = can_decode_utf8(filepath)
    if can_utf8:
        return "UTF-8", "valid UTF-8"
    else:
        # Try other encodings
        for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
            try:
                with open(filepath, 'rb') as f:
                    f.read().decode(encoding)
                return encoding, f"decodable as {encoding}"
            except:
                continue
        return "UNKNOWN", error

# Find all HTML files
html_files = sorted(glob.glob(r'backend/**/*.html', recursive=True))

print(f"Analyzing encoding of {len(html_files)} HTML files...\n")

problem_files = []
for filepath in html_files:
    encoding, note = analyze_encoding(filepath)
    if encoding != "UTF-8":
        problem_files.append((filepath, encoding, note))
        print(f"❌ {filepath}")
        print(f"   Encoding: {encoding} ({note})\n")

print("\n" + "="*80)
if problem_files:
    print(f"Found {len(problem_files)} files NOT in UTF-8 encoding:")
    for path, enc, note in problem_files:
        print(f"  {path}: {enc}")
else:
    print(f"✓ All {len(html_files)} files are already UTF-8 encoded!")

print("="*80)
