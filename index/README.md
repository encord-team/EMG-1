# Index of the buckets

The buckets cannot be listed over public HTTP, so this folder is the listing: one sub-folder per dataset, each a
snapshot of every object in that bucket. The structure comes from a listing of the bucket itself through the
Cloudflare API; the per-file tables come from the release's own manifests (`SHA256SUMS`, `MANIFEST.parquet` and its
index tables), each verified against its published digest, and `scripts/build_index.py <dataset>` checks the two
against each other.

| Folder | Dataset | Bucket |
| --- | --- | --- |
| `3ch-ego/` | EMG-1 3-channel dataset v1.0.1 | `emg1-3ch-ego-release` |
| `8ch-mocap/` | EMG-1 8-channel dataset v1.0.1 | `emg1-8ch-mocap-release` |

Inside each:

| File | Content |
| --- | --- |
| `RELEASE.json` | Dataset name, version, release date, bucket, base URL, the published digests of `SHA256SUMS` and `MANIFEST.parquet`, counts, total bytes, subset sizes and commands. The scripts read the base URL and digest from here. |
| `files.csv` | Every file of the extracted release: `key`, `bytes`, `sha256`. The URL is `<base_url>/<version>/<key>`. |
| `STRUCTURE.md` | The directory structure of the whole bucket as a tree, with repeated per-recording paths collapsed (`<clip_id>`, `<person>/<session>/<take>`) and counted. |
| `SUMMARY.md` | Totals per folder and subset, plus the dataset's own groupings (stations, splits, tiers, tasks; people, sessions, tiers). |
| `bucket_structure.json` | The bucket's own listing, taken through the Cloudflare API with Encord's account access on 2026-10-20: every object aggregated per collapsed path (files, bytes, example key, first and last upload date). `STRUCTURE.md` is built from it, and `build_index.py` compares it with the manifests and records the result in `RELEASE.json` under `bucket_listing`. |
| `bucket_objects.csv` | Optional: every object individually, written by `scripts/list_bucket.py` through R2's S3 API with an R2 token (`key`, `bytes`, `etag`, `last_modified`, `storage_class`). When present it takes precedence over `bucket_structure.json`. |
| `3ch-ego/clips.csv` | One row per clip (4,916): `station`, `date`, `session_id`, `station_day`, primary-split `split`, `clip_tier`, `left_tier`, `right_tier`, `duration_s`, dominant `task_category`, `clip_hours_with_emg`, `both_gold_standard_hours`, `starter`, and the key and size of its sensors file, clock-estimates file, wrist-pose file, vendor sidecar, the number of video frame tables, and its raw MCAP key, size and ETag. |
| `3ch-ego/raw_objects.csv` | Every raw MCAP recording (4,916; not in `SHA256SUMS`): `clip_id`, `release_key` (includes the version prefix), `bytes`, `etag`, `part_size`. Byte-identical to the release's `raw/RAW_OBJECTS.csv`. |
| `8ch-mocap/supplement_files.csv` | Every file of the Wearable Devices predictions supplement (401, outside `v1.0.1/`): `key` relative to the bucket root (`supplements/wd-fusion-predictions/v1/...`), `bytes`, `sha256`. |
| `8ch-mocap/takes.csv` | One row per take (920): `take` (`OP-001/s003/02`), `take_id`, `person`, `session`, `duration_s`, `emg_tier`, `multimodal_tier`, `default_partition`, `transport`, `lag_measured`, `lag_ms`, `emg_coverage`, `failed_channels`, `has_mediapipe_stereo_est`, `scenario_version`, `has_rest_phase`, `rest_posture`, `ppg_nominal_hz`, `starter`, and the key and size of its `take.h5`, `take.c3d`, `take.mcap` and `derived/.../automatic_est.h5`. |

These per-clip and per-take tables are convenience views. The releases' full index tables (about 100 columns for
3ch-ego clips, 79 for 8ch-mocap takes) are inside the downloads, documented in `docs/3ch-ego-v1.0.1/SCHEMA.md`
and `docs/8ch-mocap-v1.0.1/INDEX_DICTIONARY.md`.

Query them without downloading anything:

```sh
python3 scripts/list_release.py 3ch-ego --summary
python3 scripts/list_release.py 3ch-ego 'derived/wrist_poses_est/*egox-013*'
python3 scripts/list_release.py 3ch-ego --clip 20261005_egox-018_112656_888ded7e
python3 scripts/list_release.py 8ch-mocap --summary
python3 scripts/list_release.py 8ch-mocap --take OP-005/s007
python3 scripts/list_release.py 8ch-mocap --supplement 'supplements/*'
python3 scripts/list_release.py 8ch-mocap 'takes/*/take.h5' --urls > urls.txt && aria2c -i urls.txt
```

`python3 scripts/list_release.py <dataset> --refresh ...` reads the live bucket instead, and reports if its
`SHA256SUMS` digest no longer matches `RELEASE.json` (a new version). Maintainers refresh a folder with
`python3 scripts/build_index.py <dataset>` (needs pyarrow), after `python3 scripts/list_bucket.py <dataset>`
with an R2 token to capture the complete bucket listing.
