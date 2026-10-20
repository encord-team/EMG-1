# Field dictionary for v1.0.1

Times are nanoseconds unless a field explicitly names milliseconds or seconds. CSV booleans use `True` and `False`; Parquet retains typed booleans. Null means a source value was unavailable or a measurement was not applicable; it is not the same as false or zero. HDF5 NaN values require the accompanying validity mask. A clip is the original recording chunk. A quality segment is a half-open interval on the quality clock. A station-day is one recording kit on one calendar day. Quality thresholds come from `derived/quality/tier_rule.py` for whole clips and `derived/quality/segment_rule.py` for intervals. `clip_hours_with_emg` is clip duration converted to hours; `hours` and the per-wrist and both-wrist quality-hour fields sum intervals from the segment rule.

`SCHEMA.json` lists every HDF5 path with dtype, shape, units, clock, nominal rate and a description. The tables below list every field of the released Parquet indexes. For a boolean, `true count` is computed from the shipped table. `source_key` and `source_etag` are vendor source fields; raw destination keys and ETags are in `raw/RAW_OBJECTS.csv`.

`copy_manifest.csv` is the raw-copy plan with destination key, bytes and source ETag; `starter/raw_copy_keys.csv` is its starter subset. Their vendor source keys were removed. `raw/RAW_OBJECTS.csv` is the destination access index with clip_id, release_key, bytes, etag and part_size; it has rows only after the raw copy is reconciled (see `raw/README.md`). Use the destination index for access.

MF means multi-face pose estimate, SU means screened single-face estimate, and IPPE is planar pose estimation from tag corners. `stage1_complete` means primary L1 extraction completed; 2 PPG-only files exist where it is false. `extra_complete` means supplementary extraction is complete.

## Index fields

### index/clips.parquet

