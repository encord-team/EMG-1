"""Verify one local raw MCAP using the reconciled destination listing."""
import argparse,csv,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('clip_id');a=p.parse_args();r=Path(a.root)
sys.path.insert(0,str(r/'loader'))
from emg1_ego.video import _local_raw_identity
with (r/'raw/RAW_OBJECTS.csv').open() as f:row=next((x for x in csv.DictReader(f) if x['clip_id']==a.clip_id),None)
if row is None:raise SystemExit('Destination listing pending or clip absent')
key=row['release_key'].removeprefix('v1.0.1/')
if not (r/key).is_file():raise SystemExit(f"raw object not downloaded: {key}; run python3 -B tools/download.py <BASE_URL> . --sums-sha256 <SHA256SUMS digest> --raw --include '{key}'")
_local_raw_identity(r/key,row)
print('verified',a.clip_id)
