#!/usr/bin/env python3
"""Direct encoding check - writes results to file"""

import os
import glob
import sys

def main():
    os.chdir(r"c:\Users\DIVYA PATHAK\Collabix")
    
    # Get all HTML files
    html_files = sorted(glob.glob(r'backend/**/*.html', recursive=True))
    
    # Check each file
    problems = []
    for fpath in html_files:
        try:
            with open(fpath, 'rb') as f:
                data = f.read()
            # Try to decode as UTF-8
            try:
                data.decode('utf-8')
            except UnicodeDecodeError:
                problems.append(fpath)
        except Exception as e:
            pass
    
    # Write summary
    summary = f"""ENCODING CHECK RESULTS
====================
Total HTML files: {len(html_files)}
Files with UTF-8 encoding issues: {len(problems)}

Problem files:
"""
    for p in problems:
        summary += f"\n  {p}"
    
    # Write to file
    with open(r"c:\Users\DIVYA PATHAK\Collabix\encoding_summary.txt", "w") as f:
        f.write(summary)
    
    print(summary)
    print("\nResults written to encoding_summary.txt")

if __name__ == "__main__":
    main()
