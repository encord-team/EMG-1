# EMG-1 8-channel dataset (`8ch-mocap`)

**8-channel forearm EMG, IMU and PPG with a dense OptiTrack hand markerset and external stereo video, recorded during free left-hand movement.**

One 8-channel Mudra band worn high on the left forearm, 23 OptiTrack skin markers (20 on the fingers, 3 on the
wrist) at 120 Hz, a ZED 2i stereo camera at 60 fps, and automatic estimates: band-to-mocap lag, a fingertip
proximity proxy and MediaPipe stereo hand keypoints. Collected for Encord by a commercial data-collection vendor;
released free and open as **v1.0.1** on 2026-10-20.

| | |
| --- | --- |
| Recordings | 920 takes from 12 people (pseudonyms `OP-001` to `OP-012`) over 74 sessions, 15.0 hours of recording windows; takes of 30 s or 60 s, each opening on a 5 s rest in a known forearm posture, then unscripted movement |
| Band | EMG 8 channels at 2000 Hz (normalised ADC counts); IMU 6 axes at 200 Hz; PPG 2 channels at 25 or 100 Hz |
| Mocap | 23 markers in metres, canonical order `T1..T4 I1..I4 M1..M4 R1..R4 P1..P4 WR RAD ULN`, with validity masks |
| Video | External ZED 2i stereo, H.264 at 1280 x 720 per eye, 60 fps, one MCAP per take; no depth stream |
| Labels | `contact_est` per digit (within 20 mm of the thumb tip = 1, beyond 30 mm = 0, unknown between), from the markers; no human annotations |
| Quality | `EMG_TIER` 775 GOLD / 137 STANDARD / 8 EXTENDED; `MULTIMODAL_TIER` 346 / 526 / 48 |
| Size | 217.3 GB in 3,826 files, of which 182 GB is video |
| Bucket | `emg1-8ch-mocap-release`, base URL `https://pub-91c561c2860c47e9b776fa8dff99271e.r2.dev` |
| Release docs | [`docs/8ch-mocap-v1.0.1/`](8ch-mocap-v1.0.1/) (byte-identical to the bucket copies) |

## Download

```sh
python3 scripts/download.py 8ch-mocap starter        # 1.3 GB -> emg1-8ch-v1.0.1/
```

| Subset | Size | Files | Command | What it is for |
| --- | ---: | ---: | --- | --- |
| Starter | 1.3 GB | 147 | `python3 scripts/download.py 8ch-mocap starter` | 3 complete takes (HDF5, C3D, video) plus the index, splits, loader, eval, baselines, calibration and documents. |
| Benchmark | 32.1 GB | 1,842 | `python3 scripts/download.py 8ch-mocap benchmark` | Every take's `take.h5` (tasks T1 and T2) and `derived/` estimates (task T3). No video. |
| Everything except video | 35.3 GB | 2,904 | `python3 scripts/download.py 8ch-mocap novideo` | The benchmark plus the C3D marker files, baselines, reference material and the starter copies. |
| Full | 217.3 GB | 3,827 | `python3 scripts/download.py 8ch-mocap full` | Everything, the 920 `take.mcap` video containers included. |
| One take, session or person | ~20 MB per take, ~200 MB more with `--video` | | `python3 scripts/download.py 8ch-mocap take OP-001/s003/02 [--video]` | `take OP-001/s003` fetches a session, `take OP-001` a person. |
| Predictions supplement | 195 MB | 401 | `python3 scripts/download.py 8ch-mocap supplement` | Wearable Devices' fusion hand-pose predictions for 391 takes, outside `v1.0.1/` ([below](#the-wearable-devices-prediction-supplement)). |

Take paths are listed in [`index/8ch-mocap/takes.csv`](../index/8ch-mocap/takes.csv). The release ships its own
PyTorch loader, quickstart and tests; see its [README](8ch-mocap-v1.0.1/README.md) and [loader notes](8ch-mocap-v1.0.1/loader/README.md).

