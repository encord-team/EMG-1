# Schema v1.0.0

HDF5 is authoritative. Raw vendor marker order, observations and repairs remain beside the canonical R1 representation. No human labels ship. No depth was recorded.

Each host clock is an exact int64 nanosecond offset within its published clock epoch. Cross-epoch placement and uncertainty appear in clock_epochs.json and the index. Source float64 camera stamps retain their original spacing. No-frame trailer stamps are zero and require has_frame. Raw band stamps are unchanged by the lag alignment option in the loader.

Canonical markers use T/I/M/R/P 1..4 plus WR/RAD/ULN. R1 fixes OP-002 base/knuckle reversal, frozen take-level T34 tip/DIP swaps, and masks flagged per-frame test failures. C3D frames begin at markers/c3d_t_ns[0]; use the HDF5 grid for absolute epoch placement. Marker canonical values are observed-source identity repairs; vendor gap filling remains separately available in markers/repaired.

The derived files and derived groups are automatic, with validated=false. Contact_est is 1 for <20 mm, 0 for >30 mm, and -1 for the margin or missing. Camera sensor bytes remain raw_undecoded. IMU convenience arrays retain vendor raw units for three acceleration and three gyro components; physical scaling remains unverified; calibration and raw source attributes preserve the acquisition configuration.

The following catalog enumerates every dataset path present across all takes and derived files. N is variable by take. SCHEMA.json includes all observed dataset attributes.

