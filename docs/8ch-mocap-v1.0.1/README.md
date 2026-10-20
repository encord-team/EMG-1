# EMG-1 8-channel dataset, v1.0.1

EMG-1 is a free and open dataset of synchronized left-hand surface EMG, band motion and pulse signals, optical motion capture, and external stereo video from free hand movement. It contains 920 takes from 12 people, totalling 15.036 hours of recording windows. The 8-channel EMG band is worn high on the forearm below the elbow (owner report); motion capture used 23 OptiTrack skin markers and video used a ZED 2i. The recordings were collected for Encord by a commercial data-collection vendor. The headline research task is EMG-based fingertip proximity detection. Wrist-frame finger pose and palm-aligned camera versus mocap comparison are reference tasks. Person codes are pseudonyms. Version 1.0.1 was released on 2026-10-20 and is maintained by Vineeth Velmurugan (Encord).

| Modality | Channels or content | Nominal rate | Units or frame |
|---|---|---:|---|
| EMG | 8 band channels | 2,000 Hz | normalized ADC counts; physical amplitude units not provided by the vendor |
| IMU | 3 acceleration and 3 gyroscope channels | 200 Hz | vendor raw units |
| PPG | 2 optical channels | 25 or 100 Hz by take | vendor raw units |
| Mocap | 20 finger and 3 wrist markers | 120 Hz | metres, observed room frame |
| Video | Stereo H.264, 1280 x 720 per eye | 60 Hz | external ZED 2i camera |

Manifest `fs_hz` measured sensor rates and per-take nominal PPG rates are in `index/aggregate_facts.json` and `index/takes_extra.parquet`. All 920 takes record the left hand. Native TAK and SVO2 files are not included in v1.0.1. No depth stream was recorded. Automatic estimates are not human annotations.

## Licence and attribution

EMG-1 is free and open under two licences, assigned by file type. All source code files, that is every `*.py` file and every requirements file such as `requirements.txt`, are licensed under the Apache License 2.0 (SPDX `Apache-2.0`); the full text is in `LICENSE-CODE`. Every other file in this release, including the recordings, derived estimates, index, splits, calibration files, metadata and documentation, is licensed under the Creative Commons Attribution 4.0 International licence (SPDX `CC-BY-4.0`); the full text is in `LICENSE`. When you share the data or publish work that uses it, credit it as "EMG-1 8-channel dataset, Vineeth Velmurugan, Encord, 2026, CC BY 4.0". `TERMS.md` summarises the terms and gives responsible-use guidance, which is not a licence restriction.

The `access` field in the `meta/summary` JSON of every `take.h5` file and in the `/meta` message of every `take.mcap` file was written during original packaging and predates the open release. `LICENSE` supersedes it: v1.0.1 is released under CC BY 4.0 (data) and Apache-2.0 (code). `KNOWN_ISSUES.md` quotes the stale value.

## Getting the data

The release is free to download over HTTPS from a publicly readable bucket, with no account or credentials. This tree does not record the download address. The bucket-root README, which sits outside the checksummed `v1.0.1/` prefix, gives the base URL and the SHA-256 digest of `SHA256SUMS`. Replace `<BASE_URL>` below with that base URL and `<SHA256SUMS_DIGEST>` with the digest it lists, without the version prefix or a trailing slash; `tools/download.py` adds `v1.0.1/` itself. Patterns are shell-style wildcards matched against paths inside the release, such as `takes/OP-001/s003/02/take.h5`, and `*` also matches `/`. `SHA256SUMS` and `MANIFEST.parquet` are always downloaded, and every file is checked against `SHA256SUMS`.

**First download.** Start in a new, empty parent directory, not inside an existing release folder. Fetch `SHA256SUMS` and `tools/download.py` on their own over HTTPS, check them, run the tool once to create the release folder `emg1-8ch-v1.0.1`, then change into it:

```bash
mkdir emg1 && cd emg1
curl -fsSL -o SHA256SUMS "<BASE_URL>/v1.0.1/SHA256SUMS"
curl -fsSL --create-dirs -o tools/download.py "<BASE_URL>/v1.0.1/tools/download.py"
sha256sum SHA256SUMS                                     # must equal the digest in the bucket-root README
grep '  tools/download.py$' SHA256SUMS | sha256sum -c -  # must print: tools/download.py: OK
python -B tools/download.py <BASE_URL> ./emg1-8ch-v1.0.1 --sums-sha256 <SHA256SUMS_DIGEST> --exclude 'takes/*' --exclude 'derived/*'
cd emg1-8ch-v1.0.1
```