## What is in the release

```
v1.0.1/
├── README.md  DATASHEET.md  SCHEMA.md  MARKERS.md  INDEX_DICTIONARY.md  QUALITY_TIERS.md  KNOWN_ISSUES.md
│   GLOSSARY.md  TERMS.md  CONTACT.md  CHANGELOG.md  CITATION.cff  BUCKET_README.md
├── LICENSE (CC BY 4.0)  LICENSE-CODE (Apache-2.0)  SHA256SUMS  MANIFEST.parquet  croissant.json  requirements.txt
├── hours.json  thresholds.json  clock_epochs.json  selection_waterfall.json  BUILD_PROVENANCE.json  VALIDATION.json
├── takes/OP-xxx/sNNN/TT/take.h5         EMG, IMU, PPG, markers (observed, repaired, canonical), proximity proxy, lag,
│                                        gaps, embedded vendor records                                    920 x ~33 MB
├── takes/OP-xxx/sNNN/TT/take.c3d        the markers as C3D                                               920 x ~2.7 MB
├── takes/OP-xxx/sNNN/TT/take.mcap       stereo video (raw Annex-B H.264 in the /video channel)          920 x ~200 MB
├── derived/OP-xxx/sNNN/TT/automatic_est.h5   MediaPipe stereo hand keypoints, timing, gaps, proximity   920 x ~5 MB
├── index/takes.{csv,parquet}            one row per take: 79 columns of tiers, flags, lag, clocks (INDEX_DICTIONARY.md)
├── index/takes_extra.{csv,parquet}      scenario version, rest phase and posture, nominal rates
├── splits/                              default_smoke split, 12 leave-one-person-out folds, train-only normalisation
├── eval/                                TASKS.md, scorer, probe targets, vision scorer
├── loader/                              EMGDataset, TakeReader, quickstart.py, tests.py
├── baselines/                           frozen LOSO baselines (T1_metrics.json, T2_metrics.json, per-fold results)
├── calibration/OP-xxx_Left.motive       the per-person OptiTrack marker-set calibration
├── reference/                           the T1 probe's extraction and model scripts and logs
├── starter/                             3 complete takes plus starter/takes.json
└── tools/                               download.py, verify_download.py, index and metadata tools
```

A take path `OP-001/s003/02` is person / session / take number. Every take records the left hand. Native
OptiTrack TAK and ZED SVO2 files are not included.

## The Wearable Devices prediction supplement

`supplements/wd-fusion-predictions/v1/` in the same bucket, outside the frozen `v1.0.1/` prefix, holds
frame-by-frame predictions of 20 left-hand finger joint angles for 391 of the 920 takes (people OP-001 to
OP-008). Wearable Devices made them by fusing the EMG band with the ZED camera, one model per person trained
on the other seven and calibrated on about two minutes of that person's own motion-capture data; Encord moved
the time stamps onto the release clock and removed takes that are not in v1.0.1. It is CC BY 4.0 with its own
`SHA256SUMS` (digest `80394007f3ffa446f0b0b743784ce26865c94dab67e2b8cccf08e3522eb383dd`), which the release's
`tools/download.py` does not read, so this repository fetches it itself:

```sh
python3 scripts/download.py 8ch-mocap supplement      # 401 files, 195 MB -> emg1-wd-fusion-v1/
python3 scripts/list_release.py 8ch-mocap --supplement 'supplements/*/predictions/OP-002*'
```

Read [its README](8ch-mocap-supplement-wd-fusion-v1/README.md) before using it: it explains the changes to the
delivery, how to score the predictions against `markers/canonical`, the errata to the vendor's guide, and why
the numbers are not comparable with tasks T1 to T3. Its files are listed in
[`index/8ch-mocap/supplement_files.csv`](../index/8ch-mocap/supplement_files.csv).

## Read this before you train

