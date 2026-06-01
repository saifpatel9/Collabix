#!/usr/bin/env python3
import os, glob, sys
os.chdir(r"c:\Users\DIVYA PATHAK\Collabix")
html_files = sorted(glob.glob(r'backend/**/*.html', recursive=True))
problem_files = []
for fpath in html_files:
    try:
        with open(fpath, 'r', encoding='utf-8') as f: f.read()
    except UnicodeDecodeError:
        problem_files.append(fpath)
fixed = 0
if problem_files:
    encodings = ['latin-1', 'cp1252', 'iso-8859-1', 'utf-8-sig']
    for fpath in problem_files:
        for enc in encodings:
            try:
                with open(fpath, 'r', encoding=enc) as f: content = f.read()
                with open(fpath, 'w', encoding='utf-8') as f: f.write(content)
                fixed += 1
                break
            except: pass
still_broken = []
for fpath in html_files:
    try:
        with open(fpath, 'r', encoding='utf-8') as f: f.read()
    except: still_broken.append(fpath)
report = f"""ENCODING CHECK REPORT
=====================

FINDINGS:
- Total HTML files: {len(html_files)}
- Files with encoding issues: {len(problem_files)}
- Files converted: {fixed}
- Remaining issues: {len(still_broken)}

STATUS: {"✓ COMPLETE" if len(still_broken) == 0 else "⚠ INCOMPLETE"}
"""
with open(r"c:\Users\DIVYA PATHAK\Collabix\REPORT.txt", "w") as f: f.write(report)
print(report)