That run fetches the documents, checksums, `index/`, `splits/`, `starter/`, `loader/`, `tools/`, `eval/`, `baselines/`, `reference/` and `calibration/`. The release folder has its own `SHA256SUMS` and `tools/download.py`, so the two bootstrap files in the parent directory can be deleted. On macOS, use `shasum -a 256` in place of `sha256sum`.

**More data.** From inside the release folder, use its own copy of the tool with `.` as the destination:

```bash
# Benchmark data: take HDF5 for T1 and T2, derived estimates for T3
python -B tools/download.py <BASE_URL> . --include 'takes/*/take.h5' --include 'derived/*'
# Everything except video
python -B tools/download.py <BASE_URL> . --exclude '*.mcap'
```

Each command adds files to the same folder, and an interrupted command resumes when run again. Put `<BASE_URL>` and the destination before the options. Add `--list` to preview a selection, and `--sums-sha256` with the `SHA256SUMS` digest from the bucket-root README to make the tool stop if the checksum file differs. Download `take.mcap` files only when you need video. `BUCKET_README.md` describes the subsets and partial-download verification.

| Task | Additional files | Approximate size |
|---|---|---:|
| T1/T2 | `takes/*/take.h5` | 27.24 GB |
| T3 | `derived/*` | 4.81 GB |
| Video | `takes/*/take.mcap` | 181.51 GB |

Test labels are included in the release. The default split retains existing partitions and assigns new people to train. Person-disjoint evaluation uses 12 leave-one-person-out folds.

## Five-line quickstart

```bash
python -m venv ../emg1-venv && . ../emg1-venv/bin/activate
pip install -r requirements.txt
python -B loader/quickstart.py . --starter
python -B loader/tests.py .
python -B tools/verify_download.py . --ignore-missing
```

The starter has no derived estimate files, so T3 cannot be previewed. Tested Python version: 3.12. `python -B loader/quickstart.py . --starter --task T1` previews the contact feature and label path. The quickstart returns a wrist-frame marker batch with masks and computes a masked loss. `loader/README.md` describes alignment, caching and full-tree use. HDF5 requires h5py >= 3.0 / HDF5 >= 1.10. The marker frame, automatic contact proxy and quality rules are defined in `MARKERS.md`, `eval/TASKS.md` and `QUALITY_TIERS.md`. The 79 main index columns and their counts are in `INDEX_DICTIONARY.md`.

## Evaluation and citation

T1 predicts any-digit `contact_est` from EMG and reports AUROC and average precision (AP), alongside prevalence, with equal weight per held-out person. T2 predicts 20 finger markers in a wrist frame and includes the mean-pose reference in every table. T3 compares camera estimates with mocap on whatever takes have estimates at evaluation time; run `python -B tools/metadata.py . --coverage-only` to report current coverage from shipped files. `eval/TASKS.md` and `baselines/README.md` give the exact protocol and one-command reproduction.

Cite the dataset with `CITATION.cff` (Vineeth Velmurugan, Encord, version 1.0.1, released 2026-10-20). It has no DOI yet; a DOI may be added later. See `CHANGELOG.md` for changes in this version, `DATASHEET.md` for collection and use, and `KNOWN_ISSUES.md` for limitations.

## Recording details

Recording windows comprise 52 takes near 30 s, 866 takes near 60 s, 1 take near 70 s, 1 take near 319 s. The longest take is OP-001/s019/13 at 319.300 s. The minimum tier count/span EMG rate is 374.6 Hz. See `selection_waterfall.json`, `clock_epochs.json`, `MANIFEST.parquet`, and `croissant.json` for selection, clocks, hashes, and field metadata. Video is in the `/video` MCAP channel of `take.mcap` as raw Annex-B H.264 access units. The pinned requirements do not include an MCAP reader.

## Contact

Send questions, errata, takedown and withdrawal requests to support@encord.com (`CONTACT.md`). Fixes ship as new versions with a `CHANGELOG.md` entry.
