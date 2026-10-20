# EMG-1 3-channel dataset (`3ch-ego`)

**3-channel wrist EMG, IMU and PPG from both wrists with egocentric video, recorded during real textile work in a factory.**

Mudra Pro bands on both wrists, a head-mounted ZED X Mini stereo camera with neural depth, one ZED X One camera
per wrist, automatic wrist-pose estimates and weak task labels. Collected for Encord by a commercial
data-collection vendor; released free and open as **v1.0.1** on 2026-10-20.

| | |
| --- | --- |
| Recordings | 4,916 clips of about 5 minutes, 397.4 clip-hours with EMG, from 7 stations over 136 sessions and 68 station-days |
| Usable time | 271.8 h of both-wrist GOLD or STANDARD quality segments |
| Per wrist | EMG 3 channels at 2133 Hz, 24-bit; IMU 6 axes at 800 Hz; PPG 2 channels at 100 Hz |
| Cameras | Head stereo + neural depth and two wrist cameras, 1920 x 1200 at 30 fps, inside the raw MCAPs |
| Labels | Vendor task segments in 8 keyword categories (unverified); automatic wrist-cap poses (sparse); frozen quality tiers |
| Size | Extracted release 313.6 GB in 44,416 files; raw MCAP recordings 43.22 TB in 4,916 objects |
| Bucket | `emg1-3ch-ego-release`, base URL `https://pub-b29550bc5a1c44e08e91624ebf1cb243.r2.dev` |
| Release docs | [`docs/3ch-ego-v1.0.1/`](3ch-ego-v1.0.1/) (byte-identical to the bucket copies) |

## Download

```sh
python3 scripts/download.py 3ch-ego starter        # 1.5 GB -> emg1-3ch-v1.0.1/
```

| Subset | Size | Files | Command | What it is for |
| --- | ---: | ---: | --- | --- |
| Starter | 1.5 GB | 5,082 | `python3 scripts/download.py 3ch-ego starter` | 20 complete clips plus every index, split, taxonomy, loader, test, tool, baseline and document. A first look, the loader, the docs. |
| Training layer | 297.6 GB | 14,921 | `python3 scripts/download.py 3ch-ego training` | All 4,916 clips: band sensors and estimated clocks, with the indexes. EMG research without video or poses. |
| Full extracted | 313.6 GB | 44,417 | `python3 scripts/download.py 3ch-ego full` | The training layer plus wrist-pose estimates and the per-clip video frame-time tables. |
| One clip | 65 MB, +9 GB with `--raw` | | `python3 scripts/download.py 3ch-ego clip CLIP_ID [--raw]` | Add one clip's extracted files, and optionally its raw MCAP, to a tree. |
| Raw MCAPs | 43.22 TB | 4,916 | `python3 scripts/download.py 3ch-ego raw` | Every original recording: video, depth and all sensors. Download single clips instead unless you mean it. |

Clip IDs are listed in [`index/3ch-ego/clips.csv`](../index/3ch-ego/clips.csv). The release ships its own
PyTorch loader, quickstart and tests; see its [README](3ch-ego-v1.0.1/README.md) and [loader notes](3ch-ego-v1.0.1/loader/README.md).
Video frames sit inside the raw MCAPs; the loader's `video_frame_at` needs a protobuf decoder factory
(`mcap-protobuf-support`) because the video channels are protobuf-encoded.

## What is in the release

```
v1.0.1/
├── README.md  DATASHEET.md  SCHEMA.md  QUALITY_TIERS.md  CLOCKS.md  POSES.md  TASK_LABELS.md
│   KNOWN_ISSUES.md  EVALUATION.md  GLOSSARY.md  TERMS.md  CONTACT.md  CHANGELOG.md  CITATION.cff
├── LICENSE (CC BY 4.0)  LICENSE-CODE (Apache-2.0)  SHA256SUMS  MANIFEST.parquet  croissant.json
├── sensors/<clip_id>.h5                       band observations per wrist (EMG, IMU, PPG), head IMU, odometry   4,916 x ~50 MB
├── derived/sensors_est/<clip_id>_est.h5       estimated host-clock timestamps, quality windows, tag detections   4,916 x ~13 MB
├── derived/wrist_poses_est/<clip_id>_est.h5   automatic wrist-cap pose estimates                                 4,916 x ~3 MB
├── derived/quality/                           the frozen tier and segment rules and their outputs
├── vendor/<clip_id>.json                      vendor task segments: titles, descriptions, session-relative ms
├── vendor/segments.parquet  titles.csv        the same, tabulated and mapped to 8 categories
├── index/clips.{csv,parquet}                  one row per clip: station, date, split, tiers, flags, paths, hours
├── index/segments.{csv,parquet}               quality segments: clip, wrist scope, interval, tier
├── index/video_streams.{csv,parquet}          which frame-time tables exist per clip
├── index/video_frames/<clip_id>/*.parquet     frame-time tables for head_left, head_right, depth, wrist_left, wrist_right
├── splits/                                    the primary station-day split and train-only normalisation
├── eval/                                      station_held_out and cross_task splits, the scorer
├── taxonomy/                                  keyword rules mapping vendor titles to task categories
├── loader/emg1_ego/                           PyTorch/NumPy loader: EMGWindowDataset, ClipReader, video_frame_at
├── baselines/  baseline/                      reference window-level benchmark; historical clip probe
├── starter/                                   20 complete clips (sensors + derived) for a first look
├── cameras/  provenance/  tests/  tools/      camera specs, methods, unit tests, release and download tools
└── raw/<station>/<date>/<clip_id>.mcap        original recordings: video, depth, every sensor   4,916 x ~9 GB
```

