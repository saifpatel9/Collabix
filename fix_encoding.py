#!/usr/bin/env python
"""Fix template encoding issues"""
import glob
import chardet

# Files that were identified as having non-UTF-8 bytes
problem_files = [
    'backend\\templates\\organization\\partials\\chart.html',
    'backend\\templates\\components\\audit_timeline.html'
]

for filepath in problem_files:
    try:
        # Read with binary mode to detect encoding
        with open(filepath, 'rb') as f:
            raw_data = f.read()
        
        # Detect encoding
        detected = chardet.detect(raw_data)
        current_encoding = detected.get('encoding', 'unknown')
        print(f"\n{filepath}")
        print(f"  Detected encoding: {current_encoding}")
        
        # Try to decode and re-encode as UTF-8
        try:
            # First try UTF-8
            text = raw_data.decode('utf-8')
            print(f"  Already UTF-8: No changes needed")
        except UnicodeDecodeError:
            # Try detected encoding
            try:
                text = raw_data.decode(current_encoding)
                print(f"  Converting from {current_encoding} to UTF-8...")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"  ✓ Converted successfully")
            except:
                # Try common encodings
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        text = raw_data.decode(encoding)
                        print(f"  Converting from {encoding} to UTF-8...")
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(text)
                        print(f"  ✓ Converted from {encoding}")
                        break
                    except:
                        pass
                else:
                    print(f"  ✗ Could not convert - unsupported encoding")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

print("\nDone!")
