# Using the EMG-1 datasets: download, browse, load

The two datasets live in two public Cloudflare R2 buckets, served over HTTPS with no account or key. Every
command in this repository names the dataset it talks to.

| Dataset id | Dataset | Bucket | Public base URL | Guide |
| --- | --- | --- | --- | --- |
| `3ch-ego` (alias `3ch`) | EMG-1 3-channel dataset v1.0.1 | `emg1-3ch-ego-release` | `https://pub-b29550bc5a1c44e08e91624ebf1cb243.r2.dev` | [docs/3ch-ego.md](docs/3ch-ego.md) |
| `8ch-mocap` (alias `8ch`) | EMG-1 8-channel dataset v1.0.1 | `emg1-8ch-mocap-release` | `https://pub-91c561c2860c47e9b776fa8dff99271e.r2.dev` | [docs/8ch-mocap.md](docs/8ch-mocap.md) |

Every object is at `<base URL>/v1.0.1/<key>`; the releases' own `README.md`, `BUCKET_README.md`, `SHA256SUMS`
and `MANIFEST.parquet` sit under that prefix. The buckets cannot be listed, which is what `index/` here is for.

## Quick start

```sh
git clone https://github.com/encord-team/EMG-1.git
cd EMG-1
python3 scripts/download.py 3ch-ego   starter     # 1.5 GB -> emg1-3ch-v1.0.1/
python3 scripts/download.py 8ch-mocap starter     # 1.3 GB -> emg1-8ch-v1.0.1/
```

Python 3.8 or newer, no packages. Each starter has a few complete recordings plus every index table, the
splits, the loader, the baselines and the documentation. Every file is checked against its published SHA-256
digest as it downloads, the release's verifier runs afterwards, and running the same command again resumes an
interrupted download.

Each release ships its own loader, quickstart and tests; its `README.md` explains them
([3ch-ego](docs/3ch-ego-v1.0.1/README.md), [8ch-mocap](docs/8ch-mocap-v1.0.1/README.md)).

## 3-channel dataset

Clips are identified like `20261005_egox-018_112656_888ded7e` (UTC date, station, UTC time, hash); they are
listed in [`index/3ch-ego/clips.csv`](index/3ch-ego/clips.csv).

| Subset | Size | Files | Command | What it is for |
| --- | ---: | ---: | --- | --- |
| Starter | 1.5 GB | 5,082 | `python3 scripts/download.py 3ch-ego starter` | 20 complete clips plus every index, split, taxonomy, loader, test, tool, baseline and document |
| Training layer | 297.6 GB | 14,921 | `python3 scripts/download.py 3ch-ego training` | All 4,916 clips: band sensors and estimated clocks, with the indexes. No video, poses or frame tables |
| Full extracted | 313.6 GB | 44,417 | `python3 scripts/download.py 3ch-ego full` | The training layer plus wrist-pose estimates and the per-clip video frame-time tables |
| One clip | 65 MB, +9 GB with `--raw` | | `python3 scripts/download.py 3ch-ego clip CLIP_ID [--raw]` | One clip's extracted files, and optionally its raw MCAP |
| Raw MCAPs | 43.22 TB | 4,916 | `python3 scripts/download.py 3ch-ego raw` | Every original recording: video, depth and all sensors. Download single clips instead unless you mean it |

Full details, file layout, loading code and caveats: [docs/3ch-ego.md](docs/3ch-ego.md).

## 8-channel dataset

Takes are identified like `OP-001/s003/02` (person / session / take); they are listed in
[`index/8ch-mocap/takes.csv`](index/8ch-mocap/takes.csv).

