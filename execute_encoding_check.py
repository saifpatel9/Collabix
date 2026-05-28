#!/usr/bin/env python3
"""Execute encoding check and save results to file"""
import os
import glob
import sys

os.chdir(r"c:\Users\DIVYA PATHAK\Collabix")

output_lines = []

# STEP 1: Check encoding
output_lines.append("="*80)
output_lines.append("STEP 1: CHECKING ENCODING ISSUES")
output_lines.append("="*80)

def check_file_encoding(filepath):
    """Check if a file can be decoded as UTF-8"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read()
        return True, None
    except UnicodeDecodeError as e:
        return False, str(e)

# Find all HTML files
html_files = sorted(glob.glob(r'backend/**/*.html', recursive=True))
output_lines.append(f"Checking {len(html_files)} HTML files for encoding issues...\n")

problem_files = []
for filepath in html_files:
    ok, error = check_file_encoding(filepath)
    if not ok:
        problem_files.append((filepath, error))
        output_lines.append(f"❌ ERROR: {filepath}")
        output_lines.append(f"   {error}\n")

if problem_files:
    output_lines.append(f"\nFound {len(problem_files)} files with encoding issues")
else:
    output_lines.append(f"✓ All {len(html_files)} files are UTF-8 encoded")

# STEP 2: Fix encoding
output_lines.append("\n" + "="*80)
output_lines.append("STEP 2: FIXING ENCODING ISSUES")
output_lines.append("="*80)

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
            output_lines.append(f"✓ {filepath}")
            output_lines.append(f"  {message}")
            fixed += 1
        else:
            output_lines.append(f"✗ {filepath}")
            output_lines.append(f"  ERROR: {message}")
            errors += 1
    
    output_lines.append(f"\nFixed: {fixed}, Errors: {errors}")
else:
    output_lines.append("No files to fix - all already UTF-8")

# STEP 3: Verify
output_lines.append("\n" + "="*80)
output_lines.append("STEP 3: VERIFYING ALL FILES ARE NOW UTF-8")
output_lines.append("="*80)

still_broken = []
for filepath in html_files:
    ok, error = check_file_encoding(filepath)
    if not ok:
        still_broken.append((filepath, error))
        output_lines.append(f"❌ STILL BROKEN: {filepath}")
        output_lines.append(f"   {error}\n")

if still_broken:
    output_lines.append(f"\n⚠️  WARNING: {len(still_broken)} files still have encoding issues")
else:
    output_lines.append(f"✓ All {len(html_files)} files are now UTF-8 encoded")

# Summary
output_lines.append("\n" + "="*80)
output_lines.append("SUMMARY")
output_lines.append("="*80)
output_lines.append(f"Total HTML files: {len(html_files)}")
output_lines.append(f"Initial encoding issues: {len(problem_files)}")
output_lines.append(f"Successfully fixed: {len(problem_files) - len(still_broken)}")
output_lines.append(f"Remaining issues: {len(still_broken)}")

# Print to console and save to file
full_output = "\n".join(output_lines)
print(full_output)

# Save to file
with open(r"c:\Users\DIVYA PATHAK\Collabix\encoding_check_results.txt", "w", encoding='utf-8') as f:
    f.write(full_output)

print("\n✓ Results saved to encoding_check_results.txt")