| Field | Type | Units | Meaning | True count |
| --- | --- | --- | --- | ---: |
| `clip_id` | `string` | text or structured value | Stable recording clip identifier, not a person identifier. |  |
| `source_key` | `string` | text or structured value | Original vendor storage key for raw-copy provenance; not a release download path. |  |
| `bytes` | `int64` | bytes | Raw source object length in bytes. |  |
| `source_etag` | `string` | text or structured value | ETag from the vendor raw source object; multipart ETags are not SHA256. |  |
| `date` | `string` | text or structured value | UTC recording calendar date parsed from the clip identifier. |  |
| `station` | `string` | text or structured value | Recording kit identifier, not a person identifier. |  |
| `session_id` | `string` | text or structured value | Vendor recording session grouping for one kit and run. |  |
| `duration_s` | `double` | s | Duration s in seconds. |  |
| `mcap_duration_s` | `double` | s | Mcap duration s in seconds. |  |
| `clip_tier` | `string` | text or structured value | Whole-clip grade from the clip tier rule. |  |
| `flags` | `string` | text or structured value | List of recorded quality or extraction diagnostics. |  |
| `span_broken` | `bool` | boolean | True when MCAP timestamps near epoch zero make the raw time span unreliable. | 109 |
| `topics` | `string` | text or structured value | JSON mapping of MCAP topic names to message counts. |  |
| `sensor_path` | `string` | text or structured value | Relative path to the L1 sensor HDF5 file, if available. |  |
| `pose_path` | `string` | text or structured value | Automatic optical cap pose path; validity is tracked separately. |  |
| `vendor_path` | `string` | text or structured value | Relative path to the vendor JSON sidecar. |  |
| `stage1_complete` | `bool` | boolean | True when the primary L1 extraction completed; a PPG-only file can exist when false. | 4914 |
| `timestamp_exact_all_streams` | `bool` | boolean | False because some camera and odometry stamps were rounded during extraction. | 0 |
| `split` | `string` | text or structured value | Primary station-day partition: train, val or test. |  |
| `has_head_stereo` | `bool` | boolean | True when this recording contains head stereo. | 4915 |
| `has_depth` | `bool` | boolean | True when this recording contains depth. | 4915 |
| `has_wrist_left_camera` | `bool` | boolean | True when this recording contains wrist left camera. | 4916 |
| `has_wrist_right_camera` | `bool` | boolean | True when this recording contains wrist right camera. | 4916 |
| `has_head_imu` | `bool` | boolean | True when this recording contains head imu. | 4915 |
| `has_wrist_left_imu` | `bool` | boolean | True when this recording contains wrist left imu. | 4526 |
| `has_wrist_right_imu` | `bool` | boolean | True when this recording contains wrist right imu. | 4756 |
| `has_odom` | `bool` | boolean | True when this recording contains odom. | 4913 |
| `left_serial` | `string` | text or structured value | Device serial reported by the band. Side: left. |  |
| `left_firmware` | `string` | text or structured value | Firmware version reported by the band. Side: left. |  |
| `left_config` | `string` | text or structured value | Recorder settings for this band, serialized as JSON. Side: left. |  |
| `left_tier` | `string` | text or structured value | Left-band whole-clip grade from the clip tier rule. |  |
| `left_flags` | `string` | text or structured value | Quality diagnostics for this band. Side: left. |  |
| `right_serial` | `string` | text or structured value | Device serial reported by the band. Side: right. |  |
| `right_firmware` | `string` | text or structured value | Firmware version reported by the band. Side: right. |  |
| `right_config` | `string` | text or structured value | Recorder settings for this band, serialized as JSON. Side: right. |  |
| `right_tier` | `string` | text or structured value | Right-band whole-clip grade from the clip tier rule. |  |
| `right_flags` | `string` | text or structured value | Quality diagnostics for this band. Side: right. |  |
| `both_gold_hours` | `double` | h | Both gold hours in hours. |  |
| `both_standard_hours` | `double` | h | Both standard hours in hours. |  |
| `left_gold_hours` | `double` | h | Left gold hours in hours. |  |
| `left_standard_hours` | `double` | h | Left standard hours in hours. |  |
| `right_gold_hours` | `double` | h | Right gold hours in hours. |  |
| `right_standard_hours` | `double` | h | Right standard hours in hours. |  |
| `per_wrist_gold_hours` | `double` | h | Per wrist gold hours in hours. |  |
| `per_wrist_standard_hours` | `double` | h | Per wrist standard hours in hours. |  |
| `pose_frames` | `int64` | count | Automatic optical cap pose frames; validity is tracked separately. |  |
| `pose_mf_fraction` | `double` | fraction | Automatic optical cap pose mf fraction; validity is tracked separately. |  |
| `pose_su_fraction` | `double` | fraction | Automatic optical cap pose su fraction; validity is tracked separately. |  |
| `extra_complete` | `bool` | boolean | True when the supplementary derived extraction finished. | 4916 |
| `station_day` | `string` | text or structured value | Recording kit and UTC calendar day used as the split group. |  |
| `task_categories` | `list<element: string>` | text or structured value | Categories present in vendor task segments for this clip. |  |
| `task_mix` | `string` | text or structured value | Vendor task-category duration mix for this clip, not quality-window labels. |  |
| `task_category` | `string` | text or structured value | Category assigned from vendor title rules; other includes clips without vendor segments. |  |
| `vendor_derived_unverified` | `bool` | boolean | True when task labels come from the unaudited vendor sidecar. | 4916 |
| `both_gold_standard_hours` | `double` | h | Both gold standard hours in hours. |  |
| `clip_hours_with_emg` | `double` | h | Clip duration with EMG converted to hours. |  |
| `failing_band_1325482500024` | `bool` | boolean | True when the known degraded left band is present. | 676 |
| `missing_wrist_imu_left` | `bool` | boolean | True when wrist imu left is unavailable. | 390 |
| `recorder_200hz_left` | `bool` | boolean | True when this band used the unsuitable 200 Hz recorder setting. | 153 |
| `clock_nonlinear_left` | `bool` | boolean | True when fitted host residual knots depart from an endpoint line by over 5 ms. | 76 |
| `dropouts_left` | `bool` | boolean | True when this band has packet losses or positive EMG device-clock steps above 3 x 469 ticks (about 1.41 ms). | 3919 |
| `qc_identity_left` | `string` | text or structured value | Frozen quality assessment qc identity left from the segment rule. |  |
| `missing_wrist_imu_right` | `bool` | boolean | True when wrist imu right is unavailable. | 160 |
| `recorder_200hz_right` | `bool` | boolean | True when this band used the unsuitable 200 Hz recorder setting. | 184 |
| `clock_nonlinear_right` | `bool` | boolean | True when fitted host residual knots depart from an endpoint line by over 5 ms. | 75 |
| `dropouts_right` | `bool` | boolean | True when this band has packet losses or positive EMG device-clock steps above 3 x 469 ticks (about 1.41 ms). | 4617 |
| `qc_identity_right` | `string` | text or structured value | Frozen quality assessment qc identity right from the segment rule. |  |
| `recorder_200hz` | `bool` | boolean | True when the recorder used an unsuitable 200 Hz EMG setting. | 184 |
| `clock_nonlinear` | `bool` | boolean | True when fitted host residual knots depart from an endpoint line by over 5 ms. | 79 |
| `dropouts` | `bool` | boolean | True when packet losses or positive EMG device-clock steps above 3 x 469 ticks (about 1.41 ms) were detected. | 4817 |
| `head_stamp_slip_station` | `bool` | boolean | station-level known risk, not per-clip confirmed slip. | 1576 |
| `derived_sensor_path` | `string` | text or structured value | Relative path to the estimated sensor-clock HDF5 file. |  |
| `pose_availability_reason` | `string` | text or structured value | Automatic optical cap pose availability reason; validity is tracked separately. |  |
| `physical_side_quarantined` | `bool` | boolean | True when wrist-side identity is too uncertain for pose targets. | 74 |
| `video_frame_tables_complete` | `bool` | boolean | True when all expected frame-index tables exist for this clip. | 0 |
| `first_valid_timestamp_ns_left` | `int64` | count | First positive estimated EMG host timestamp for this side, in nanoseconds. |  |
| `last_valid_timestamp_ns_left` | `int64` | count | Last positive estimated EMG host timestamp for this side, in nanoseconds. |  |
| `first_valid_timestamp_ns_right` | `int64` | count | First positive estimated EMG host timestamp for this side, in nanoseconds. |  |
| `last_valid_timestamp_ns_right` | `int64` | count | Last positive estimated EMG host timestamp for this side, in nanoseconds. |  |
| `first_valid_timestamp_ns` | `int64` | ns | Timestamp in nanoseconds on the recorder host clock (estimated from device ticks). |  |
| `last_valid_timestamp_ns` | `int64` | ns | Timestamp in nanoseconds on the recorder host clock (estimated from device ticks). |  |
| `pose_uninterrupted_runs` | `int64` | count | Automatic optical cap pose uninterrupted runs; validity is tracked separately. |  |
| `pose_max_uninterrupted_run_s` | `double` | s | Pose max uninterrupted run s in seconds. |  |
| `pose_world_valid_frames` | `int64` | count | Automatic optical cap pose world valid frames; validity is tracked separately. |  |
| `pose_run_cap_seconds_bins` | `list<element: double>` | s | Automatic optical cap pose run cap seconds bins; validity is tracked separately. |  |
| `pose_paired_emg_frames` | `int64` | count | Automatic optical cap pose paired emg frames; validity is tracked separately. |  |
| `clock_fault_left` | `bool` | boolean | True when either wrist has an estimated clock fault. This is the left side. | 2 |
| `clock_fault_right` | `bool` | boolean | True when either wrist has an estimated clock fault. This is the right side. | 2 |
| `clock_fault` | `bool` | boolean | True when either wrist has an estimated clock fault. | 3 |
| `timestamp_validity_definition` | `string` | text or structured value | Text naming the rule used to mark a timestamp valid. |  |
| `emg_observed_rate_hz_left` | `double` | Hz | Observed EMG sample rate for the named wrist in hertz. |  |
| `emg_observed_rate_hz_right` | `double` | Hz | Observed EMG sample rate for the named wrist in hertz. |  |
| `mcap_duration_untrusted_reason` | `string` | text or structured value | span_broken_epoch_zero for untrusted MCAP span, otherwise null. |  |

### index/segments.parquet

