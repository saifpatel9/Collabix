import subprocess
import os
import sys

os.chdir(r"c:\Users\DIVYA PATHAK\Collabix")

print("="*80)
print("STEP 1: CHECKING INITIAL ENCODING")
print("="*80)
subprocess.call([sys.executable, "check_encoding.py"])

print("\n" + "="*80)
print("STEP 2: FIXING ENCODINGS")
print("="*80)
subprocess.call([sys.executable, "fix_all_encodings.py"])

print("\n" + "="*80)
print("STEP 3: VERIFYING ENCODINGS")
print("="*80)
subprocess.call([sys.executable, "check_encoding.py"])
