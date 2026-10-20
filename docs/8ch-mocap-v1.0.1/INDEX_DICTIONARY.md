# Index dictionary

All counts use 920 takes. Boolean true-counts are computed from the shipped index. Threshold names refer to `thresholds.json`. An empty true-count means the field is not Boolean.

| Column | Type | Meaning | Threshold key | True-count |
|---|---|---|---|---:|
| `take_id` | string | Take identifier with underscores | none |  |
| `subject_id` | string | Pseudonymous person code | none |  |
| `session_id` | string | Session code | none |  |
| `transport` | string | Band connection transport | none |  |
| `clock_epoch_id` | string | Within-person clock epoch code | none |  |
| `subject_relative_epoch_start_s` | double | Epoch start relative to person clock origin, seconds | none |  |
| `epoch_start_uncertainty_s` | double | Estimated epoch start uncertainty, seconds | none |  |
| `take_start_subject_relative_s` | double | Take start relative to person clock origin, seconds | none |  |
| `take_start_anchor_uncertainty_s` | double | Take anchor uncertainty, seconds | none |  |
| `take_start_placement_uncertainty_s` | double | Take placement uncertainty including epoch anchor, seconds | none |  |
| `duration_s` | double | Recording window duration, seconds | none |  |
| `EMG_TIER` | string | GOLD: coverage >=0.99, no failed channel, monotonic timestamps, maximum gap <=0.1 s and valid 8-channel rate; STANDARD: coverage >=0.90 and at most one failed channel; otherwise EXTENDED | gold_coverage / standard_coverage / gold_max_gap_s / rate_error_fraction |  |
| `MULTIMODAL_TIER` | string | GOLD: EMG GOLD with no marker, video or sync flags; STANDARD: EMG GOLD or STANDARD, video coverage >=0.90 and marker dropout <=0.30; otherwise EXTENDED | video_standard_coverage / marker_standard_max_dropout |  |
| `emg_coverage` | double | EMG sample count divided by nominal recording-window count, capped at 1 | gold_coverage / standard_coverage |  |
| `emg_max_gap_s` | double | Longest EMG timestamp or edge gap, seconds | gold_max_gap_s |  |
| `failed_channels` | int64 | Channels failing finite, flat, rail, mains or duplicate checks | flat_run_s / rail_run_s / rail_abs / duplicate_corr / mains_prominence_db |  |
| `video_frames` | int64 | Retained video frames | none |  |
| `unmatched_frame_rows` | int64 | Video log rows without a matching frame | none |  |
| `sync_window_coverage` | double | Share of lag windows with score above sync_min_score | sync_min_score / sync_min_window_coverage |  |
| `sync_swing_ms` | double | Range of measured lag windows, milliseconds | sync_max_swing_ms |  |
| `privacy_status` | string | Privacy status code recorded at packaging | none |  |
| `source` | string | Take path with slashes | none |  |
| `marker_label_version` | string | Canonical R1 marker mapping; 1.0.0 is retained in unchanged data files | none |  |
| `marker_fixes_applied` | string | JSON automatic repairs: T34 swaps tip and mid trajectories; a mixed T23 flag masks the tip marker on failing frames, and a whole-take T23 failure quarantines the digit | none |  |
| `has_marker_fixes` | bool | Any canonical marker identity repair or mask was applied | none | 282 |
| `has_tip_DIP_swap` | bool | An automatic whole-take tip and distal marker swap was applied | none | 41 |
| `has_identity_mask` | bool | At least one canonical marker frame was masked for uncertain identity | none | 32 |
| `has_unresolved_marker_identity` | bool | A whole-take marker identity ambiguity remains masked | none | 1 |
| `has_OP002_reversal` | bool | OP-002 canonical base and knuckle labels were reversed from vendor labels | none | 216 |
| `lag_ms` | double | Applied band-to-mocap lag in milliseconds; HDF5 lag_ms can be diagnostic | none |  |
| `lag_measured` | bool | A usable band-to-mocap lag was estimated and applied | none | 863 |
| `lag_unmeasured` | bool | No usable band-to-mocap lag was applied | none | 57 |
| `lag_low_coverage` | bool | Lag window coverage is below sync_min_window_coverage | sync_min_window_coverage | 325 |
| `lag_swing_over_50ms` | bool | Range of lag estimates exceeds sync_max_swing_ms | sync_max_swing_ms | 162 |
| `has_marker_speed_artifact` | bool | At least one adjacent marker speed exceeds 5 m/s | none | 90 |
| `has_marker_dropout` | bool | Maximum per-marker dropout fraction exceeds marker_max_dropout | marker_max_dropout | 56 |
| `has_vendor_marker_repairs` | bool | Vendor gap-filled marker positions occur | none | 2 |
| `has_marker_repair_burden` | bool | Vendor repaired-position fraction exceeds marker_max_repaired_share | marker_max_repaired_share | 0 |
| `has_emg_timestamp_reset` | bool | EMG timestamps have at least one backward reset | none | 0 |
| `has_emg_timestamp_duplicate` | bool | EMG timestamps have at least one duplicate | none | 0 |
| `has_video_unmatched_rows` | bool | At least one video log row has no matching retained frame | none | 920 |
| `has_video_coverage_issue` | bool | Recording-window or frame-log video coverage is below video_gold_coverage | video_gold_coverage / video_standard_coverage | 28 |
| `has_channel_failure` | bool | At least one EMG channel fails finite, flat, rail, mains or duplicate checks | none | 0 |
| `has_duplicate_channels` | bool | At least one EMG channel pair correlation exceeds duplicate_corr | duplicate_corr | 0 |
| `has_rate_config_issue` | bool | EMG is not 8 channels or measured count/span rate differs by more than rate_error_fraction from 2 kHz | rate_error_fraction | 50 |
| `has_epoch_uncertainty_over_50ms` | bool | Epoch start uncertainty exceeds 0.05 s | none | 399 |
| `has_epoch_change` | bool | Clock epoch identifier is later than the first epoch for this person | none | 576 |
| `camera_sensors_raw_undecoded` | bool | Camera sensor payloads are retained as raw undecoded bytes | none | 920 |
| `native_bundle_deferred` | bool | Native TAK and SVO2 source bundles are not included | none | 920 |
| `has_no_depth` | bool | No depth stream was recorded | none | 920 |
| `physical_band_identity_unknown` | bool | Band serial identity was removed and is not verified | none | 920 |
| `anatomical_mapping_unconfirmed` | bool | Electrode to anatomy mapping is unconfirmed | none | 920 |
| `has_emg_flat_channel` | bool | An EMG channel has a flat run longer than flat_run_s | flat_run_s | 0 |
| `has_emg_railed_channel` | bool | An EMG channel remains near rail_abs longer than rail_run_s | rail_run_s / rail_abs | 0 |
| `has_emg_nonfinite` | bool | An EMG sample is nonfinite | none | 0 |
| `has_mains_noise` | bool | An EMG channel exceeds mains_prominence_db | mains_prominence_db | 0 |
| `has_vendor_dropped_markers` | bool | Vendor marker stream has dropped marker observations | none | 1 |
| `has_unlabelled_vendor_marker_changes` | bool | Vendor marker order changed without a label update | none | 0 |
| `has_missing_camera_sensor_topic` | bool | Expected camera sensor topic is absent | none | 70 |
| `has_emg_gaps` | bool | EMG timestamps contain a gap longer than 1.5 nominal periods inside the stream; a late start or early end is not flagged | none | 886 |
| `has_imu_gaps` | bool | IMU timestamps contain a gap longer than 1.5 nominal periods inside the stream; a late start or early end is not flagged | none | 431 |
| `has_ppg_gaps` | bool | PPG timestamps contain a gap longer than 1.5 nominal periods inside the stream; a late start or early end is not flagged | none | 404 |
| `has_markers_gaps` | bool | Mocap timestamps contain a gap longer than 1.5 nominal periods inside the stream; a late start or early end is not flagged | none | 146 |
| `has_video_gaps` | bool | Video timestamps contain a gap longer than 1.5 nominal periods inside the stream; a late start or early end is not flagged | none | 920 |
| `has_any_gaps` | bool | At least one modality has an internal timestamp gap | none | 920 |
| `transport_dongle` | bool | True when transport is dongle | none | 192 |
| `transport_wifi` | bool | True when transport is wifi | none | 200 |
| `transport_ble` | bool | True when transport is ble | none | 528 |
| `transport_unknown` | bool | True when transport is unknown | none | 0 |
| `emg_tier_gold` | bool | True when the named tier is GOLD | none | 775 |
| `emg_tier_standard` | bool | True when the named tier is STANDARD | none | 137 |
| `emg_tier_extended` | bool | True when the named tier is EXTENDED | none | 8 |
| `multimodal_tier_gold` | bool | True when the named tier is GOLD | none | 346 |
| `multimodal_tier_standard` | bool | True when the named tier is STANDARD | none | 526 |
| `multimodal_tier_extended` | bool | True when the named tier is EXTENDED | none | 48 |
| `has_mediapipe_stereo_est` | bool | Derived file contains a MediaPipe stereo estimate group | none | 919 |
| `default_smoke_partition` | string | Train, validation or test partition of convenience split | none |  |
| `marker_speed_artifact_proxy` | bool | Duplicate of has_marker_speed_artifact for compatibility | none | 90 |
| `lag_boundary_unmeasured` | bool | The median good-window lag is within one 2 ms step of the 300 ms search limit, or every good window is at that limit or has a degenerate score of 1.0; no lag is applied | none | 7 |

A 5 m/s adjacent-marker speed is a fixed geometric check, not a `thresholds.json` key. `T34` is an automatic tip/mid trajectory swap; `T23` flags a base-to-middle ordering failure: for a digit classed mixed the tip marker is masked on failing frames, and a whole-take failure masks the whole canonical digit. `canonical-R1-1.0.0` names the unchanged R1 mapping.

The flat `take_id` `OP-001_s003_01` and path `source` `OP-001/s003/01` identify the same take. `marker_speed_artifact_proxy` duplicates `has_marker_speed_artifact`. Flags true for every take indicate a release-wide limitation; they cannot select a cleaner subset. `index/input_disposition.parquet` accounts for vendor-kept, excluded and missing-input recordings before this release selection. It records the disposition of each raw input but not its raw digest or size; those stay private because a digest of a redacted or withheld input would let anyone confirm guesses of the removed values.

Example filter:

```python
import pyarrow.parquet as pq
rows = pq.read_table("index/takes.parquet").to_pylist()
sources = [r["source"] for r in rows if r["EMG_TIER"] in ("GOLD", "STANDARD") and r["lag_measured"]]
from loader.dataset import EMGDataset
ds = EMGDataset(".", sources=sources, split="default_smoke", target_frame="wrist")
```