| Container | Dataset | Dtype | Unit | Nominal Hz | Clock |
|---|---|---|---|---|---|
| take | /calibration/camera/factory | object | UTF-8 metadata; JSON where specified | None | none |
| take | /calibration/camera/svo_header | object | UTF-8 metadata; JSON where specified | None | none |
| take | /calibration/mocap/properties | object | UTF-8 metadata; JSON where specified | None | none |
| take | /camera/container_records | object | UTF-8 metadata; JSON where specified | None | none |
| take | /camera/decoding_status | object | UTF-8 metadata; JSON where specified | None | none |
| take | /camera/integrated_sensors/device_t_ns | int64 | ns | None | subject_relative_UTC, camera anchor; source precision retained |
| take | /camera/integrated_sensors/messages | object | UTF-8 metadata; JSON where specified | None | none |
| take | /camera/integrated_sensors/raw_payload | uint8 | source raw units; no physical scaling inferred | None | none |
| take | /camera/sensors/device_t_ns | int64 | ns | None | subject_relative_UTC, camera anchor; source precision retained |
| take | /camera/sensors/messages | object | UTF-8 metadata; JSON where specified | None | none |
| take | /camera/sensors/raw_payload | uint8 | source raw units; no physical scaling inferred | None | none |
| take | /camera/side_by_side/messages | object | UTF-8 metadata; JSON where specified | None | none |
| take | /camera/svo_footer/messages | object | UTF-8 metadata; JSON where specified | None | none |
| take | /camera/svo_header/messages | object | UTF-8 metadata; JSON where specified | None | none |
| take | /derived/band_mocap_lag_est | object | UTF-8 metadata; JSON where specified | None | none |
| take | /derived/decision_intervals_est | object | UTF-8 metadata; JSON where specified | None | none |
| take | /derived/gaps_est/emg | int64 | columns: start_t_ns,end_t_ns,interval_ns (ns), estimated_missing_samples (count) | None | host_perf_epoch for start/end; interval and count columns |
| take | /derived/gaps_est/imu | int64 | columns: start_t_ns,end_t_ns,interval_ns (ns), estimated_missing_samples (count) | None | host_perf_epoch for start/end; interval and count columns |
| take | /derived/gaps_est/markers | int64 | columns: start_t_ns,end_t_ns,interval_ns (ns), estimated_missing_samples (count) | None | host_perf_epoch for start/end; interval and count columns |
| take | /derived/gaps_est/ppg | int64 | columns: start_t_ns,end_t_ns,interval_ns (ns), estimated_missing_samples (count) | None | host_perf_epoch for start/end; interval and count columns |
| take | /derived/gaps_est/video | int64 | columns: start_t_ns,end_t_ns,interval_ns (ns), estimated_missing_samples (count) | None | host_perf_epoch for start/end; interval and count columns |
| take | /derived/lag_input_provenance_est | object | UTF-8 metadata; JSON where specified | None | none |
| take | /derived/proximity_est/index/contact_est | int8 | source raw units; no physical scaling inferred | None | none |
| take | /derived/proximity_est/index/distance_m | float64 | m | None | none |
| take | /derived/proximity_est/index/within_20mm | bool | bool | None | none |
| take | /derived/proximity_est/index/within_30mm | bool | bool | None | none |
| take | /derived/proximity_est/middle/contact_est | int8 | source raw units; no physical scaling inferred | None | none |
| take | /derived/proximity_est/middle/distance_m | float64 | m | None | none |
| take | /derived/proximity_est/middle/within_20mm | bool | bool | None | none |
| take | /derived/proximity_est/middle/within_30mm | bool | bool | None | none |
| take | /derived/proximity_est/pinky/contact_est | int8 | source raw units; no physical scaling inferred | None | none |
| take | /derived/proximity_est/pinky/distance_m | float64 | m | None | none |
| take | /derived/proximity_est/pinky/within_20mm | bool | bool | None | none |
| take | /derived/proximity_est/pinky/within_30mm | bool | bool | None | none |
| take | /derived/proximity_est/ring/contact_est | int8 | source raw units; no physical scaling inferred | None | none |
| take | /derived/proximity_est/ring/distance_m | float64 | m | None | none |
| take | /derived/proximity_est/ring/within_20mm | bool | bool | None | none |
| take | /derived/proximity_est/ring/within_30mm | bool | bool | None | none |
| take | /derived/qc_est | object | UTF-8 metadata; JSON where specified | None | none |
| take | /derived/timing_est/emg | object | UTF-8 metadata; JSON where specified | None | none |
| take | /derived/timing_est/imu | object | UTF-8 metadata; JSON where specified | None | none |
| take | /derived/timing_est/markers | object | UTF-8 metadata; JSON where specified | None | none |
| take | /derived/timing_est/ppg | object | UTF-8 metadata; JSON where specified | None | none |
| take | /derived/timing_est/video | object | UTF-8 metadata; JSON where specified | None | none |
| take | /emg/data | float32 | ADC counts / 2^23 | 2000.0 | none |
| take | /emg/finite | bool | bool | 2000.0 | none |
| take | /emg/t_ns | int64 | ns | 2000.0 | host_perf_epoch, exact int64 ns offsets |
| take | /imu/accel_valid | bool | bool | per-take manifest nominal_fs_hz; see timing_est | none |
| take | /imu/data | float32 | vendor raw acceleration xyz and gyro xyz; physical scaling unverified | per-take manifest nominal_fs_hz; see timing_est | none |
| take | /imu/finite | bool | bool | per-take manifest nominal_fs_hz; see timing_est | none |
| take | /imu/gyro_valid | bool | bool | per-take manifest nominal_fs_hz; see timing_est | none |
| take | /imu/t_ns | int64 | ns | per-take manifest nominal_fs_hz; see timing_est | host_perf_epoch, exact int64 ns offsets |
| take | /markers/anatomical_mapping_status | object | UTF-8 metadata; JSON where specified | 120.0 | none |
| take | /markers/c3d_source_row | int64 | source raw units; no physical scaling inferred | 120.0 | none |
| take | /markers/c3d_t_ns | int64 | ns | 120.0 | host_perf_epoch, exact int64 ns offsets |
| take | /markers/canonical | float32 | m | 120.0 | none |
| take | /markers/canonical_aliases | object | UTF-8 metadata; JSON where specified | 120.0 | none |
| take | /markers/canonical_labels | object | UTF-8 metadata; JSON where specified | 120.0 | none |
| take | /markers/canonical_valid | bool | bool | 120.0 | none |
| take | /markers/changed_without_vendor_label | bool | bool | 120.0 | none |
| take | /markers/frame_number | int64 | source raw units; no physical scaling inferred | 120.0 | none |
| take | /markers/identity_mask | bool | bool | 120.0 | none |
| take | /markers/labels | object | UTF-8 metadata; JSON where specified | 120.0 | none |
| take | /markers/marker_fixes_applied | object | UTF-8 metadata; JSON where specified | 120.0 | none |
| take | /markers/missing | bool | bool | 120.0 | none |
| take | /markers/observed | float32 | m | 120.0 | none |
| take | /markers/repair_provenance | object | UTF-8 metadata; JSON where specified | 120.0 | none |
| take | /markers/repaired | float32 | m | 120.0 | none |
| take | /markers/repaired_missing | bool | bool | 120.0 | none |
| take | /markers/status | uint8 | source raw units; no physical scaling inferred | 120.0 | none |
| take | /markers/t_ns | int64 | ns | 120.0 | host_perf_epoch, exact int64 ns offsets |
| take | /meta/omissions | object | UTF-8 metadata; JSON where specified | None | none |
| take | /meta/summary | object | UTF-8 metadata; JSON where specified | None | none |
| take | /ppg/data | float32 | vendor raw PPG counts; two components | per-take manifest nominal_fs_hz; see timing_est | none |
| take | /ppg/finite | bool | bool | per-take manifest nominal_fs_hz; see timing_est | none |
| take | /ppg/t_ns | int64 | ns | per-take manifest nominal_fs_hz; see timing_est | host_perf_epoch, exact int64 ns offsets |
| take | /source/session/scenario.yaml | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/session/session.index.json | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/session/session.log | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-001_Left.motive | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-001_Left.motive_parsed | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/take/decision.json | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/take/manifest.json | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/take/markers/session.h5/markers/frame_number | int64 | source raw units; no physical scaling inferred | 120.0 | none |
| take | /source/take/markers/session.h5/markers/labels | object | UTF-8 metadata; JSON where specified | 120.0 | none |
| take | /source/take/markers/session.h5/markers/perf_ns | int64 | ns | 120.0 | host_perf_epoch, exact int64 ns offsets |
| take | /source/take/markers/session.h5/markers/xyz | float32 | source raw units; no physical scaling inferred | 120.0 | none |
| take | /source/take/sensors/session.h5/bands/band1/emg | float32 | source raw units; no physical scaling inferred | 2000.0 | none |
| take | /source/take/sensors/session.h5/bands/band1/emg_perf_ns | int64 | ns | 2000.0 | host_perf_epoch, exact int64 ns offsets |
| take | /source/take/sensors/session.h5/bands/band1/imu_hand | float32 | source raw units; no physical scaling inferred | per-take manifest nominal_fs_hz; see timing_est | none |
| take | /source/take/sensors/session.h5/bands/band1/imu_hand_perf_ns | int64 | ns | per-take manifest nominal_fs_hz; see timing_est | host_perf_epoch, exact int64 ns offsets |
| take | /source/take/sensors/session.h5/bands/band1/ppg | float32 | source raw units; no physical scaling inferred | per-take manifest nominal_fs_hz; see timing_est | none |
| take | /source/take/sensors/session.h5/bands/band1/ppg_perf_ns | int64 | ns | per-take manifest nominal_fs_hz; see timing_est | host_perf_epoch, exact int64 ns offsets |
| take | /source/take/video/session.h5/video/cam1/device_timestamp_ns | float64 | ns | None | subject_relative_UTC, camera anchor; source precision retained |
| take | /source/take/video/session.h5/video/cam1/frame_index | int64 | source raw units; no physical scaling inferred | None | none |
| take | /source/take/video/session.h5/video/cam1/perf_ns | int64 | ns | None | host_perf_epoch, exact int64 ns offsets |
| take | /video/access_unit_row | int64 | source raw units; no physical scaling inferred | 60.0 | none |
| take | /video/device_timestamp_ns | float64 | ns | 60.0 | subject_relative_UTC, camera anchor; source precision retained |
| take | /video/frame_index | int64 | source raw units; no physical scaling inferred | 60.0 | none |
| take | /video/has_frame | bool | bool | 60.0 | none |
| take | /video/keyframe | bool | bool | 60.0 | none |
| take | /video/mcap_byte_length | int64 | byte | 60.0 | none |
| take | /video/mcap_byte_offset | int64 | byte | 60.0 | none |
| take | /video/mcap_file | object | UTF-8 metadata; JSON where specified | 60.0 | none |
| take | /video/sha256 | object | UTF-8 metadata; JSON where specified | 60.0 | none |
| take | /video/t_ns | int64 | ns | 60.0 | host_perf_epoch, exact int64 ns offsets |
| take | /video/trailer | uint8 | byte | 60.0 | none |
| take | /video/trailer_device_timestamp_ns | int64 | ns | 60.0 | subject_relative_UTC, camera anchor; source precision retained |
| take | /video/wrapper | uint8 | byte | 60.0 | none |
| derived | /band_mocap_lag_est | object | UTF-8 metadata; JSON where specified | None | none |
| derived | /decision_intervals_est | object | UTF-8 metadata; JSON where specified | None | none |
| derived | /gaps_est/emg | int64 | columns: start_t_ns,end_t_ns,interval_ns (ns), estimated_missing_samples (count) | None | host_perf_epoch for start/end; interval and count columns |
| derived | /gaps_est/imu | int64 | columns: start_t_ns,end_t_ns,interval_ns (ns), estimated_missing_samples (count) | None | host_perf_epoch for start/end; interval and count columns |
| derived | /gaps_est/markers | int64 | columns: start_t_ns,end_t_ns,interval_ns (ns), estimated_missing_samples (count) | None | host_perf_epoch for start/end; interval and count columns |
| derived | /gaps_est/ppg | int64 | columns: start_t_ns,end_t_ns,interval_ns (ns), estimated_missing_samples (count) | None | host_perf_epoch for start/end; interval and count columns |
| derived | /gaps_est/video | int64 | columns: start_t_ns,end_t_ns,interval_ns (ns), estimated_missing_samples (count) | None | host_perf_epoch for start/end; interval and count columns |
| derived | /lag_input_provenance_est | object | UTF-8 metadata; JSON where specified | None | none |
| derived | /mediapipe_stereo_est/camera_keypoints_est | float64 | m | 60.0 | none |
| derived | /mediapipe_stereo_est/camera_keypoints_gated_est | float64 | m | 60.0 | none |
| derived | /mediapipe_stereo_est/digit_valid_est | bool | bool | 60.0 | none |
| derived | /mediapipe_stereo_est/eye_detection_selection_est | int64 | index | 60.0 | none |
| derived | /mediapipe_stereo_est/identity_reason_est | object | text | 60.0 | none |
| derived | /mediapipe_stereo_est/keypoint_names_est | object | UTF-8 metadata; JSON where specified | 60.0 | none |
| derived | /mediapipe_stereo_est/keypoints_est | float64 | m | 60.0 | none |
| derived | /mediapipe_stereo_est/provenance_est | object | UTF-8 metadata; JSON where specified | 60.0 | none |
| derived | /mediapipe_stereo_est/reprojection_error_est | float64 | pixel | 60.0 | none |
| derived | /mediapipe_stereo_est/stereo_side_error_est | float64 | mm | 60.0 | none |
| derived | /mediapipe_stereo_est/stereo_valid_est | bool | bool | 60.0 | none |
| derived | /mediapipe_stereo_est/t_ns_est | int64 | ns | 60.0 | host_perf_epoch, exact int64 ns offsets |
| derived | /mediapipe_stereo_est/valid_est | bool | bool | 60.0 | none |
| derived | /mediapipe_stereo_est/video_row_est | int64 | index | 60.0 | none |
| derived | /proximity_est/index/contact_est | int8 | source raw units; no physical scaling inferred | None | none |
| derived | /proximity_est/index/distance_m | float64 | m | None | none |
| derived | /proximity_est/index/within_20mm | bool | bool | None | none |
| derived | /proximity_est/index/within_30mm | bool | bool | None | none |
| derived | /proximity_est/middle/contact_est | int8 | source raw units; no physical scaling inferred | None | none |
| derived | /proximity_est/middle/distance_m | float64 | m | None | none |
| derived | /proximity_est/middle/within_20mm | bool | bool | None | none |
| derived | /proximity_est/middle/within_30mm | bool | bool | None | none |
| derived | /proximity_est/pinky/contact_est | int8 | source raw units; no physical scaling inferred | None | none |
| derived | /proximity_est/pinky/distance_m | float64 | m | None | none |
| derived | /proximity_est/pinky/within_20mm | bool | bool | None | none |
| derived | /proximity_est/pinky/within_30mm | bool | bool | None | none |
| derived | /proximity_est/ring/contact_est | int8 | source raw units; no physical scaling inferred | None | none |
| derived | /proximity_est/ring/distance_m | float64 | m | None | none |
| derived | /proximity_est/ring/within_20mm | bool | bool | None | none |
| derived | /proximity_est/ring/within_30mm | bool | bool | None | none |
| derived | /qc_est | object | UTF-8 metadata; JSON where specified | None | none |
| derived | /timing_est/emg | object | UTF-8 metadata; JSON where specified | None | none |
| derived | /timing_est/imu | object | UTF-8 metadata; JSON where specified | None | none |
| derived | /timing_est/markers | object | UTF-8 metadata; JSON where specified | None | none |
| derived | /timing_est/ppg | object | UTF-8 metadata; JSON where specified | None | none |
| derived | /timing_est/video | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/take/markers/repairs.json | object | UTF-8 metadata; JSON where specified | 120.0 | none |
| take | /source/take/markers/session_repaired.h5/markers/frame_number | int64 | source raw units; no physical scaling inferred | 120.0 | none |
| take | /source/take/markers/session_repaired.h5/markers/labels | object | UTF-8 metadata; JSON where specified | 120.0 | none |
| take | /source/take/markers/session_repaired.h5/markers/perf_ns | int64 | ns | 120.0 | host_perf_epoch, exact int64 ns offsets |
| take | /source/take/markers/session_repaired.h5/markers/xyz | float32 | source raw units; no physical scaling inferred | 120.0 | none |
| take | /calibration/mocap/properties_attributes | object | UTF-8 metadata; JSON where specified | None | none |
| take | /calibration/mocap/properties_1 | object | UTF-8 metadata; JSON where specified | None | none |
| take | /calibration/mocap/properties_1_attributes | object | UTF-8 metadata; JSON where specified | None | none |
| take | /camera/source_segments | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-002_Left.motive | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-002_Left.motive_parsed | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/take/session_notes.json | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-003_Left.motive | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-003_Left.motive_parsed | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-004_Left.motive | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-004_Left.motive_parsed | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-005_Left.motive | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-005_Left.motive_parsed | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/take/changes.json | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-006_Left.motive | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-006_Left.motive_parsed | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-007_Left.motive | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-007_Left.motive_parsed | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-008_Left.motive | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-008_Left.motive_parsed | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-009_Left.motive | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-009_Left.motive_parsed | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-010_Left.motive | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-010_Left.motive_parsed | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-011_Left.motive | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-011_Left.motive_parsed | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-012_Left.motive | object | UTF-8 metadata; JSON where specified | None | none |
| take | /source/subject/OP-012_Left.motive_parsed | object | UTF-8 metadata; JSON where specified | None | none |
