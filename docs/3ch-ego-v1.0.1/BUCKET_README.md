# EMG-1 3-channel dataset: download and verification

The public base URL is given in the bucket-root `README.md`, outside the `v1.0.1/` prefix; it is not stored inside the release. Use that URL as `BASE_URL` in the commands below.

This is a free and open release. The data are licensed under CC BY 4.0 and the source code (every `.py` file and `requirements*.txt`) under Apache-2.0; see `LICENSE`, `LICENSE-CODE` and `TERMS.md`. No account, access key or agreement is needed. Credit the data as "EMG-1 3-channel dataset, Vineeth Velmurugan, Encord, 2026, CC BY 4.0".

Files are served over public HTTPS from the `emg1-3ch-ego-release` bucket. The bucket root contains a `README.md` and the `v1.0.1/` prefix. Objects under a published prefix are not modified; corrections ship as a new version. This release has 4,916 raw MCAP objects (43.22 TB); their destination keys, sizes and ETags are reconciled in `raw/RAW_OBJECTS.csv`.

## Downloader

`tools/download.py` is a Python 3 script that uses only the standard library. It reads `SHA256SUMS` from the release, downloads the selected files over HTTPS, checks each file against its SHA256 digest, and resumes an interrupted run when you repeat the same command. It never asks for or sends credentials. The general form is `python3 -B tools/download.py <BASE_URL> <dest> [--sums-sha256 HEX] [--include GLOB ...] [--exclude GLOB ...] [--raw] [--list] [--workers N] [--version v1.0.1]`, with `BASE_URL` and the destination folder before the options. `--sums-sha256` makes the tool refuse a `SHA256SUMS` whose SHA256 differs from the published digest. A file is selected when it matches at least one `--include` pattern (or no `--include` is given) and matches no `--exclude` pattern. Patterns are shell-style wildcards, and `*` also matches `/`; quote them so your shell does not expand them. `SHA256SUMS` and `MANIFEST.parquet` are always downloaded. `--list` prints the selection and its size without downloading. Raw MCAPs are downloaded only with `--raw`. The commands use `python3`; on Windows use `py -3`.

Before you have the release, set `BASE_URL` and `SUMS_SHA256` in your shell, fetch `SHA256SUMS` and the downloader itself, and check both before running anything. The bucket-root `README.md` gives both values; `SUMS_SHA256` is the SHA256 of `SHA256SUMS`, published outside the `v1.0.1/` prefix.

```sh
BASE_URL='<public base URL>'
SUMS_SHA256='<SHA256SUMS digest>'
mkdir -p tools
curl -fsSL -o SHA256SUMS "$BASE_URL/v1.0.1/SHA256SUMS"
curl -fsSL -o tools/download.py "$BASE_URL/v1.0.1/tools/download.py"
python3 - "$SUMS_SHA256" <<'PYCHECK'
import hashlib, sys
from pathlib import Path
sums = Path('SHA256SUMS').read_bytes()
if hashlib.sha256(sums).hexdigest() != sys.argv[1]: sys.exit('SHA256SUMS does not match the published digest')
want = next(line.split()[0] for line in sums.decode().splitlines() if line.endswith('  tools/download.py'))
if hashlib.sha256(Path('tools/download.py').read_bytes()).hexdigest() != want: sys.exit('tools/download.py does not match SHA256SUMS')
print('SHA256SUMS and tools/download.py verified')
PYCHECK
```

The commands below then write the release to `emg1-3ch-v1.0.1/`, and `--sums-sha256` checks the `SHA256SUMS` they fetch against the same digest. The downloaded tree contains its own checksummed `tools/download.py`; `cmp tools/download.py emg1-3ch-v1.0.1/tools/download.py` confirms that the copy you fetched first is the same file. Inside an existing release tree, run `python3 -B tools/download.py "$BASE_URL" . --sums-sha256 "$SUMS_SHA256" ...` to add files to it. Any HTTPS client can also fetch a single file from `<BASE_URL>/v1.0.1/<key>`; check it against its line in `SHA256SUMS`.

