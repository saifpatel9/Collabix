import subprocess
import sys

# Run the inline_encoding_check.py script and capture output
result = subprocess.run([sys.executable, r'c:\Users\DIVYA PATHAK\Collabix\inline_encoding_check.py'], 
                       capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
    
print(f"\nReturn code: {result.returncode}")
