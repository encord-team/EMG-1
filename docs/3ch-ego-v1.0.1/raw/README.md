# Original MCAP recordings

Original MCAP recordings live under `v1.0.1/raw/<station>/<date>/<clip_id>.mcap`. The 4,916 destination objects (43.22 TB) are reconciled by key, size and ETag in `RAW_OBJECTS.csv`. Multipart ETags are not SHA256 content digests.

| RAW_OBJECTS.csv column | Meaning |
| --- | --- |
| `clip_id` | Recording clip identifier, matching the raw filename stem. |
| `release_key` | Full destination key, including `v1.0.1/`. |
| `bytes` | Destination object length. |
| `etag` | Destination ETag after normalization; a multipart ETag is not a SHA256 digest. |
| `part_size` | Inferred multipart part size in bytes when the 64 MiB inference matches the part count; blank otherwise. |

`copy_manifest.csv` records destination keys, planned sizes, and source ETags for the copy operation. `starter/raw_copy_keys.csv` provides the same subset for the starter clips. These are copy plans, not access indexes; use `RAW_OBJECTS.csv` for destination lookup. The copy plans omit `source_key`; the clip index, vendor sidecars and pose files retain it for provenance.

| Loader stream | MCAP topic | Content |
| --- | --- | --- |
| `head_left` | `/ego/zed_head/left/image_compressed` | Rectified left image. |
| `head_right` | `/ego/zed_head/right/image_compressed` | Right stereo image. |
| `depth` | `/ego/zed_head/depth/image_compressed` | Neural stereo depth estimate. |
| `wrist_left` | `/wrist_left/image_compressed` | Left wrist image. |
| `wrist_right` | `/wrist_right/image_compressed` | Right wrist image. |

The MCAPs also contain camera calibration, head and wrist camera IMUs, odometry, transforms, and band EMG, IMU and PPG. Raw MCAPs keep the recorder metadata, including station hostnames and account-like recording strings, some in email format. These strings are stand-in values, not personal contact details. Extracted L1 files have those account fields removed. Video is not visually anonymised. The raw MCAPs, including the ego video, are released under CC BY 4.0 with the rest of the data; see `LICENSE` and `TERMS.md`.

## Downloading raw recordings

Raw MCAPs are not listed in `SHA256SUMS`. `tools/download.py` downloads them only with `--raw`, using the keys, sizes and ETags in `RAW_OBJECTS.csv`, and checks each one by size and ETag. Take `BASE_URL` from the bucket-root `README.md`, outside the `v1.0.1/` prefix. For one recording, inside a release tree that already has the starter, replace `CLIP_ID` with a `clip_id` from `RAW_OBJECTS.csv` and run:

```sh
python -B tools/download.py "$BASE_URL" . --raw --include 'raw/*/*/CLIP_ID.mcap'
python -B tools/verify_raw.py . CLIP_ID
```

`tools/verify_raw.py` checks the local file content against its listed ETag. `--include 'raw/*.mcap'` selects every raw recording. A full raw download is 43.22 TB.

## Reading frames over HTTPS

After reconciliation, this optional example requests a compressed image near a starter EMG timestamp with HTTPS range requests, without downloading the whole MCAP. It needs the packages in `requirements-video.txt`. Set the `BASE_URL` environment variable to the public base URL first.

```python
import csv, json, os, sys, urllib.request
from pathlib import Path
sys.path.insert(0, "loader")
from emg1_ego import EMGWindowDataset
from emg1_ego.video import video_frame_at
root = '.'
base_url = os.environ['BASE_URL'].rstrip('/')
ids = json.loads((Path(root)/'starter/clips.json').read_text())['clip_ids']
dataset = EMGWindowDataset(root, clip_ids=ids, split=None, available_only=True)
batch = dataset[0]
with (Path(root)/'raw/RAW_OBJECTS.csv').open() as f:
    row = next(r for r in csv.DictReader(f) if r['clip_id'] == batch['clip_id'])
url = base_url + '/' + row['release_key']
etag = row['etag'] if row['etag'].startswith('"') else '"' + row['etag'] + '"'
def read_range(offset, count):
    request = urllib.request.Request(url, headers={'Range': f'bytes={offset}-{offset + count - 1}', 'If-Match': etag})
    with urllib.request.urlopen(request) as response:
        if response.status != 206:
            raise RuntimeError(f'expected HTTP 206 Partial Content for a range read, got {response.status}')
        return response.read()
frame = video_frame_at(batch['clip_id'], 'head_left', int(batch['t_ns'][0,0]), root=root, read_range=read_range)
```

MCAP `log_time` and EMG `t_ns_est` use the same recorder host clock; on starter clips, their ends agree within tens of milliseconds. Neither is exposure time. Camera header stamps can slip. Inspect returned `delta_ns`, decode `data` according to `format`, and keep the `etag` with cached frame references. Range reads use `If-Match` against the reconciled ETag and accept only a 206 Partial Content response, so a server that ignores the `Range` header cannot hand back the whole object.
