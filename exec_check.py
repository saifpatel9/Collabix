#!/usr/bin/env python3
code = """
import os, glob

os.chdir(r'c:\\Users\\DIVYA PATHAK\\Collabix')

html_files = sorted(glob.glob(r'backend/**/*.html', recursive=True))
print(f'Total HTML files: {len(html_files)}')

problem_files = []
for fpath in html_files:
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            f.read()
    except UnicodeDecodeError:
        problem_files.append(fpath)

print(f'Files with encoding issues: {len(problem_files)}')

if problem_files:
    print('\\nConverting files...')
    fixed = 0
    encodings = ['latin-1', 'cp1252', 'iso-8859-1', 'utf-8-sig']
    
    for fpath in problem_files:
        converted = False
        for enc in encodings:
            try:
                with open(fpath, 'r', encoding=enc) as f:
                    content = f.read()
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'✓ {fpath} (from {enc})')
                fixed += 1
                converted = True
                break
            except:
                pass
        
        if not converted:
            try:
                with open(fpath, 'rb') as f:
                    content = f.read()
                text = content.decode('utf-8', errors='replace')
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f'✓ {fpath} (error replacement)')
                fixed += 1
            except:
                print(f'✗ {fpath} (failed)')

    print(f'\\nFixed: {fixed} files')

# Verify
still_broken = []
for fpath in html_files:
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            f.read()
    except UnicodeDecodeError:
        still_broken.append(fpath)

print(f'\\nFinal Status: {len(still_broken)} files still broken')
if len(still_broken) == 0:
    print('✓ All files are UTF-8 encoded!')
"""

exec(code)