- **No human labels.** `contact_est` is a skin-marker proximity proxy (thumb tip to fingertip), not physical
  touch; MediaPipe estimates are automatic and not bit-reproducible. [TASKS](8ch-mocap-v1.0.1/eval/TASKS.md)
- **Read the markers through their masks.** Canonical markers can be swapped or masked by automatic identity
  checks; `canonical_aliases` is in vendor order and must not be zipped with `canonical_labels`.
  [MARKERS](8ch-mocap-v1.0.1/MARKERS.md)
- **Lag is an estimate.** The band-to-mocap lag is measured on 863 of 920 takes and applied only then; it is a
  band-IMU timing estimate, not EMG latency. Band IMU sentinel values (-4, -500) are masked by `accel_valid` and
  `gyro_valid`.
- **Evaluate person-disjoint.** The official protocol is 12 leave-one-person-out folds with equal weight per
  person; `default_smoke` is only a loader convenience. Test labels are in the release.
- **Units and placement are unknown.** EMG amplitude units, electrode type, placement and channel order were not
  provided by the vendor; the band sits high on the forearm (owner report).
- **The take files still say "controlled access".** The `access` field inside `take.h5` and `take.mcap` predates
  the open release and is superseded by `LICENSE`. [KNOWN_ISSUES](8ch-mocap-v1.0.1/KNOWN_ISSUES.md)
- **Video is not anonymised** and faces are not blurred. Do not try to identify anyone. [TERMS](8ch-mocap-v1.0.1/TERMS.md)

All of it: [README](8ch-mocap-v1.0.1/README.md), [DATASHEET](8ch-mocap-v1.0.1/DATASHEET.md),
[SCHEMA](8ch-mocap-v1.0.1/SCHEMA.md), [INDEX_DICTIONARY](8ch-mocap-v1.0.1/INDEX_DICTIONARY.md),
[QUALITY_TIERS](8ch-mocap-v1.0.1/QUALITY_TIERS.md), [GLOSSARY](8ch-mocap-v1.0.1/GLOSSARY.md),
[loader](8ch-mocap-v1.0.1/loader/README.md), [baselines](8ch-mocap-v1.0.1/baselines/README.md),
[CHANGELOG](8ch-mocap-v1.0.1/CHANGELOG.md).

## Verifying

```sh
python3 tools/8ch-mocap/verify_download.py emg1-8ch-v1.0.1 --ignore-missing   # a partial tree (needs pyarrow)
python3 tools/8ch-mocap/verify_download.py emg1-8ch-v1.0.1                    # the full release
cd emg1-8ch-v1.0.1 && shasum -a 256 -c --ignore-missing SHA256SUMS            # the no-dependency alternative
cd emg1-wd-fusion-v1 && shasum -a 256 -c SHA256SUMS                           # the supplement
```

Digests: `SHA256SUMS` `f3b335e64fea3edd31da96b6fc577eb23591bd87150f21d30b10c57e7393f8a0`,
`MANIFEST.parquet` `4e966de81a62a30cbd9907fb9ae7ca5b3e1694c1ae783297b6a0a74b04868ca7`, as observed in the bucket
on 2026-10-20 and recorded in [`index/8ch-mocap/RELEASE.json`](../index/8ch-mocap/RELEASE.json).

## Licence and citation

Data CC BY 4.0, code Apache-2.0: [LICENSE](8ch-mocap-v1.0.1/LICENSE), [LICENSE-CODE](8ch-mocap-v1.0.1/LICENSE-CODE),
[TERMS](8ch-mocap-v1.0.1/TERMS.md). Credit: "EMG-1 8-channel dataset, Vineeth Velmurugan, Encord, 2026, CC BY 4.0".
Cite with [CITATION.cff](8ch-mocap-v1.0.1/CITATION.cff). Contact: support@encord.com ([CONTACT](8ch-mocap-v1.0.1/CONTACT.md)).
