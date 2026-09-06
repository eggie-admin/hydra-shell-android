#!/usr/bin/env python3
from pathlib import Path
import base64, hashlib, json
root=Path(__file__).resolve().parent
m=json.loads((root/'mirror.json').read_text())
text=''
for p in m['chunks']:
    s=(root/p['file']).read_text().strip()
    if hashlib.sha256(s.encode()).hexdigest()!=p['sha256']: raise SystemExit('CHUNK HASH FAIL: '+p['file'])
    text+=s
data=base64.b64decode(text,validate=True)
if hashlib.sha256(data).hexdigest()!=m['artifact_sha256']: raise SystemExit('ARTIFACT HASH FAIL')
out=root/m['artifact']; out.write_bytes(data)
print('RESTORE GREEN:',out)
