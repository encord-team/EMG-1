"""Verify full or partial release against SHA256SUMS and MANIFEST.parquet."""
import argparse,hashlib
from pathlib import Path
import pyarrow.parquet as pq

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('root',type=Path);a.add_argument('--ignore-missing',action='store_true');x=a.parse_args();root=x.root
 rows=[]
 for line in (root/'SHA256SUMS').read_text().splitlines():
  digest,key=line.split('  ',1);rows.append((key,digest))
 missing=[];bad=[];checked=0
 for key,d in rows:
  p=root/key
  if not p.is_file():missing.append(key);continue
  checked+=1
  if sha(p)!=d:bad.append(key)
 manifest=pq.read_table(root/'MANIFEST.parquet').to_pylist();by_key={r['key']:r for r in manifest};listed=set(by_key)
 expected={key for key,_ in rows if key!='MANIFEST.parquet'}
 if listed!=expected:bad.append('MANIFEST key set')
 for key,d in rows:
  if key=='MANIFEST.parquet' or key not in by_key:continue
  row=by_key[key]
  if row['sha256']!=d:bad.append('MANIFEST digest: '+key)
  if (root/key).is_file() and row['bytes']!=(root/key).stat().st_size:bad.append('MANIFEST size: '+key)
 print(f'checked={checked} missing={len(missing)} mismatches={len(bad)}')
 if bad:print('mismatches:',bad[:20])
 if missing and not x.ignore_missing:raise SystemExit(1)
 if bad:raise SystemExit(1)
if __name__=='__main__':main()