Starter contents: `starter/`, all `vendor/`, `index/*.csv` and `index/*.parquet`, `splits/`, `eval/`, `taxonomy/`, `loader/`, `tests/`, `tools/`, `baseline/`, `baselines/`, `cameras/`, `provenance/`, `raw/README.md`, `copy_manifest.csv`, `requirements*.txt`, `LICENSE`, `LICENSE-CODE`, root documentation, `raw/RAW_OBJECTS.csv` and `MANIFEST.parquet`, plus `SHA256SUMS`, which the downloader always fetches.

| Subset | Size from MANIFEST | Files |
| --- | ---: | ---: |
| Starter | 1.48 GB | 5,082 |
| Sensors | 231.46 GB | 4,916 |
| Derived sensor estimates | 64.59 GB | 4,916 |
| Training layer (without poses or frame tables) | 297.58 GB | 14,921 |
| Full extracted (without raw MCAPs) | 313.56 GB | 44,417 |
| Reconciled raw MCAPs | 43.22 TB | 4,916 |

### Starter download

```sh
python3 -B tools/download.py "$BASE_URL" emg1-3ch-v1.0.1 --sums-sha256 "$SUMS_SHA256" --include 'starter/*' 'vendor/*' 'index/*.csv' 'index/*.parquet' 'splits/*' 'eval/*' 'taxonomy/*' 'loader/*' 'tests/*' 'tools/*' 'baseline/*' 'baselines/*' 'cameras/*' 'provenance/*' 'raw/RAW_OBJECTS.csv' 'raw/README.md' 'copy_manifest.csv' 'LICENSE' 'LICENSE-CODE' 'MANIFEST.parquet' 'BUCKET_README.md' 'CHANGELOG.md' 'CITATION.cff' 'CLOCKS.md' 'CONTACT.md' 'DATASHEET.md' 'EVALUATION.md' 'GLOSSARY.md' 'KNOWN_ISSUES.md' 'POSES.md' 'QUALITY_TIERS.md' 'README.md' 'SCHEMA.json' 'SCHEMA.md' 'TASK_LABELS.md' 'TERMS.md' 'VALIDATION.json' 'croissant.json' 'requirements-core.txt' 'requirements-video.txt' 'requirements.txt' --exclude 'index/video_frames/*' '*.mcap'
```

### Training layer download

```sh
python3 -B tools/download.py "$BASE_URL" emg1-3ch-v1.0.1 --sums-sha256 "$SUMS_SHA256" --exclude 'derived/wrist_poses_est/*' 'index/video_frames/*' '*.mcap'
```

### Full extracted download

```sh
python3 -B tools/download.py "$BASE_URL" emg1-3ch-v1.0.1 --sums-sha256 "$SUMS_SHA256" --exclude '*.mcap'
```

### Raw MCAP download

```sh
python3 -B tools/download.py "$BASE_URL" emg1-3ch-v1.0.1 --sums-sha256 "$SUMS_SHA256" --raw --include 'raw/*.mcap'
```

With `--raw`, the downloader also fetches `raw/RAW_OBJECTS.csv` and downloads the raw objects it lists that match the patterns. It checks raw objects by size and ETag, because raw MCAPs are not listed in `SHA256SUMS`. A full raw download is 43.22 TB.

After downloading, run `cd emg1-3ch-v1.0.1` and `python3 -B tools/verify_download.py . --subset starter` for a starter tree. It verifies every required starter file and exits nonzero on a missing file, mismatch or wrong root. The starter has 5,082 files; verification prints `verified 5081 missing 0 mismatches 0` because `SHA256SUMS` does not hash itself. Use `python3 -B tools/verify_download.py .` for a partial or training-layer tree, and `--require-all` for the full extracted release. `SHA256SUMS` covers local release files; raw objects are reconciled by ETag in `raw/RAW_OBJECTS.csv`. Multipart ETags are not SHA256 digests.

To download one recording, look up its `clip_id` in `raw/RAW_OBJECTS.csv`. Inside a release tree that has the starter, run `python3 -B tools/download.py "$BASE_URL" . --sums-sha256 "$SUMS_SHA256" --raw --include 'raw/*/*/<clip_id>.mcap'`, then `python3 -B tools/verify_raw.py . <clip_id>` to check the file content against its listed ETag.
