#!/usr/bin/env python3
"""Run encoding checks and fixes"""
import subprocess
import sys

# Step 1: Run check_encoding.py
print("=" * 70)
print("STEP 1: CHECKING ENCODING ISSUES")
print("=" * 70)
result1 = subprocess.run([sys.executable, 'check_encoding.py'], capture_output=True, text=True)
print(result1.stdout)
if result1.stderr:
    print("STDERR:", result1.stderr)

# Step 2: Run fix_all_encodings.py
print("\n" + "=" * 70)
print("STEP 2: FIXING ENCODING ISSUES")
print("=" * 70)
result2 = subprocess.run([sys.executable, 'fix_all_encodings.py'], capture_output=True, text=True)
print(result2.stdout)
if result2.stderr:
    print("STDERR:", result2.stderr)

# Step 3: Run check_encoding.py again
print("\n" + "=" * 70)
print("STEP 3: VERIFYING ALL FILES ARE UTF-8")
print("=" * 70)
result3 = subprocess.run([sys.executable, 'check_encoding.py'], capture_output=True, text=True)
print(result3.stdout)
if result3.stderr:
    print("STDERR:", result3.stderr)

print("\n" + "=" * 70)
print("ENCODING CHECK AND FIX COMPLETE")
print("=" * 70)
