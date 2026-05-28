#!/usr/bin/env python3
import os
import glob
import sys

os.chdir(r"c:\Users\DIVYA PATHAK\Collabix")

# Import and run check_encoding.py
print("="*80)
print("STEP 1: CHECKING ENCODING ISSUES")
print("="*80)

def check_file_encoding(filepath):
    """Check if a file can be decoded as UTF-8"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read()
        return True, None
    except UnicodeDecodeError as e:
        return False, str(e)

# Find all HTML files
html_files = glob.glob(r'backend/**/*.html', recursive=True)
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
else:
    print(f"✓ All {len(html_files)} files are UTF-8 encoded")

# Now fix them
print("\n" + "="*80)
print("STEP 2: FIXING ENCODING ISSUES")
print("="*80)

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

if problem_files:
    fixed = 0
    errors = 0
    for filepath, _ in sorted(problem_files):
        success, message = fix_file_encoding(filepath)
        if success:
            print(f"✓ {filepath}")
            print(f"  {message}")
            fixed += 1
        else:
            print(f"✗ {filepath}")
            print(f"  ERROR: {message}")
            errors += 1
    
    print(f"\nFixed: {fixed}, Errors: {errors}")
else:
    print("No files to fix - all already UTF-8")

# Verify
print("\n" + "="*80)
print("STEP 3: VERIFYING ALL FILES ARE NOW UTF-8")
print("="*80)

still_broken = []
for filepath in html_files:
    ok, error = check_file_encoding(filepath)
    if not ok:
        still_broken.append((filepath, error))
        print(f"❌ STILL BROKEN: {filepath}")
        print(f"   {error}\n")

if still_broken:
    print(f"\n⚠️  WARNING: {len(still_broken)} files still have encoding issues")
else:
    print(f"✓ All {len(html_files)} files are now UTF-8 encoded")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total HTML files: {len(html_files)}")
print(f"Initial encoding issues: {len(problem_files)}")
print(f"Successfully fixed: {len(problem_files) - len(still_broken)}")
print(f"Remaining issues: {len(still_broken)}")

# Write output to file so we can read it
with open(r"c:\Users\DIVYA PATHAK\Collabix\encoding_check_output.txt", "w", encoding='utf-8') as outfile:
    outfile.write("ENCODING CHECK RESULTS\n")
    outfile.write(f"Total HTML files: {len(html_files)}\n")
    outfile.write(f"Initial encoding issues: {len(problem_files)}\n")
    outfile.write(f"Successfully fixed: {len(problem_files) - len(still_broken)}\n")
    outfile.write(f"Remaining issues: {len(still_broken)}\n")
