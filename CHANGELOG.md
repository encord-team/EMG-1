# Changelog of this repository

Changes to the datasets themselves are in the releases' own changelogs: `docs/3ch-ego-v1.0.1/CHANGELOG.md` and
`docs/8ch-mocap-v1.0.1/CHANGELOG.md`.

## Unreleased: licensing clarifications

- Added `LICENSE-DATA` (CC BY 4.0), `NOTICE` and a License section in `README.md` stating which files of this
  repository are Apache-2.0 (code: `*.py`, `requirements*.txt`, plus `pyproject.toml`, `uv.lock` and
  `.python-version`) and which are CC BY 4.0 (everything else). `pyproject.toml` lists `LICENSE` and `NOTICE` as
  `license-files`. Copyright 2026 Encord.
- Encord owns all of EMG-1. The supplement `supplements/wd-fusion-predictions/v1/` was produced for Encord by
  Wearable Devices Ltd., is owned by Encord and is licensed CC BY 4.0; credit it as "EMG-1 fusion hand-pose
  predictions, Encord, 2026, CC BY 4.0". Its v1 `LICENSE` and `README.md`, which name Wearable Devices Ltd. as rights
  holder and give a Wearable Devices credit line, are superseded; to be corrected in supplement v2.
- The 8-channel v1.0.1 `LICENSE` says "Rights holder: Encord" without a copyright line; the intended notice is
  "Copyright 2026 Encord", as in the 3-channel `LICENSE`. To be corrected in v1.0.2.
- The copies under `docs/*-v1.0.1/` and `docs/8ch-mocap-supplement-wd-fusion-v1/` are left byte-identical to the
  bucket.

## 2026-10-20

- First version of the release repository, covering both EMG-1 datasets, each released 2026-10-20 as v1.0.1:
  the **3-channel dataset** (`3ch-ego`, factory textile work with egocentric video) and the **8-channel dataset**
  (`8ch-mocap`, free hand movement with OptiTrack markers and stereo video).
- `scripts/download.py DATASET SUBSET`: one-command subsets on top of each release's own verified downloader.
- `index/<dataset>/`: a committed snapshot of every object in each bucket (files, raw MCAPs, one row per clip or
  take) and `scripts/list_release.py DATASET` to query it or the live bucket.
- `docs/<dataset>-v1.0.1/`: each release's documentation, byte-identical to the bucket copies.
