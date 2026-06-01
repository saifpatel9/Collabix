import subprocess
import sys

# Execute the full check report
result = subprocess.run([sys.executable, r'c:\Users\DIVYA PATHAK\Collabix\full_check_report.py'], 
                       capture_output=False, text=True)
sys.exit(result.returncode)
