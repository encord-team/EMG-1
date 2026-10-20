# Datasheet for EMG-1 8-channel v1.0.1

## Motivation

This dataset supports research on wearable surface EMG for hand interaction, especially predicting automatic fingertip proximity from EMG. Wrist-frame finger pose and palm-aligned camera versus mocap comparison are reference tasks. The collection target was 20 hours; the released recording windows total 15.036 hours.

Funding: Encord. Author and maintainer: Vineeth Velmurugan (Encord). The recordings were collected for Encord by a commercial data-collection vendor.

## Composition

There are 920 takes from 12 people and 15.036 recording-window hours, selected from 921 vendor-kept takes (1 excluded; see `selection_waterfall.json`). Every recorded hand is left. Person codes are pseudonyms, and no identity mapping ships. Per-person demographics are withheld, and v1.0.1 publishes no demographic aggregates. The default split retains the uploaded partitions of existing people and assigns new people to train. Counts and hours below are generated from `index/takes.parquet`.

| Partition | Takes | Hours |
|---|---:|---:|
| Train | 632 | 10.213 |
| Validation | 216 | 3.617 |
| Test | 72 | 1.205 |

Each take contains eight EMG channels, six band IMU channels, two PPG channels, 23 optical skin markers and external stereo video. HDF5 holds sensor values, exact relative timestamps, validity masks, source metadata and automatic estimates. MCAP carries video. C3D carries mocap. Native TAK and SVO2 files are not included in v1.0.1. There are no human activity or contact annotations. `contact_est` is an automatic fingertip proximity proxy. The video is not visually anonymised and faces were not blurred, so people in the recordings may be recognisable.

## Collection process

The recordings were collected for Encord by a commercial data-collection vendor. Encord holds the rights to release these recordings publicly, including the video. Recruitment, consent procedures, compensation and ethics review: not reported.

The band is worn high on the forearm, below the elbow (owner report). The participant moved the left hand and fingers freely, with no prescribed pose during movement. Scenario and rest variants are recorded per take in `index/takes_extra.parquet`. The band firmware and nominal rates are summarised in `index/aggregate_facts.json`. There is no maximum voluntary contraction calibration. Electrode type and exact placement: not provided by the vendor. Channel order: not provided by the vendor. Hardware filters: not provided by the vendor. Physical EMG amplitude units (volts): not provided by the vendor.

EMG is nominally 2 kHz and appears as ADC counts divided by 2^23 in the source metadata. Per-take measured sensor rates and nominal PPG rates must be read from the manifest and sidecar. Mocap is nominally 120 Hz and video 60 Hz. The camera is external to the hand. No depth stream was recorded.

## Time synchronisation and processing

Band and mocap streams use LSL `local_clock()` co-registration; mocap is stamped at camera mid-exposure when available. The published `index/takes.parquet` `lag_ms` is the applied band-to-mocap correction, while an HDF5 lag field can retain a diagnostic value. Positive lag means band time t corresponds to mocap time t minus lag. The median applied lag is 14.000 ms, with measured range -166.000 to 240.000 ms. Use `applied_lag_ms` only when the HDF5 status is `measured`. Other statuses are `sync unmeasured` and `boundary_unmeasured`; the loader applies zero for these. The lag estimates band IMU timing, not EMG physiology. Clock-epoch placement and uncertainty are recorded separately. There is no statistical lag confidence interval.

Automatic identity repairs and masks produce a canonical marker order while the raw observed order and vendor repaired positions remain. Contact labels use thumb-tip distance to each other fingertip: 1 below 20 mm, 0 above 30 mm, and -1 between thresholds or when missing. It is a proximity estimate, not touch ground truth. The estimated camera keypoints, quality tiers and lag are also automatic and unverified by humans. Current vision coverage is computed from shipped derived files by `tools/metadata.py`; do not assume every take has an estimate.

## Uses

Intended uses: research on surface-EMG decoding, hand pose and contact estimation, human-computer interaction and assistive-technology research. The release documents T1 contact detection, T2 wrist-frame pose and T3 vision comparison.

Not intended for: biometric identification or re-identification of people, monitoring of workers or individuals, and clinical diagnosis or medical decisions. This is guidance, not a licence restriction.

Pose labels are skin marker locations rather than joint centres. The world coordinate origin and cross-session stability are not established. Quality tiers and masks must be considered when interpreting results.

## Distribution

v1.0.1 was released on 2026-10-20 as a free and open dataset. The files are served over HTTPS from a publicly readable bucket, and downloads need no account or credentials. Take the base URL from the bucket-root README and pass it to `tools/download.py`; `BUCKET_README.md` gives the commands. Source code files (every `*.py` file and every requirements file) are licensed under Apache-2.0 (`LICENSE-CODE`), and every other file under CC BY 4.0 (`LICENSE`). The `access` value embedded in the take files predates the open release and is superseded by `LICENSE` (see `KNOWN_ISSUES.md`). Attribution: "EMG-1 8-channel dataset, Vineeth Velmurugan, Encord, 2026, CC BY 4.0". Cite the dataset with `CITATION.cff`. It has no DOI yet; a DOI may be added later. Test labels are included. No direct identity mapping or per-person demographic record is included.

## Maintenance

Maintainer: Vineeth Velmurugan (Encord). Contact: support@encord.com for questions, errata, takedown and withdrawal requests (`CONTACT.md`).

Errata: report errors to support@encord.com; fixes ship as new versions with a `CHANGELOG.md` entry. Withdrawal: send requests to support@encord.com; the affected recordings are removed from later versions. Retention: released versions stay available unless a withdrawal or legal request requires removal. Copies that people have already downloaded cannot be recalled.
