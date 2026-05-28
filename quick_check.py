import os
import glob

os.chdir(r"c:\Users\DIVYA PATHAK\Collabix")

# Find all HTML files
html_files = sorted(glob.glob(r'backend/**/*.html', recursive=True))
print(f"Total HTML files found: {len(html_files)}\n")

# Check encoding
problem_files = []
print("Checking encoding...\n")

for i, filepath in enumerate(html_files, 1):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read()
        status = "✓ UTF-8"
    except UnicodeDecodeError as e:
        status = f"✗ NOT UTF-8"
        problem_files.append(filepath)
    print(f"{i:2d}. {filepath:80s} {status}")

print(f"\n\n{'='*80}")
print(f"SUMMARY:")
print(f"{'='*80}")
print(f"Total HTML files: {len(html_files)}")
print(f"Files with encoding issues: {len(problem_files)}")
print(f"\nFiles with issues:")
for f in problem_files:
    print(f"  - {f}")
