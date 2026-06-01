#!/usr/bin/env python3
"""
Encoding Check and Conversion Script
Checks all HTML files under backend/ for UTF-8 encoding
Converts any non-UTF-8 files to UTF-8
Generates a detailed report
"""

import os
import glob
import sys
from pathlib import Path

def main():
    # Change to project directory
    project_dir = r"c:\Users\DIVYA PATHAK\Collabix"
    os.chdir(project_dir)
    
    print("="*80)
    print("HTML ENCODING CHECK AND FIX")
    print("="*80)
    print(f"Working directory: {os.getcwd()}\n")
    
    # Step 1: Find all HTML files
    html_files = sorted(glob.glob(r'backend/**/*.html', recursive=True))
    print(f"STEP 1: Found {len(html_files)} HTML files")
    print("-"*80 + "\n")
    
    # Step 2: Check encoding issues
    print("STEP 2: CHECKING ENCODING")
    print("-"*80)
    problem_files = []
    
    for i, fpath in enumerate(html_files, 1):
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                f.read()
            status = "✓ UTF-8"
        except UnicodeDecodeError as e:
            problem_files.append(fpath)
            status = "✗ NOT UTF-8"
        
        if status.startswith("✗"):
            print(f"  [{i:2d}/{len(html_files)}] {status}: {fpath}")
    
    print(f"\nSummary: {len(problem_files)} files with encoding issues\n")
    
    # Step 3: Fix encoding
    print("STEP 3: FIXING ENCODING ISSUES")
    print("-"*80)
    
    fixed_count = 0
    failed_count = 0
    
    if problem_files:
        for fpath in problem_files:
            success = False
            # Try different encodings
            for enc in ['latin-1', 'cp1252', 'iso-8859-1', 'utf-8-sig']:
                try:
                    with open(fpath, 'r', encoding=enc, errors='strict') as f:
                        content = f.read()
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✓ Fixed {fpath}")
                    print(f"  Converted from: {enc}")
                    fixed_count += 1
                    success = True
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
            
            if not success:
                # Last resort: use error replacement
                try:
                    with open(fpath, 'rb') as f:
                        content = f.read()
                    text = content.decode('utf-8', errors='replace')
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.write(text)
                    print(f"✓ Fixed {fpath}")
                    print(f"  Method: Error replacement (may have lost data)")
                    fixed_count += 1
                except Exception as e:
                    print(f"✗ Failed to fix {fpath}")
                    print(f"  Error: {str(e)}")
                    failed_count += 1
    else:
        print("No encoding issues found!\n")
    
    # Step 4: Verify
    print("\nSTEP 4: VERIFICATION")
    print("-"*80)
    
    still_broken = []
    for fpath in html_files:
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                f.read()
        except UnicodeDecodeError:
            still_broken.append(fpath)
    
    if still_broken:
        print(f"⚠️ WARNING: {len(still_broken)} files still have encoding issues")
        for f in still_broken:
            print(f"  - {f}")
    else:
        print(f"✓ SUCCESS: All {len(html_files)} files are UTF-8 encoded")
    
    # Final Report
    print("\n" + "="*80)
    print("FINAL REPORT")
    print("="*80)
    print(f"1. Total HTML files found: {len(html_files)}")
    print(f"2. Files with initial encoding issues: {len(problem_files)}")
    print(f"3. Files converted:")
    print(f"   - Successfully fixed: {fixed_count}")
    print(f"   - Failed to fix: {failed_count}")
    if problem_files and fixed_count > 0:
        for i, f in enumerate(problem_files[:fixed_count], 1):
            print(f"   - {f}")
    print(f"4. Final status:")
    print(f"   - Total files: {len(html_files)}")
    print(f"   - Initial issues: {len(problem_files)}")
    print(f"   - Successfully fixed: {fixed_count}")
    print(f"   - Remaining issues: {len(still_broken)}")
    print(f"   - Status: {'✓ COMPLETE - All files are UTF-8' if len(still_broken) == 0 else '⚠ INCOMPLETE'}")
    print("="*80)

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
