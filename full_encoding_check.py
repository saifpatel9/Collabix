#!/usr/bin/env python3
"""
Comprehensive encoding check and fix script
"""
import os
import glob
import chardet

def detect_file_encoding(filepath):
    """Detect actual encoding of a file using chardet"""
    try:
        with open(filepath, 'rb') as f:
            raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding'], result['confidence']
    except Exception as e:
        return 'error', str(e)

def check_file_encoding(filepath):
    """Check if a file can be decoded as UTF-8"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read()
        return True, None
    except UnicodeDecodeError as e:
        return False, str(e)

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
html_files = sorted(glob.glob(r'backend/**/*.html', recursive=True))
print(f"Found {len(html_files)} HTML files\n")

print("="*80)
print("STEP 1: CHECKING INITIAL ENCODING STATUS")
print("="*80)

problem_files = []
for filepath in html_files:
    is_utf8, error = check_file_encoding(filepath)
    if not is_utf8:
        detected_enc, confidence = detect_file_encoding(filepath)
        problem_files.append({
            'path': filepath,
            'detected': detected_enc,
            'confidence': confidence,
            'error': error
        })
        print(f"❌ {filepath}")
        print(f"   Detected: {detected_enc} (confidence: {confidence})")
        print(f"   Error: {error}\n")

if not problem_files:
    print("✓ All files are already UTF-8 encoded!")
else:
    print(f"\nFound {len(problem_files)} files with encoding issues:\n")
    for pf in problem_files:
        print(f"  - {pf['path']}")
        print(f"    Detected as: {pf['detected']}")

print("\n" + "="*80)
print("STEP 2: FIXING ENCODING ISSUES")
print("="*80)

if problem_files:
    for pf in problem_files:
        filepath = pf['path']
        success, message = fix_file_encoding(filepath)
        if success:
            print(f"✓ {filepath}")
            print(f"  {message}\n")
        else:
            print(f"✗ {filepath}")
            print(f"  ERROR: {message}\n")

print("\n" + "="*80)
print("STEP 3: VERIFYING ALL FILES ARE NOW UTF-8")
print("="*80)

still_broken = []
for filepath in html_files:
    is_utf8, error = check_file_encoding(filepath)
    if not is_utf8:
        still_broken.append(filepath)
        print(f"❌ STILL BROKEN: {filepath}")
        print(f"   Error: {error}\n")

if not still_broken:
    print("✓ All files are now UTF-8 encoded!")
else:
    print(f"\n⚠️  WARNING: {len(still_broken)} files still have encoding issues")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total HTML files: {len(html_files)}")
print(f"Files with initial encoding issues: {len(problem_files)}")
print(f"Files still with issues after fix: {len(still_broken)}")
if len(problem_files) == 0:
    print("\n✓ All files already had correct UTF-8 encoding!")
elif len(still_broken) == 0:
    print(f"\n✓ Successfully fixed all {len(problem_files)} encoding issue(s)!")
else:
    print(f"\n⚠️  Could not fix {len(still_broken)} file(s)")