| Field | Type | Units | Meaning | True count |
| --- | --- | --- | --- | ---: |
| `segment_id` | `string` | text or structured value | Identifier of a quality or vendor segment within a clip. |  |
| `clip_id` | `string` | text or structured value | Stable recording clip identifier, not a person identifier. |  |
| `scope` | `string` | enum: left, right, both | Wrist coverage of a quality interval: left, right, or both. |  |
| `start_t_ns` | `int64` | ns | Timestamp in nanoseconds on the recorder host clock. |  |
| `end_t_ns` | `int64` | ns | Timestamp in nanoseconds on the recorder host clock. |  |
| `duration_s` | `double` | s | Duration s in seconds. |  |
| `tier` | `string` | text or structured value | Frozen signal usability grade, not task ground truth. |  |
| `w_start` | `int64` | 1 s quality-window index | First quality-window index, inclusive, at one-second resolution. |  |
| `w_end` | `int64` | 1 s quality-window index | Last quality-window index, exclusive, at one-second resolution. |  |
| `flags` | `string` | text or structured value | List of recorded quality or extraction diagnostics. |  |
| `sensor_available` | `bool` | boolean | True when both extracted sensor inputs needed for a quality window are present. | 52552 |
| `split` | `string` | text or structured value | Primary station-day partition: train, val or test. |  |
| `hours` | `double` | h | Duration of this quality interval in hours. |  |
| `station_day` | `string` | text or structured value | Recording kit and UTC calendar day used as the split group. |  |
| `station` | `string` | text or structured value | Recording kit identifier, not a person identifier. |  |
| `task_category` | `string` | text or structured value | Category assigned from vendor title rules; other includes clips without vendor segments. |  |
| `task_mix` | `string` | text or structured value | Vendor task-category duration mix for this clip, not quality-window labels. |  |
| `vendor_derived_unverified` | `bool` | boolean | True when task labels come from the unaudited vendor sidecar. | 52578 |
| `span_broken` | `bool` | boolean | True when MCAP timestamps near epoch zero make the raw time span unreliable. | 1037 |
| `failing_band_1325482500024` | `bool` | boolean | True when the known degraded left band is present. | 4321 |
| `missing_wrist_imu_left` | `bool` | boolean | True when wrist imu left is unavailable. | 3212 |
| `missing_wrist_imu_right` | `bool` | boolean | True when wrist imu right is unavailable. | 1852 |
| `recorder_200hz` | `bool` | boolean | True when the recorder used an unsuitable 200 Hz EMG setting. | 118 |
| `clock_nonlinear` | `bool` | boolean | True when fitted host residual knots depart from an endpoint line by over 5 ms. | 933 |
| `dropouts` | `bool` | boolean | True when packet losses or positive EMG device-clock steps above 3 x 469 ticks (about 1.41 ms) were detected. | 52253 |
| `head_stamp_slip_station` | `bool` | boolean | station-level known risk, not per-clip confirmed slip. | 17554 |
| `physical_side_quarantined` | `bool` | boolean | True when wrist-side identity is too uncertain for pose targets. | 5 |
| `task_category_scope` | `string` | text or structured value | Whether category is clip-dominant or segment-local. |  |
| `clock_nonlinear_left` | `bool` | boolean | True when fitted host residual knots depart from an endpoint line by over 5 ms. | 897 |
| `clock_nonlinear_right` | `bool` | boolean | True when fitted host residual knots depart from an endpoint line by over 5 ms. | 877 |
| `clock_fault` | `bool` | boolean | True when either wrist has an estimated clock fault. | 11 |
| `clock_fault_left` | `bool` | boolean | True when either wrist has an estimated clock fault. This is the left side. | 9 |
| `clock_fault_right` | `bool` | boolean | True when either wrist has an estimated clock fault. This is the right side. | 5 |
| `recorder_200hz_left` | `bool` | boolean | True when this band used the unsuitable 200 Hz recorder setting. | 0 |
| `recorder_200hz_right` | `bool` | boolean | True when this band used the unsuitable 200 Hz recorder setting. | 118 |
| `dropouts_left` | `bool` | boolean | True when this band has packet losses or positive EMG device-clock steps above 3 x 469 ticks (about 1.41 ms). | 43559 |
| `dropouts_right` | `bool` | boolean | True when this band has packet losses or positive EMG device-clock steps above 3 x 469 ticks (about 1.41 ms). | 50708 |

### index/video_streams.parquet

| Field | Type | Units | Meaning | True count |
| --- | --- | --- | --- | ---: |
| `clip_id` | `string` | text or structured value | Stable recording clip identifier, not a person identifier. |  |
| `stream` | `string` | text or structured value | Named camera or depth stream in the frame index. |  |
| `topic` | `string` | text or structured value | Original MCAP topic corresponding to this stream. |  |
| `expected_messages` | `int64` | count | Expected message count from the source topic inventory. |  |
| `indexed_messages` | `int64` | count | Messages indexed in the shipped frame table. |  |
| `available` | `bool` | boolean | True when this index or stream is available. | 4914 |
| `path` | `string` | text or structured value | Relative path of this index or stream file; null means absent. |  |
| `reason` | `string` | text or structured value | Reason this stream or index is unavailable. |  |

### vendor/segments.parquet

| Field | Type | Units | Meaning | True count |
| --- | --- | --- | --- | ---: |
| `clip_id` | `string` | text or structured value | Stable recording clip identifier, not a person identifier. |  |
| `vendor_segment_id` | `int64` | count | Identifier of the segment in its clip sidecar. |  |
| `title` | `string` | text or structured value | Original vendor task title, not a verified label. |  |
| `start_ts_ms` | `int64` | ms | Vendor-session start time in milliseconds; subtract vendor/<clip_id>.json data.start_ts for clip time. |  |
| `end_ts_ms` | `int64` | ms | Vendor-session end time in milliseconds; subtract vendor/<clip_id>.json data.start_ts for clip time. |  |
| `duration_ms` | `int64` | ms | Duration ms in milliseconds. |  |
| `task_category` | `string` | text or structured value | Category assigned from vendor title rules; other includes clips without vendor segments. |  |
| `vendor_derived_unverified` | `bool` | boolean | True when task labels come from the unaudited vendor sidecar. | 10401 |
| `clock` | `string` | text or structured value | Clock domain used for this interval, as named in the associated table. |  |

