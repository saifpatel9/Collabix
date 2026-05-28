#!/usr/bin/env python3
import os
import glob
import sys

try:
    os.chdir(r"c:\Users\DIVYA PATHAK\Collabix")
    
    # Find all HTML files
    html_files = sorted(glob.glob(r'backend/**/*.html', recursive=True))
    
    # Check encoding
    problem_files = []
    converted_files = []
    
    print(f"Found {len(html_files)} HTML files")
    print(f"Checking encoding...\n")
    
    for filepath in html_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                f.read()
        except UnicodeDecodeError as e:
            problem_files.append(filepath)
            print(f"ERROR: {filepath}")
    
    # Fix problem files
    if problem_files:
        print(f"\nFound {len(problem_files)} files with encoding issues")
        print(f"Converting to UTF-8...\n")
        
        encodings_to_try = ['latin-1', 'cp1252', 'iso-8859-1', 'utf-8-sig']
        
        for filepath in problem_files:
            converted = False
            for encoding in encodings_to_try:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        content = f.read()
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✓ Converted {filepath} from {encoding}")
                    converted_files.append((filepath, encoding))
                    converted = True
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
            
            if not converted:
                try:
                    with open(filepath, 'rb') as f:
                        content = f.read().decode('utf-8', errors='replace')
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✓ Converted {filepath} with error replacement")
                    converted_files.append((filepath, 'error replacement'))
                except Exception as e:
                    print(f"✗ Failed to convert {filepath}: {str(e)}")
    else:
        print(f"All {len(html_files)} files are already UTF-8 encoded")
    
    # Verify
    print(f"\nVerifying all files are UTF-8...\n")
    still_broken = []
    for filepath in html_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                f.read()
        except UnicodeDecodeError as e:
            still_broken.append(filepath)
            print(f"STILL BROKEN: {filepath}")
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total HTML files: {len(html_files)}")
    print(f"Initial encoding issues: {len(problem_files)}")
    print(f"Successfully fixed: {len(converted_files)}")
    print(f"Remaining issues: {len(still_broken)}")
    
    if still_broken:
        print(f"\nStill broken files:")
        for f in still_broken:
            print(f"  - {f}")
    else:
        print(f"\n✓ All files are now UTF-8 encoded!")
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
