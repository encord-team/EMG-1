"""Verify the full release or the documented starter subset."""
import argparse,hashlib
from starter_subset import selected,aws_patterns
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('root',nargs='?',default='.');p.add_argument('--require-all',action='store_true');p.add_argument('--subset',choices=['starter']);a=p.parse_args();r=Path(a.root)
sums=r/'SHA256SUMS'
if not sums.is_file():raise SystemExit(f'Wrong release root: {sums} is missing')
lines=sums.read_text().splitlines();all_keys=[line.split('  ',1)[1] for line in lines]+['SHA256SUMS'];starter_patterns=aws_patterns(all_keys)
missing=bad=good=0
for line in lines:
 digest,key=line.split('  ',1)
 if a.subset=='starter' and not selected(key,starter_patterns):continue
 path=r/key
 if not path.is_file():missing+=1;continue
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 if h.hexdigest()!=digest:bad+=1;print('mismatch',key)
 else:good+=1
print('verified',good,'missing',missing,'mismatches',bad)
raise SystemExit(bool(bad or good==0 or (a.subset=='starter' and missing) or (a.require_all and missing)))
