#!/usr/bin/env python3
"""
Manual encoding analysis of HTML files
This script will be executed and provide the encoding report
"""

import os
import glob

def check_utf8_validity(file_path):
    """Check if file is valid UTF-8"""
    try:
        with open(file_path, 'rb') as f:
            f.read().decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False

# Get all HTML files
html_files = sorted(glob.glob(r'backend/**/*.html', recursive=True))

print("\n" + "="*80)
print("ENCODING ANALYSIS REPORT")
print("="*80)
print(f"Total HTML files to check: {len(html_files)}\n")

# Check encoding of each file
non_utf8_files = []
for i, html_file in enumerate(html_files, 1):
    is_valid_utf8 = check_utf8_validity(html_file)
    if not is_valid_utf8:
        non_utf8_files.append(html_file)
        print(f"[{i:3d}/{len(html_files)}] ❌ {html_file} - NOT UTF-8")
    else:
        print(f"[{i:3d}/{len(html_files)}] ✓ {html_file}")

print("\n" + "="*80)
print("RESULTS")
print("="*80)

if non_utf8_files:
    print(f"\n❌ Found {len(non_utf8_files)} files with encoding issues:\n")
    for f in non_utf8_files:
        print(f"  • {f}")
    
    # Now fix them
    print("\n" + "="*80)
    print("ATTEMPTING TO FIX ENCODING ISSUES")
    print("="*80 + "\n")
    
    fixed_count = 0
    for file_path in non_utf8_files:
        encodings = ['latin-1', 'cp1252', 'iso-8859-1', 'utf-8-sig']
        
        for encoding in encodings:
            try:
                # Read with this encoding
                with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                    content = f.read()
                
                # Write as UTF-8
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✓ Fixed: {file_path}")
                print(f"  Converted from: {encoding}\n")
                fixed_count += 1
                break
            except Exception as e:
                continue
        else:
            # If no encoding worked, use error replacement
            try:
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='replace')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ Fixed: {file_path}")
                print(f"  Converted with error replacement\n")
                fixed_count += 1
            except Exception as e:
                print(f"✗ Failed to fix: {file_path}")
                print(f"  Error: {e}\n")
    
    # Verify
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80 + "\n")
    
    still_broken = []
    for file_path in non_utf8_files:
        if not check_utf8_validity(file_path):
            still_broken.append(file_path)
            print(f"❌ Still not UTF-8: {file_path}")
        else:
            print(f"✓ Now UTF-8: {file_path}")
    
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"Total files checked: {len(html_files)}")
    print(f"Files with initial encoding issues: {len(non_utf8_files)}")
    print(f"Files successfully fixed: {fixed_count}")
    print(f"Files still with issues: {len(still_broken)}")
    
else:
    print(f"\n✓ SUCCESS: All {len(html_files)} HTML files are already UTF-8 encoded!")
    print("No encoding issues found.")

print("="*80 + "\n")
