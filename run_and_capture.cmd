@echo off
cd /d "c:\Users\DIVYA PATHAK\Collabix"
python inline_encoding_check.py > encoding_output.log 2>&1
type encoding_output.log