| Subset | Size | Files | Command | What it is for |
| --- | ---: | ---: | --- | --- |
| Starter | 1.3 GB | 147 | `python3 scripts/download.py 8ch-mocap starter` | 3 complete takes (HDF5, C3D, video) plus the index, splits, loader, eval, baselines, calibration and documents |
| Benchmark | 32.1 GB | 1,842 | `python3 scripts/download.py 8ch-mocap benchmark` | Every take's `take.h5` (tasks T1, T2) and `derived/` estimates (task T3). No video |
| Everything except video | 35.3 GB | 2,904 | `python3 scripts/download.py 8ch-mocap novideo` | The benchmark plus the C3D marker files, baselines, reference material and starter copies |
| Full | 217.3 GB | 3,827 | `python3 scripts/download.py 8ch-mocap full` | Everything, the 920 `take.mcap` video containers included |
| One take, session or person | ~20 MB per take, ~200 MB more with `--video` | | `python3 scripts/download.py 8ch-mocap take OP-001/s003/02 [--video]` | `take OP-001/s003` fetches a session, `take OP-001` a person |
| Predictions supplement | 195 MB | 401 | `python3 scripts/download.py 8ch-mocap supplement` | Wearable Devices' fusion hand-pose predictions for 391 takes, outside `v1.0.1/` (see below) |

Full details, file layout, loading code and caveats: [docs/8ch-mocap.md](docs/8ch-mocap.md).

### The Wearable Devices prediction supplement

`supplements/wd-fusion-predictions/v1/` in the 8-channel bucket holds frame-by-frame predictions of 20 left-hand
finger joint angles for 391 of the 920 takes, made by Wearable Devices from the EMG band and the ZED camera, with
one model per person trained on the other seven people and calibrated on two minutes of that person's own
motion-capture data. It is CC BY 4.0, sits outside the frozen `v1.0.1/` prefix, and has its own `SHA256SUMS`,
which the releases' own `tools/download.py` does not read. `python3 scripts/download.py 8ch-mocap supplement`
fetches and checks it (into `emg1-wd-fusion-v1/` beside the release folder, as its README expects). Read
[its README](docs/8ch-mocap-supplement-wd-fusion-v1/README.md) first: it explains what Encord changed in the
delivery, how to score the predictions against the release's markers, and why they are not comparable with
tasks T1 to T3.

## Options and your own selections

Any selection by glob (patterns match paths inside the release, `*` also matches `/`):

```sh
python3 scripts/download.py 3ch-ego custom --include 'vendor/*' 'index/*.parquet'
python3 scripts/download.py 8ch-mocap custom --include 'takes/OP-002/*/take.h5' 'derived/OP-002/*'
```

`--list` is a dry run that prints the selection, `--dest DIR` picks the folder, `--workers N` the parallelism,
`--no-verify` skips the verification pass. Put these before the first `--include` or `--exclude`; anything from
there on goes to the release's own `tools/download.py` unchanged (`--timeout`, `--retries`, `--quiet`).
`python3 scripts/download.py --help` prints everything. Sizes are decimal (GB = 10^9 bytes).

<details>
<summary>Without this repository</summary>

Any HTTPS client works:

```sh
curl -fLO https://pub-b29550bc5a1c44e08e91624ebf1cb243.r2.dev/v1.0.1/sensors/20261005_egox-018_112656_888ded7e.h5
curl -fLO https://pub-91c561c2860c47e9b776fa8dff99271e.r2.dev/v1.0.1/takes/OP-001/s003/02/take.h5
```

