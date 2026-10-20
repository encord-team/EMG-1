# EMG-1 3-channel dataset v1.0.1

This release records Mudra Pro wrist-band muscle, inertial and pulse signals during textile work in a factory, alongside head and wrist cameras. The recordings were collected for Encord by a commercial data-collection vendor. It has 4,916 clips, 397.428 clip-hours with EMG and 271.779 hours of both-wrist GOLD or STANDARD quality segments. The original compressed video and depth are in raw MCAP objects. Task descriptions are unverified vendor annotations; wrist poses and sensor clock alignment are automatic estimates. The data can support EMG task-recognition and multimodal-alignment research when those limitations are measured.

## Getting the data

The release is free and open: no account, access key or agreement is needed. Download it over public HTTPS with `tools/download.py`, which checks every file against `SHA256SUMS`. The public base URL is given in the bucket-root `README.md`, outside the `v1.0.1/` prefix; pass it to the downloader as `BASE_URL`. If you do not have the release yet, that README also shows how to fetch `tools/download.py` itself. `BUCKET_README.md` lists the subset commands, sizes and verification steps. Raw MCAP recordings are downloaded only when you add `--raw`.

The starter download contains `starter/`, all `vendor/`, `index/*.csv` and `index/*.parquet`, `splits/`, `eval/`, `taxonomy/`, `loader/`, `tests/`, `tools/`, `baseline/`, `baselines/`, `cameras/`, `provenance/`, `raw/README.md`, `copy_manifest.csv`, `requirements*.txt`, `LICENSE`, `LICENSE-CODE`, root documentation, `raw/RAW_OBJECTS.csv` and `MANIFEST.parquet`, plus `SHA256SUMS`, which the downloader always fetches.

## Quickstart

Requires Python 3.12 or 3.13; macOS arm64 prebuilt wheels require macOS 14 or newer.

```sh
python3 -B tools/verify_download.py . --subset starter
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -B loader/example.py . --starter
python -B -m unittest discover -s tests
```

The example yields an EMG batch and vendor-derived labels. The starter is illustrative, not an evaluation partition. Omit `--starter` for the full tree. For partial trees, `available_only=True` drops missing-file windows and prints their count. Use PyTorch `num_workers` for parallel reading and call `dataset.close()` when finished.

## Modalities

| Layer | Rate and shape | Units and order | Notes |
| --- | --- | --- | --- |
| Band EMG | 3 channels per wrist, nominal 2133 Hz, 24-bit | Vendor amplitude units | Amplitude scaling to physical units and electrode type and placement were not provided by the vendor. The 200 Hz recorder configuration affects 184 clips and is excluded by quality tiers. |
| Band IMU | nominal 800 Hz, 6 axes | acceleration x/y/z in g, then angular velocity x/y/z in degrees/s | `imu_h` in sensor HDF5. |
| Band PPG | nominal 100 Hz, 2 channels | microvolts | Pulse waveform, not a clinical measurement. |
| Camera IMUs | about 200 Hz | angular velocity first in rad/s, acceleration in m/s² | Different order and units from band IMU. |
| Odometry | about 30 Hz | estimated transform | Not anatomical hand ground truth. |
| Head cameras | 1920x1200, 30 frames/s | ZED X Mini stereo, rectified left, neural stereo depth | Observed head baseline range 0.04977 to 0.04989 m in L1 `tf_static` and `mcap_metadata`; inspect each clip. |
| Wrist cameras | 1920x1200, 30 frames/s | ZED X One GS, one per wrist | No head-to-wrist extrinsic ships. |

Band firmware is recorded per wrist in the clip index; version 2.0.2.2 appears on 4,915 left and 4,916 right records. The extracted HDF5 stores `head_left_camera_info`; other camera_info topics remain in the raw MCAPs. Video and depth are compressed MCAP streams, not pixels in sensor HDF5. Raw MCAPs retain recorder metadata, including station hostnames and account-like recording strings, some in email format. These strings are stand-in values, not personal contact details. The L1 sensor and derived files have account fields removed. Raw destination count, sizes and ETags are reconciled in `raw/RAW_OBJECTS.csv`.