Vendor segment `start_ts_ms` and `end_ts_ms` are vendor-session milliseconds. Clip-relative milliseconds equal the value minus `vendor/<clip_id>.json` `data.start_ts`. HDF5 root attribute `schema_version=1.0.0` describes the extraction format; release label is v1.0.1.

## HDF5 paths

| Path | Type | Units | Meaning |
| --- | --- | --- | --- |
| `sensors/<clip_id>.h5/bands/left/emg/i` | `int64` | count or zero-based index | Zero-based sample index within the source package. |
| `sensors/<clip_id>.h5/bands/left/emg/ints` | `int64` | mixed timing units and package indices | Int64 stack of t_host_ns, t_dev, i and pkg_seq; EMG and IMU also include pkg_t_dev and pkg_t_host_ns. These are timing and package fields, not ADC counts. |
| `sensors/<clip_id>.h5/bands/left/emg/pkg_seq` | `int64` | count or zero-based index | Source packet sequence number for gap detection. |
| `sensors/<clip_id>.h5/bands/left/emg/pkg_t_dev` | `int64` | device ticks, nominal microseconds | Packet device clock ticks. |
| `sensors/<clip_id>.h5/bands/left/emg/pkg_t_host_ns` | `int64` | ns | Timestamp in nanoseconds on the recorder host clock. |
| `sensors/<clip_id>.h5/bands/left/emg/t_dev` | `int64` | device ticks, nominal microseconds | Original device clock ticks, nominal microseconds. |
| `sensors/<clip_id>.h5/bands/left/emg/t_host_ns` | `int64` | ns | Timestamp in nanoseconds on the recorder host clock. |
| `sensors/<clip_id>.h5/bands/left/emg/v` | `float32` | vendor amplitude units; scaling to physical units not provided by the vendor | Observed values in the documented channel order for this stream, stored as float32 cast from the recorder's decimal payload; rounding to the payload's decimals (EMG 8, IMU 6, PPG 3) recovers the recorded value. |
| `sensors/<clip_id>.h5/bands/left/host_clock` | `object` | structured metadata or text | Clock fit source and host time-base metadata for this band. |
| `sensors/<clip_id>.h5/bands/left/imu_h/i` | `int64` | count or zero-based index | Zero-based sample index within the source package. |
| `sensors/<clip_id>.h5/bands/left/imu_h/ints` | `int64` | mixed timing units and package indices | Int64 stack of t_host_ns, t_dev, i and pkg_seq; EMG and IMU also include pkg_t_dev and pkg_t_host_ns. These are timing and package fields, not ADC counts. |
| `sensors/<clip_id>.h5/bands/left/imu_h/pkg_seq` | `int64` | count or zero-based index | Source packet sequence number for gap detection. |
| `sensors/<clip_id>.h5/bands/left/imu_h/pkg_t_dev` | `int64` | device ticks, nominal microseconds | Packet device clock ticks. |
| `sensors/<clip_id>.h5/bands/left/imu_h/pkg_t_host_ns` | `int64` | ns | Timestamp in nanoseconds on the recorder host clock. |
| `sensors/<clip_id>.h5/bands/left/imu_h/t_dev` | `int64` | device ticks, nominal microseconds | Original device clock ticks, nominal microseconds. |
| `sensors/<clip_id>.h5/bands/left/imu_h/t_host_ns` | `int64` | ns | Timestamp in nanoseconds on the recorder host clock. |
| `sensors/<clip_id>.h5/bands/left/imu_h/v` | `float32` | [ax, ay, az] g; [gx, gy, gz] degrees/s | Observed values in the documented channel order for this stream, stored as float32 cast from the recorder's decimal payload; rounding to the payload's decimals (EMG 8, IMU 6, PPG 3) recovers the recorded value. |
| `sensors/<clip_id>.h5/bands/left/ppg/i` | `int64` | count or zero-based index | Zero-based sample index within the source package. |
| `sensors/<clip_id>.h5/bands/left/ppg/ints` | `int64` | mixed timing units and package indices | Int64 stack of t_host_ns, t_dev, i and pkg_seq; EMG and IMU also include pkg_t_dev and pkg_t_host_ns. These are timing and package fields, not ADC counts. |
| `sensors/<clip_id>.h5/bands/left/ppg/pkg_seq` | `int64` | count or zero-based index | Source packet sequence number for gap detection. |
| `sensors/<clip_id>.h5/bands/left/ppg/t_dev` | `int64` | device ticks, nominal microseconds | Original device clock ticks, nominal microseconds. |
| `sensors/<clip_id>.h5/bands/left/ppg/t_host_ns` | `int64` | ns | Timestamp in nanoseconds on the recorder host clock. |
| `sensors/<clip_id>.h5/bands/left/ppg/v` | `float32` | microvolts, two optical channels | Observed values in the documented channel order for this stream, stored as float32 cast from the recorder's decimal payload; rounding to the payload's decimals (EMG 8, IMU 6, PPG 3) recovers the recorded value. |
| `sensors/<clip_id>.h5/bands/right/emg/i` | `int64` | count or zero-based index | Zero-based sample index within the source package. |
| `sensors/<clip_id>.h5/bands/right/emg/ints` | `int64` | mixed timing units and package indices | Int64 stack of t_host_ns, t_dev, i and pkg_seq; EMG and IMU also include pkg_t_dev and pkg_t_host_ns. These are timing and package fields, not ADC counts. |
| `sensors/<clip_id>.h5/bands/right/emg/pkg_seq` | `int64` | count or zero-based index | Source packet sequence number for gap detection. |
| `sensors/<clip_id>.h5/bands/right/emg/pkg_t_dev` | `int64` | device ticks, nominal microseconds | Packet device clock ticks. |
| `sensors/<clip_id>.h5/bands/right/emg/pkg_t_host_ns` | `int64` | ns | Timestamp in nanoseconds on the recorder host clock. |
| `sensors/<clip_id>.h5/bands/right/emg/t_dev` | `int64` | device ticks, nominal microseconds | Original device clock ticks, nominal microseconds. |
| `sensors/<clip_id>.h5/bands/right/emg/t_host_ns` | `int64` | ns | Timestamp in nanoseconds on the recorder host clock. |
| `sensors/<clip_id>.h5/bands/right/emg/v` | `float32` | vendor amplitude units; scaling to physical units not provided by the vendor | Observed values in the documented channel order for this stream, stored as float32 cast from the recorder's decimal payload; rounding to the payload's decimals (EMG 8, IMU 6, PPG 3) recovers the recorded value. |
| `sensors/<clip_id>.h5/bands/right/host_clock` | `object` | structured metadata or text | Clock fit source and host time-base metadata for this band. |
| `sensors/<clip_id>.h5/bands/right/imu_h/i` | `int64` | count or zero-based index | Zero-based sample index within the source package. |
| `sensors/<clip_id>.h5/bands/right/imu_h/ints` | `int64` | mixed timing units and package indices | Int64 stack of t_host_ns, t_dev, i and pkg_seq; EMG and IMU also include pkg_t_dev and pkg_t_host_ns. These are timing and package fields, not ADC counts. |
| `sensors/<clip_id>.h5/bands/right/imu_h/pkg_seq` | `int64` | count or zero-based index | Source packet sequence number for gap detection. |
| `sensors/<clip_id>.h5/bands/right/imu_h/pkg_t_dev` | `int64` | device ticks, nominal microseconds | Packet device clock ticks. |
| `sensors/<clip_id>.h5/bands/right/imu_h/pkg_t_host_ns` | `int64` | ns | Timestamp in nanoseconds on the recorder host clock. |
| `sensors/<clip_id>.h5/bands/right/imu_h/t_dev` | `int64` | device ticks, nominal microseconds | Original device clock ticks, nominal microseconds. |
| `sensors/<clip_id>.h5/bands/right/imu_h/t_host_ns` | `int64` | ns | Timestamp in nanoseconds on the recorder host clock. |
| `sensors/<clip_id>.h5/bands/right/imu_h/v` | `float32` | [ax, ay, az] g; [gx, gy, gz] degrees/s | Observed values in the documented channel order for this stream, stored as float32 cast from the recorder's decimal payload; rounding to the payload's decimals (EMG 8, IMU 6, PPG 3) recovers the recorded value. |
| `sensors/<clip_id>.h5/bands/right/ppg/i` | `int64` | count or zero-based index | Zero-based sample index within the source package. |
| `sensors/<clip_id>.h5/bands/right/ppg/ints` | `int64` | mixed timing units and package indices | Int64 stack of t_host_ns, t_dev, i and pkg_seq; EMG and IMU also include pkg_t_dev and pkg_t_host_ns. These are timing and package fields, not ADC counts. |
| `sensors/<clip_id>.h5/bands/right/ppg/pkg_seq` | `int64` | count or zero-based index | Source packet sequence number for gap detection. |
| `sensors/<clip_id>.h5/bands/right/ppg/t_dev` | `int64` | device ticks, nominal microseconds | Original device clock ticks, nominal microseconds. |
| `sensors/<clip_id>.h5/bands/right/ppg/t_host_ns` | `int64` | ns | Timestamp in nanoseconds on the recorder host clock. |
| `sensors/<clip_id>.h5/bands/right/ppg/v` | `float32` | microvolts, two optical channels | Observed values in the documented channel order for this stream, stored as float32 cast from the recorder's decimal payload; rounding to the payload's decimals (EMG 8, IMU 6, PPG 3) recovers the recorded value. |
| `sensors/<clip_id>.h5/extra_source` | `object` | structured metadata or text | Provenance of the supplemental camera, IMU and odometry extraction. |
| `sensors/<clip_id>.h5/head_left_camera_info` | `object` | structured metadata or text | Camera calibration head left camera info from the source message. |
| `sensors/<clip_id>.h5/head_left_frames/log_time` | `int64` | ns | MCAP recorder log timestamp for this frame or tag observation. |
| `sensors/<clip_id>.h5/head_left_frames/stamp` | `int64` | ns | Camera header timestamp carried by the source message; may slip. |
| `sensors/<clip_id>.h5/imu_head/data` | `float64` | angular velocity rad/s; acceleration m/s^2 | Observed samples or message payload in the stream-specific channel order. |
| `sensors/<clip_id>.h5/imu_head/t_ns` | `int64` | ns | T ns in nanoseconds. |
| `sensors/<clip_id>.h5/imu_head/v` | `float64` | [gx, gy, gz] rad/s; [ax, ay, az] m/s^2 | Observed values in the documented channel order for this stream. |
| `sensors/<clip_id>.h5/imu_wrist_left/data` | `float64` | angular velocity rad/s; acceleration m/s^2 | Observed samples or message payload in the stream-specific channel order. |
| `sensors/<clip_id>.h5/imu_wrist_left/t_ns` | `int64` | ns | T ns in nanoseconds. |
| `sensors/<clip_id>.h5/imu_wrist_left/v` | `float64` | [gx, gy, gz] rad/s; [ax, ay, az] m/s^2 | Observed values in the documented channel order for this stream. |
| `sensors/<clip_id>.h5/imu_wrist_right/data` | `float64` | angular velocity rad/s; acceleration m/s^2 | Observed samples or message payload in the stream-specific channel order. |
| `sensors/<clip_id>.h5/imu_wrist_right/t_ns` | `int64` | ns | T ns in nanoseconds. |
| `sensors/<clip_id>.h5/imu_wrist_right/v` | `float64` | [gx, gy, gz] rad/s; [ax, ay, az] m/s^2 | Observed values in the documented channel order for this stream. |
| `sensors/<clip_id>.h5/mcap_metadata` | `object` | MCAP metadata fields | MCAP recorder metadata retained for provenance; not a pose measurement. |
| `sensors/<clip_id>.h5/odom/data` | `float64` | translation m; orientation quaternion | Observed samples or message payload in the stream-specific channel order. |
| `sensors/<clip_id>.h5/odom/frames` | `object` | structured metadata or text | Coordinate frame names attached to odometry transforms. |
| `sensors/<clip_id>.h5/odom/t_ns` | `int64` | ns | T ns in nanoseconds. |
| `sensors/<clip_id>.h5/odom/v` | `float64` | xyz m, quaternion xyzw | Observed values in the documented channel order for this stream. |
| `sensors/<clip_id>.h5/provenance` | `object` | structured metadata or text | Extraction provenance and software method metadata. |
| `sensors/<clip_id>.h5/source` | `object` | structured metadata or text | Source recording descriptors used for extraction provenance. |
| `sensors/<clip_id>.h5/tf_static` | `object` | structured metadata or text | Static coordinate transforms from recorded ROS messages. |
| `derived/sensors_est/<clip_id>_est.h5/bands/left/emg/clock_model_est` | `object` | structured metadata or text | Fitted device-to-host clock parameters, an estimate rather than a synchronized exposure time. |
| `derived/sensors_est/<clip_id>_est.h5/bands/left/emg/host_residual_ns_est` | `int64` | ns | Device-to-host fit residual for samples, in nanoseconds. |
| `derived/sensors_est/<clip_id>_est.h5/bands/left/emg/qc_t_ns_est` | `float64` | ns | Timestamp in nanoseconds on the recorder host clock (estimated from device ticks). |
| `derived/sensors_est/<clip_id>_est.h5/bands/left/emg/t_ns_est` | `int64` | ns | Estimated host-clock timestamp in nanoseconds. |
| `derived/sensors_est/<clip_id>_est.h5/bands/left/imu_h/clock_model_est` | `object` | structured metadata or text | Fitted device-to-host clock parameters, an estimate rather than a synchronized exposure time. |
| `derived/sensors_est/<clip_id>_est.h5/bands/left/imu_h/host_residual_ns_est` | `int64` | ns | Device-to-host fit residual for samples, in nanoseconds. |
| `derived/sensors_est/<clip_id>_est.h5/bands/left/imu_h/t_ns_est` | `int64` | ns | Estimated host-clock timestamp in nanoseconds. |
| `derived/sensors_est/<clip_id>_est.h5/bands/left/ppg/clock_model_est` | `object` | structured metadata or text | Fitted device-to-host clock parameters, an estimate rather than a synchronized exposure time. |
| `derived/sensors_est/<clip_id>_est.h5/bands/left/ppg/host_residual_ns_est` | `int64` | ns | Device-to-host fit residual for samples, in nanoseconds. |
| `derived/sensors_est/<clip_id>_est.h5/bands/left/ppg/t_ns_est` | `int64` | ns | Estimated host-clock timestamp in nanoseconds. |
| `derived/sensors_est/<clip_id>_est.h5/bands/right/emg/clock_model_est` | `object` | structured metadata or text | Fitted device-to-host clock parameters, an estimate rather than a synchronized exposure time. |
| `derived/sensors_est/<clip_id>_est.h5/bands/right/emg/host_residual_ns_est` | `int64` | ns | Device-to-host fit residual for samples, in nanoseconds. |
| `derived/sensors_est/<clip_id>_est.h5/bands/right/emg/qc_t_ns_est` | `float64` | ns | Timestamp in nanoseconds on the recorder host clock (estimated from device ticks). |
| `derived/sensors_est/<clip_id>_est.h5/bands/right/emg/t_ns_est` | `int64` | ns | Estimated host-clock timestamp in nanoseconds. |
| `derived/sensors_est/<clip_id>_est.h5/bands/right/imu_h/clock_model_est` | `object` | structured metadata or text | Fitted device-to-host clock parameters, an estimate rather than a synchronized exposure time. |
| `derived/sensors_est/<clip_id>_est.h5/bands/right/imu_h/host_residual_ns_est` | `int64` | ns | Device-to-host fit residual for samples, in nanoseconds. |
| `derived/sensors_est/<clip_id>_est.h5/bands/right/imu_h/t_ns_est` | `int64` | ns | Estimated host-clock timestamp in nanoseconds. |
| `derived/sensors_est/<clip_id>_est.h5/bands/right/ppg/clock_model_est` | `object` | structured metadata or text | Fitted device-to-host clock parameters, an estimate rather than a synchronized exposure time. |
| `derived/sensors_est/<clip_id>_est.h5/bands/right/ppg/host_residual_ns_est` | `int64` | ns | Device-to-host fit residual for samples, in nanoseconds. |
| `derived/sensors_est/<clip_id>_est.h5/bands/right/ppg/t_ns_est` | `int64` | ns | Estimated host-clock timestamp in nanoseconds. |
| `derived/sensors_est/<clip_id>_est.h5/qc` | `object` | structured metadata or text | Frozen signal-quality summary and flags for the clip. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/left_flat` | `int32` | count or zero-based index | Frozen quality assessment left flat from the segment rule. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/left_gap_ms` | `float32` | ms | Largest left-band sampling gap in this quality window, milliseconds. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/left_hard` | `int32` | count or zero-based index | Frozen quality assessment left hard from the segment rule. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/left_harm` | `float32` | fraction | Frozen quality assessment left harm from the segment rule. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/left_l50` | `float32` | fraction | Frozen quality assessment left l50 from the segment rule. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/left_n` | `int32` | count or zero-based index | Frozen quality assessment left n from the segment rule. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/left_rail` | `int32` | count or zero-based index | Frozen quality assessment left rail from the segment rule. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/left_rms` | `float32` | vendor amplitude units | Frozen quality assessment left rms from the segment rule. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/right_flat` | `int32` | count or zero-based index | Frozen quality assessment right flat from the segment rule. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/right_gap_ms` | `float32` | ms | Right gap ms in milliseconds. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/right_hard` | `int32` | count or zero-based index | Frozen quality assessment right hard from the segment rule. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/right_harm` | `float32` | fraction | Frozen quality assessment right harm from the segment rule. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/right_l50` | `float32` | fraction | Frozen quality assessment right l50 from the segment rule. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/right_n` | `int32` | count or zero-based index | Frozen quality assessment right n from the segment rule. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/right_rail` | `int32` | count or zero-based index | Frozen quality assessment right rail from the segment rule. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/right_rms` | `float32` | vendor amplitude units | Frozen quality assessment right rms from the segment rule. |
| `derived/sensors_est/<clip_id>_est.h5/quality_windows/w0_ns` | `int64` | ns | Host-clock nanoseconds at the first quality window. |
| `derived/sensors_est/<clip_id>_est.h5/segments` | `object` | structured metadata or text | Derived segment interval metadata on the frozen quality clock. |
| `derived/sensors_est/<clip_id>_est.h5/tags/accepted` | `bool` | boolean | Boolean tag detection accepted by geometric and image checks. |
| `derived/sensors_est/<clip_id>_est.h5/tags/ambiguity_margin_px` | `float64` | pixel | Ambiguity margin px in image pixels. |
| `derived/sensors_est/<clip_id>_est.h5/tags/camera_info_json` | `object` | structured metadata or text | Camera calibration camera info json from the source message. |
| `derived/sensors_est/<clip_id>_est.h5/tags/cap_ids` | `int16` | fiducial tag ID | Detected optical cap tag identifiers, not people identifiers. |
| `derived/sensors_est/<clip_id>_est.h5/tags/decoded_frames` | `int64` | count or zero-based index | Number of image frames successfully decoded for tag search. |
| `derived/sensors_est/<clip_id>_est.h5/tags/discarded_face_mask` | `uint8` | coded state or bit mask | Bit mask of tag faces rejected from this pose fit. |
| `derived/sensors_est/<clip_id>_est.h5/tags/full_search` | `bool` | boolean | Whether the detector searched the full image rather than a tracked region. |
| `derived/sensors_est/<clip_id>_est.h5/tags/geometry_json` | `object` | structured metadata or text | Tag corner geometry and detector configuration serialized as JSON. |
| `derived/sensors_est/<clip_id>_est.h5/tags/ippe_physical_valid` | `bool` | boolean | Whether the planar IPPE pose solution passes physical geometry checks. |
| `derived/sensors_est/<clip_id>_est.h5/tags/ippe_reason` | `object` | categorical text | Reason the IPPE solution was accepted or rejected. |
| `derived/sensors_est/<clip_id>_est.h5/tags/ippe_rmse_px` | `float64` | pixel | Ippe rmse px in image pixels. |
| `derived/sensors_est/<clip_id>_est.h5/tags/ippe_rvec` | `float64` | radian rotation vector | IPPE rotation vector for the planar tag solution. |
| `derived/sensors_est/<clip_id>_est.h5/tags/ippe_translation_nominal_m` | `float64` | nominal meters | IPPE translation in metres at nominal tag scale. |
| `derived/sensors_est/<clip_id>_est.h5/tags/log_time` | `int64` | ns | MCAP recorder log timestamp for this frame or tag observation. |
| `derived/sensors_est/<clip_id>_est.h5/tags/log_time_fault` | `bool` | boolean | True when MCAP log time fails the tag timing check. |
| `derived/sensors_est/<clip_id>_est.h5/tags/metadata_json` | `object` | structured metadata or text | Method settings and source descriptions serialized as JSON. |
| `derived/sensors_est/<clip_id>_est.h5/tags/nfaces` | `uint8` | count or zero-based index | Number of visible tag faces used or considered for the cap pose. |
| `derived/sensors_est/<clip_id>_est.h5/tags/rejection_reason` | `object` | categorical text | Detector or pose-fit reason for rejecting this observation. |
| `derived/sensors_est/<clip_id>_est.h5/tags/rmse_px` | `float64` | pixel | Rmse px in image pixels. |
| `derived/sensors_est/<clip_id>_est.h5/tags/rvec` | `float64` | radian rotation vector | Rotation vector of the estimated optical cap pose. |
| `derived/sensors_est/<clip_id>_est.h5/tags/single_tag_id` | `int16` | fiducial tag ID | Identifier of the single visible tag in an SU observation. |
| `derived/sensors_est/<clip_id>_est.h5/tags/source_json` | `object` | structured metadata or text | Tag source and extraction settings serialized as JSON. |
| `derived/sensors_est/<clip_id>_est.h5/tags/stamp` | `int64` | ns | Camera header timestamp carried by the source message; may slip. |
| `derived/sensors_est/<clip_id>_est.h5/tags/state` | `uint8` | coded state or bit mask | Tag detection and pose-fit state for this frame. |
| `derived/sensors_est/<clip_id>_est.h5/tags/tag_corners_px` | `float64` | px | Four detected tag corners in image pixel coordinates. |
| `derived/sensors_est/<clip_id>_est.h5/tags/tag_edge_px` | `float64` | px | Detected tag edge length in image pixels. |
| `derived/sensors_est/<clip_id>_est.h5/tags/tag_id` | `int32` | fiducial tag ID | Detected fiducial tag identifier. |
| `derived/sensors_est/<clip_id>_est.h5/tags/tag_offsets` | `int64` | count or zero-based index | Offsets of tag detections within the flattened corner arrays. |
| `derived/sensors_est/<clip_id>_est.h5/tags/timestamp_fault` | `bool` | boolean | True when a timestamp fails the tag observation timing check. |
| `derived/sensors_est/<clip_id>_est.h5/tags/translation_nominal_m` | `float64` | nominal meters | Estimated optical cap translation at nominal scale in metres. |
| `derived/sensors_est/<clip_id>_est.h5/tags/used_face_mask` | `uint8` | coded state or bit mask | Bit mask of tag faces included in the pose fit. |
| `derived/sensors_est/<clip_id>_est.h5/tier` | `object` | categorical text | Frozen signal usability grade, not task ground truth. |
| `derived/wrist_poses_est/<clip_id>_est.h5/ambiguity_margin_px` | `float64` | pixel | Ambiguity margin px in image pixels. |
| `derived/wrist_poses_est/<clip_id>_est.h5/cap_ids` | `int16` | fiducial tag ID | Detected optical cap tag identifiers, not people identifiers. |
| `derived/wrist_poses_est/<clip_id>_est.h5/claimed_cap_id_side` | `object` | categorical text | Side claimed by the upstream cap ID mapping before independent checks. |
| `derived/wrist_poses_est/<clip_id>_est.h5/identity_arbitration_reason` | `object` | categorical text | Reason for the final physical-side identity decision. |
| `derived/wrist_poses_est/<clip_id>_est.h5/identity_contradiction` | `bool` | boolean | True when independent side evidence contradicts a claimed identity. |
| `derived/wrist_poses_est/<clip_id>_est.h5/identity_status` | `object` | categorical text | VERIFIED, BY_EXCLUSION, WEAK or UNVERIFIED physical-side decision. |
| `derived/wrist_poses_est/<clip_id>_est.h5/image_band_boundary_invalid` | `bool` | boolean | True near a discontinuity in image-to-band clock alignment. |
| `derived/wrist_poses_est/<clip_id>_est.h5/image_band_lag_ci95_ms` | `float64` | ms | Image band lag ci95 ms in milliseconds. |
| `derived/wrist_poses_est/<clip_id>_est.h5/image_band_lag_ms` | `float64` | ms | Image band lag ms in milliseconds. |
| `derived/wrist_poses_est/<clip_id>_est.h5/image_band_timing_segment_id` | `int64` | count or zero-based index | Index of the local image-to-band timing interval. |
| `derived/wrist_poses_est/<clip_id>_est.h5/image_band_timing_state` | `object` | categorical text | ON_TIME or UNKNOWN result of the image-to-band timing check. |
| `derived/wrist_poses_est/<clip_id>_est.h5/ippe_physical_valid_est` | `bool` | boolean | Estimated IPPE pose passes the physical geometry checks. |
| `derived/wrist_poses_est/<clip_id>_est.h5/ippe_rmse_px_est` | `float64` | pixel | Reprojection root-mean-square error of the IPPE fit in pixels. |
| `derived/wrist_poses_est/<clip_id>_est.h5/ippe_rvec_est` | `float64` | radian rotation vector | Estimated IPPE rotation vector for the cap. |
| `derived/wrist_poses_est/<clip_id>_est.h5/ippe_translation_nominal_m_est` | `float64` | nominal meters | Estimated IPPE translation in metres at nominal tag scale. |
| `derived/wrist_poses_est/<clip_id>_est.h5/log_time_ns` | `int64` | ns | Log time ns in nanoseconds. |
| `derived/wrist_poses_est/<clip_id>_est.h5/measured_physical_side` | `object` | categorical text | Physical wrist side inferred from independent image evidence. |
| `derived/wrist_poses_est/<clip_id>_est.h5/metadata_json` | `object` | structured metadata or text | Method settings and source descriptions serialized as JSON. |
| `derived/wrist_poses_est/<clip_id>_est.h5/odom_head_boundary_invalid` | `bool` | boolean | True near a discontinuity in odometry-to-head timing. |
| `derived/wrist_poses_est/<clip_id>_est.h5/odom_head_lag_ci95_ms` | `float64` | ms | Odom head lag ci95 ms in milliseconds. |
| `derived/wrist_poses_est/<clip_id>_est.h5/odom_head_lag_ms` | `float64` | ms | Odom head lag ms in milliseconds. |
| `derived/wrist_poses_est/<clip_id>_est.h5/odom_head_timing_segment_id` | `int64` | count or zero-based index | Index of the local odometry-to-head timing interval. |
| `derived/wrist_poses_est/<clip_id>_est.h5/odom_head_timing_state` | `object` | categorical text | ON_TIME or UNKNOWN result of the odometry-to-head timing check. |
| `derived/wrist_poses_est/<clip_id>_est.h5/optical_from_cap_quat_xyzw_est` | `float64` | unit quaternion xyzw | Estimated cap orientation in optical-camera coordinates, quaternion x/y/z/w. |
| `derived/wrist_poses_est/<clip_id>_est.h5/optical_from_cap_translation_m_est` | `float64` | nominal meters | Estimated cap position in optical-camera coordinates, metres. |
| `derived/wrist_poses_est/<clip_id>_est.h5/paired_emg_pose_valid` | `bool` | boolean | True only for a cap pose paired with a valid EMG quality interval and verified side. |
| `derived/wrist_poses_est/<clip_id>_est.h5/physical_side` | `object` | categorical text | Final left or right side assigned to this cap observation. |
| `derived/wrist_poses_est/<clip_id>_est.h5/pose_status` | `object` | categorical text | Automatic optical cap pose status; validity is tracked separately. |
| `derived/wrist_poses_est/<clip_id>_est.h5/raw_tag_state` | `uint8` | coded state or bit mask | Detection state before timing and identity filtering. |
| `derived/wrist_poses_est/<clip_id>_est.h5/schema_version` | `int64` | schema version number | Extraction schema version stored as an HDF5 root attribute; value 1.0.0. |
| `derived/wrist_poses_est/<clip_id>_est.h5/source_etag` | `object` | identifier or ETag text | ETag from the vendor raw source object; multipart ETags are not SHA256. |
| `derived/wrist_poses_est/<clip_id>_est.h5/source_key` | `object` | identifier or ETag text | Original vendor storage key for raw-copy provenance; not a release download path. |
| `derived/wrist_poses_est/<clip_id>_est.h5/stamp_ns` | `int64` | ns | Stamp ns in nanoseconds. |
| `derived/wrist_poses_est/<clip_id>_est.h5/su_margin_screened_2px` | `bool` | boolean | Single-face pose survived a two-pixel margin screen; still unverified. |
| `derived/wrist_poses_est/<clip_id>_est.h5/upstream_identity_status` | `object` | categorical text | Identity status inherited from the earlier pose-processing stage. |
| `derived/wrist_poses_est/<clip_id>_est.h5/upstream_physical_side` | `object` | categorical text | Side proposed by the earlier pose-processing stage. |
| `derived/wrist_poses_est/<clip_id>_est.h5/upstream_verified_band_serial` | `object` | identifier or ETag text | Band serial proposed by the earlier identity stage. |
| `derived/wrist_poses_est/<clip_id>_est.h5/verified_band_serial` | `object` | identifier or ETag text | Band serial matched by the final side-identity check. |
| `derived/wrist_poses_est/<clip_id>_est.h5/world_from_cap_quat_xyzw_est` | `float64` | unit quaternion xyzw | Estimated cap orientation in odometry world coordinates, quaternion x/y/z/w. |
| `derived/wrist_poses_est/<clip_id>_est.h5/world_from_cap_translation_m_est` | `float64` | nominal meters | Estimated cap position in odometry world coordinates, metres. |
| `derived/wrist_poses_est/<clip_id>_est.h5/world_odom_jump` | `bool` | boolean | True where an odometry discontinuity invalidates the world pose. |
| `derived/wrist_poses_est/<clip_id>_est.h5/world_segment_id` | `int64` | count or zero-based index | Index of the continuous world-odometry segment. |
| `derived/wrist_poses_est/<clip_id>_est.h5/world_transform_valid` | `bool` | boolean | True when a valid transform from cap to world is available. |
