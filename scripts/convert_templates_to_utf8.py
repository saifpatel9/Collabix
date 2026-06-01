#!/usr/bin/env python3
"""Recursively convert all .html template files under backend/templates and frontend/templates to UTF-8.

Usage: python scripts/convert_templates_to_utf8.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIRS = [ROOT / 'backend' / 'templates', ROOT / 'backend' / 'frontend' / 'templates']

encodings_to_try = ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1', 'iso-8859-1']

fixed = 0
failed = []

for tdir in TEMPLATE_DIRS:
    if not tdir.exists():
        continue
    for path in tdir.rglob('*.html'):
        try:
            raw = path.read_bytes()
        except Exception as e:
            failed.append((str(path), f'read error: {e}'))
            continue

        decoded = None
        used = None
        for enc in encodings_to_try:
            try:
                decoded = raw.decode(enc)
                used = enc
                break
            except Exception:
                continue
        if decoded is None:
            # last resort: replace errors
            try:
                decoded = raw.decode('utf-8', errors='replace')
                used = 'utf-8 (replace)'
            except Exception as e:
                failed.append((str(path), f'decode failed: {e}'))
                continue

        # if already utf-8 and no replacement needed, skip rewrite
        if used == 'utf-8':
            continue

        try:
            path.write_text(decoded, encoding='utf-8')
            fixed += 1
            print(f"Converted {path} from {used} -> utf-8")
        except Exception as e:
            failed.append((str(path), f'write error: {e}'))

print('\nSummary:')
print(f'  Converted: {fixed}')
print(f'  Failed: {len(failed)}')
if failed:
    for p, msg in failed:
        print(f'    {p}: {msg}')

if failed:
    sys.exit(2)
else:
    sys.exit(0)
