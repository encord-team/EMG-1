# Changelog of this repository

Changes to the datasets themselves are in the releases' own changelogs: `docs/3ch-ego-v1.0.1/CHANGELOG.md` and
`docs/8ch-mocap-v1.0.1/CHANGELOG.md`.

## 2026-10-20

- First version of the release repository, covering both EMG-1 datasets, each released 2026-10-20 as v1.0.1:
  the **3-channel dataset** (`3ch-ego`, factory textile work with egocentric video) and the **8-channel dataset**
  (`8ch-mocap`, free hand movement with OptiTrack markers and stereo video).
- `scripts/download.py DATASET SUBSET`: one-command subsets on top of each release's own verified downloader.
- `index/<dataset>/`: a committed snapshot of every object in each bucket (files, raw MCAPs, one row per clip or
  take) and `scripts/list_release.py DATASET` to query it or the live bucket.
- `docs/<dataset>-v1.0.1/`: each release's documentation, byte-identical to the bucket copies.