Check single files against their line in `index/<dataset>/files.csv` (or the release's `SHA256SUMS`). Each
release's own bootstrap, which verifies `SHA256SUMS` and the downloader before running anything, is in its
`BUCKET_README.md` ([3ch-ego](docs/3ch-ego-v1.0.1/BUCKET_README.md), [8ch-mocap](docs/8ch-mocap-v1.0.1/BUCKET_README.md)).
Note that both tell readers to take the base URL and digest from a bucket-root README; the base URLs are the
ones in the table at the top of this page, and the digests are below.
</details>

## Browse the buckets without downloading

`index/` holds a listing of each bucket, generated from the releases' own manifests:

| | `3ch-ego` | `8ch-mocap` |
| --- | --- | --- |
| The directory structure of the bucket | [`STRUCTURE.md`](index/3ch-ego/STRUCTURE.md) | [`STRUCTURE.md`](index/8ch-mocap/STRUCTURE.md) |
| Totals per folder, subset and grouping | [`SUMMARY.md`](index/3ch-ego/SUMMARY.md) | [`SUMMARY.md`](index/8ch-mocap/SUMMARY.md) |
| One row per recording, with its files and sizes | [`clips.csv`](index/3ch-ego/clips.csv) (4,916 clips) | [`takes.csv`](index/8ch-mocap/takes.csv) (920 takes) |
| Every file: key, bytes, sha256 | [`files.csv`](index/3ch-ego/files.csv) (44,416) | [`files.csv`](index/8ch-mocap/files.csv) (3,826) |
| Raw MCAPs: key, bytes, ETag | [`raw_objects.csv`](index/3ch-ego/raw_objects.csv) (4,916) | none (video is in `takes/*/take.mcap`) |
| Supplement files | none | [`supplement_files.csv`](index/8ch-mocap/supplement_files.csv) (401) |
| Version, base URL, digests, counts | [`RELEASE.json`](index/3ch-ego/RELEASE.json) | [`RELEASE.json`](index/8ch-mocap/RELEASE.json) |

`scripts/list_release.py` queries them (standard library only):

```sh
python3 scripts/list_release.py 3ch-ego --summary
python3 scripts/list_release.py 3ch-ego --clip 20261005_egox-018_112656_888ded7e     # all of one clip's objects, raw MCAP included
python3 scripts/list_release.py 8ch-mocap --take OP-005/s007                         # one session's objects
python3 scripts/list_release.py 8ch-mocap 'takes/*/take.h5' --urls > urls.txt       # then: aria2c -i urls.txt
python3 scripts/list_release.py 8ch-mocap --supplement 'supplements/*'               # the predictions supplement
python3 scripts/list_release.py DATASET --refresh --summary                          # read the live bucket instead
```

## Verifying what you downloaded

`scripts/download.py` checks every file against the release's `SHA256SUMS` as it downloads and runs the release's
verifier afterwards. To re-check a tree later:

```sh
python3 tools/3ch-ego/verify_download.py emg1-3ch-v1.0.1 --subset starter      # or no flag (partial), --require-all (full)
python3 tools/3ch-ego/verify_raw.py emg1-3ch-v1.0.1 CLIP_ID                    # one raw MCAP, by size and ETag
python3 tools/8ch-mocap/verify_download.py emg1-8ch-v1.0.1 --ignore-missing    # needs pyarrow; omit the flag for a full tree
cd emg1-wd-fusion-v1 && shasum -a 256 -c SHA256SUMS                            # the supplement
```

The identity of each release is the SHA-256 of its `SHA256SUMS`, recorded in `index/<dataset>/RELEASE.json`.
The downloader refuses a `SHA256SUMS` with any other digest.

```
3ch-ego    SHA256SUMS  724dc60071da364309cb69f7d62a3c608dd4310f6cb3570e66c9d1a86e282ed0   (also in the bucket-root README)
8ch-mocap  SHA256SUMS  f3b335e64fea3edd31da96b6fc577eb23591bd87150f21d30b10c57e7393f8a0
supplement SHA256SUMS  80394007f3ffa446f0b0b743784ce26865c94dab67e2b8cccf08e3522eb383dd
```

The files in `tools/` are the releases' own, byte-identical to the bucket copies (`tools/README.md` shows how to
check), and the copies in `docs/<dataset>-v1.0.1/` are the releases' documentation, checked the same way.

## Repository layout

```
README.md                  what EMG-1 is
USAGE.md                   this page
scripts/download.py        one-command subsets of either dataset, on top of the releases' own downloader
scripts/list_release.py    list, filter and size a bucket's contents, offline or live
scripts/build_index.py     regenerate index/<dataset>/ from a bucket's manifests (maintainers, needs pyarrow)
scripts/list_bucket.py     list a bucket completely through R2's S3 API (maintainers, needs an R2 token)
tools/<dataset>/           each release's own downloader and verifiers, byte-identical to the bucket copies
index/<dataset>/           the committed listing of each bucket
docs/<dataset>.md          the guide to each dataset; docs/<dataset>-v1.0.1/ holds the release documentation
docs/HOSTING.md            maintainers' notes on the buckets
```

Questions, errata, takedown and withdrawal requests about the data: support@encord.com, naming the dataset and
the clip IDs, take paths or object keys concerned. Problems with this repository: open a GitHub issue.