## Tasks and splits

The primary split groups entire station-days. It has 191.070/40.347/40.362 quality-filtered both-wrist hours in train/val/test. A station is a recording kit, not a person. Workers may cross partitions. Bootstrap over station-days. `EMGWindowDataset(root, split_name='primary', partition='train')` selects it explicitly.

The `station_held_out` split tests on egox-017, whose left band is degraded in 676 affected clips; its 13.515 quality-filtered both-wrist hours are within 54.924 clip-hours. Its validation station egox-013 has head-camera stamp slips; the flag also occurs on all 752 egox-005 clips. Per-wrist results use the same canonical both-wrist windows, with only that wrist's features. The literal partition keys are `train`, `val`, and `test`. `cross_task` is experimental, with no official metric. Passing clip IDs that conflict with a partition raises an error; set `split=None` for an explicit clip list.

Vendor segment timestamps count from the session start, not the clip. Of 4,916 clips, 4,785 begin after session start. After sidecar-anchor subtraction, 10,401 vendor segments fit within their clip using an inclusive-end allowance of 1 ms (`tools/check_vendor_segments.py`). 1,196 segments end 1 ms past `data.end_ts`; the maximum end over indexed `duration_s` is 34 ms. `vendor_segments(clip_id, clock='clip')` returns clip-relative milliseconds; `clock='host_est'` uses an estimated host anchor. `label='vendor_segment'` returns a weak category and validity mask with a 3 s boundary margin. How the vendor produced task titles was not provided by the vendor. Task categories come from the vendor titles, mapped by the frozen keyword taxonomy; unmatched titles map to `other`. See `TASK_LABELS.md`.

## Quality and clocks

`GOLD` accepts ordinary EMG filtering. `STANDARD` can need a saturation mask around `|v| >= 0.99` (250 ms each side) and a 50 Hz comb plus 45-55 Hz band-stop for mains contamination. `EXTENDED` needs expert handling of electrodes, contact gaps or clock faults. `NONE` is unsuitable for ordinary EMG analysis. The clip tier is the worse wrist tier; segment tiers can preserve usable time inside lower-tier clips. `dropouts` is present on 4,817 clips and is not a useful blanket exclusion filter. See `QUALITY_TIERS.md` and `SCHEMA.md`.

`t_host_ns` is recorder host time, `t_dev` a device tick, `t_ns_est` an estimated alignment, and `qc_t_ns_est` the frozen quality clock. MCAP `log_time` is used for video lookup; image header stamps can slip. Estimated host time does not certify exposure synchronization. `CLOCKS.md` lists the clock fields and frozen tier bounds. Automatic wrist poses are optical cap estimates at nominal scale. Their validity is sparse; inspect `pose_valid`. The example defaults to `pose_targets=False`. Coverage by tier and split is in `POSES.md`.

## Licence, citation and use

The data are licensed under CC BY 4.0 and the source code (every `.py` file and `requirements*.txt`) under Apache-2.0; see `LICENSE`, `LICENSE-CODE` and `TERMS.md`. Credit the data as "EMG-1 3-channel dataset, Vineeth Velmurugan, Encord, 2026, CC BY 4.0" and cite this v1.0.1 release with `CITATION.cff`.

Intended uses are research on surface-EMG decoding of hand activity, egocentric activity recognition with wrist EMG, multimodal sensor fusion and human-computer interaction. As guidance, not a licence restriction, the dataset is not intended for biometric identification or re-identification, monitoring or evaluating workers or individuals, or clinical diagnosis or medical decisions.

The maintainer is Vineeth Velmurugan (Encord). Send questions, errata, takedown requests and withdrawal requests to support@encord.com; see `CONTACT.md`. See `EVALUATION.md`, `DATASHEET.md`, `KNOWN_ISSUES.md`, and `CHANGELOG.md`.
