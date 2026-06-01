#!/usr/bin/env python3
"""
Standalone script to execute encoding check
This will run and generate output as a file for reading
"""

if __name__ == "__main__":
    import os
    import glob
    import sys
    
    os.chdir(r"c:\Users\DIVYA PATHAK\Collabix")
    
    output = []
    
    # Find all HTML files
    html_files = sorted(glob.glob(r'backend/**/*.html', recursive=True))
    
    output.append("="*80)
    output.append("HTML ENCODING CHECK AND FIX REPORT")
    output.append("="*80)
    output.append(f"\nTotal HTML files found: {len(html_files)}\n")
    
    # Check encoding
    problem_files = []
    
    for i, filepath in enumerate(html_files, 1):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                f.read()
            output.append(f"{i:3d}. {filepath}")
        except UnicodeDecodeError as e:
            problem_files.append(filepath)
            output.append(f"{i:3d}. {filepath} - ERROR: NOT UTF-8")
    
    output.append(f"\n{'='*80}")
    output.append(f"Initial Check Results:")
    output.append(f"{'='*80}")
    output.append(f"Total HTML files: {len(html_files)}")
    output.append(f"Files with encoding issues: {len(problem_files)}")
    
    if problem_files:
        output.append(f"\nFiles with issues:")
        for f in problem_files:
            output.append(f"  - {f}")
    
    # Fix encoding
    fixed_count = 0
    fixed_files = []
    
    if problem_files:
        output.append(f"\n{'='*80}")
        output.append(f"Fixing Encoding Issues:")
        output.append(f"{'='*80}")
        
        encodings_to_try = ['latin-1', 'cp1252', 'iso-8859-1', 'utf-8-sig']
        
        for filepath in problem_files:
            converted = False
            for encoding in encodings_to_try:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        content = f.read()
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    output.append(f"✓ Converted: {filepath}")
                    output.append(f"  Original encoding: {encoding}")
                    fixed_count += 1
                    fixed_files.append(filepath)
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
                    output.append(f"✓ Converted: {filepath}")
                    output.append(f"  Method: Error replacement")
                    fixed_count += 1
                    fixed_files.append(filepath)
                except Exception as e:
                    output.append(f"✗ Failed to convert: {filepath}")
                    output.append(f"  Error: {str(e)}")
    
    # Verify
    output.append(f"\n{'='*80}")
    output.append(f"Verification:")
    output.append(f"{'='*80}")
    
    still_broken = []
    for filepath in html_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                f.read()
        except UnicodeDecodeError as e:
            still_broken.append(filepath)
    
    output.append(f"Files with remaining encoding issues: {len(still_broken)}")
    
    if still_broken:
        output.append(f"\nRemaining broken files:")
        for f in still_broken:
            output.append(f"  - {f}")
    else:
        output.append(f"✓ All files are now UTF-8 encoded!")
    
    # Final summary
    output.append(f"\n{'='*80}")
    output.append(f"FINAL SUMMARY")
    output.append(f"{'='*80}")
    output.append(f"1. How many HTML files were found: {len(html_files)}")
    output.append(f"2. How many had encoding issues: {len(problem_files)}")
    output.append(f"3. Which files were converted: {fixed_count} files")
    if fixed_files:
        for f in fixed_files:
            output.append(f"   - {f}")
    output.append(f"4. Final summary:")
    output.append(f"   - Total files: {len(html_files)}")
    output.append(f"   - Initial issues: {len(problem_files)}")
    output.append(f"   - Fixed: {fixed_count}")
    output.append(f"   - Remaining issues: {len(still_broken)}")
    output.append(f"   - Status: {'✓ COMPLETE' if len(still_broken) == 0 else '⚠ INCOMPLETE'}")
    
    # Write to file
    result_text = "\n".join(output)
    
    with open(r"c:\Users\DIVYA PATHAK\Collabix\ENCODING_CHECK_RESULTS.txt", "w", encoding='utf-8') as f:
        f.write(result_text)
    
    # Also print to stdout
    print(result_text)
    print(f"\n✓ Results saved to: c:\\Users\\DIVYA PATHAK\\Collabix\\ENCODING_CHECK_RESULTS.txt")
