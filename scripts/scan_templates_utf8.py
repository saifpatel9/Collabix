from pathlib import Path
bad=[]
for p in Path('backend').rglob('templates/**/*.html'):
    try:
        p.read_text(encoding='utf-8')
    except Exception as e:
        bad.append((str(p),str(e)))
for p in Path('backend').rglob('templates/*.html'):
    try:
        p.read_text(encoding='utf-8')
    except Exception as e:
        bad.append((str(p),str(e)))
if bad:
    print('BAD FILES')
    for f,e in bad:
        print(f, e)
else:
    print('No non-UTF8 template issues found')