A clip ID such as `20261005_egox-018_112656_888ded7e` is the UTC date, the station (a recording kit, not a
person), the UTC time and a hash. Raw MCAPs are not in `SHA256SUMS`; they are reconciled by size and ETag in
`raw/RAW_OBJECTS.csv`, and the downloader fetches them only with `--raw`.

## Read this before you train

- **Task labels are weak.** Titles and segments come from the collection vendor, mapped to 8 categories by a
  keyword rule, with no human review. Use `label_valid`, reduced class sets and per-class support floors.
  [TASK_LABELS](3ch-ego-v1.0.1/TASK_LABELS.md)
- **Wrist poses are automatic and sparse.** They are optical tag-cap estimates at nominal scale, not anatomical
  ground truth; valid runs are fragmented. Respect `pose_valid`. [POSES](3ch-ego-v1.0.1/POSES.md)
- **Use the quality tiers.** GOLD needs ordinary filtering; STANDARD needs a saturation mask and mains notch;
  EXTENDED and NONE need expert handling. Segments are the authority, not the clip tier.
  [QUALITY_TIERS](3ch-ego-v1.0.1/QUALITY_TIERS.md)
- **Splits group station-days, not people.** Workers may appear in several partitions. Bootstrap over
  station-days. The station-held-out test station has a failing left band. [EVALUATION](3ch-ego-v1.0.1/EVALUATION.md)
- **Clocks are estimates.** `t_ns_est` aligns band samples to the recorder host; nothing certifies camera exposure
  time. [CLOCKS](3ch-ego-v1.0.1/CLOCKS.md)
- **Video is not anonymised** and may show people at work. Do not try to identify anyone. [TERMS](3ch-ego-v1.0.1/TERMS.md)

All of it: [README](3ch-ego-v1.0.1/README.md), [DATASHEET](3ch-ego-v1.0.1/DATASHEET.md),
[KNOWN_ISSUES](3ch-ego-v1.0.1/KNOWN_ISSUES.md), [SCHEMA](3ch-ego-v1.0.1/SCHEMA.md) (every field),
[GLOSSARY](3ch-ego-v1.0.1/GLOSSARY.md), [loader](3ch-ego-v1.0.1/loader/README.md), [raw MCAPs](3ch-ego-v1.0.1/raw/README.md),
[baselines](3ch-ego-v1.0.1/baselines/README.md), [CHANGELOG](3ch-ego-v1.0.1/CHANGELOG.md).

## Verifying

```sh
python3 tools/3ch-ego/verify_download.py emg1-3ch-v1.0.1 --subset starter    # a starter tree
python3 tools/3ch-ego/verify_download.py emg1-3ch-v1.0.1                     # a partial tree
python3 tools/3ch-ego/verify_download.py emg1-3ch-v1.0.1 --require-all       # the full extracted release
python3 tools/3ch-ego/verify_raw.py emg1-3ch-v1.0.1 CLIP_ID                  # one raw MCAP, by size and ETag
```

Published digests: `SHA256SUMS` `724dc60071da364309cb69f7d62a3c608dd4310f6cb3570e66c9d1a86e282ed0`,
`MANIFEST.parquet` `80e22ed9e76ff9a8c15204fa597f9be0a5f12cd442dfdbf53f8cbef45cf507a0` (also in the bucket-root README).

## Licence and citation

Data CC BY 4.0, code Apache-2.0: [LICENSE](3ch-ego-v1.0.1/LICENSE), [LICENSE-CODE](3ch-ego-v1.0.1/LICENSE-CODE),
[TERMS](3ch-ego-v1.0.1/TERMS.md). Credit: "EMG-1 3-channel dataset, Vineeth Velmurugan, Encord, 2026, CC BY 4.0".
Cite with [CITATION.cff](3ch-ego-v1.0.1/CITATION.cff). Contact: support@encord.com ([CONTACT](3ch-ego-v1.0.1/CONTACT.md)).
