# Automatic wrist-cap pose targets

The targets are optical tag-cap observations at nominal scale, not anatomical wrists or human-verified ground truth. A cap is the physical tag rig attached near a wrist. The `paired_emg_pose_valid` mask requires verified physical-side identity, a locally acceptable image-to-band timing state, no boundary invalidation and a GOLD or STANDARD EMG quality interval. Valid runs are fragmented; `derived/wrist_poses_est/fragmentation.json` gives run lengths. `pose_validated` is false.

The table below sums paired cap-frame counts and divides by twice the indexed pose-frame count because each frame has two potential wrist-cap observations. This is an approximate per-wrist observation density, not pose accuracy or an exact fraction of EMG samples. `tools/pose_coverage.py` recomputes it.

| Primary partition | Clip tier | Paired cap-frame count | Pose frames | Wrist-frame opportunity ratio |
| --- | --- | ---: | ---: | ---: |
| test | EXTENDED | 4051 | 1132109 | 0.179% |
| test | GOLD | 81812 | 3152791 | 1.297% |
| test | NONE | 1569 | 346976 | 0.226% |
| test | STANDARD | 12444 | 1354798 | 0.459% |
| train | EXTENDED | 22043 | 2737540 | 0.403% |
| train | GOLD | 632143 | 12563657 | 2.516% |
| train | NONE | 35188 | 5563733 | 0.316% |
| train | STANDARD | 411900 | 9213726 | 2.235% |
| val | EXTENDED | 26563 | 766549 | 1.733% |
| val | GOLD | 168282 | 2772846 | 3.034% |
| val | NONE | 2102 | 1105115 | 0.095% |
| val | STANDARD | 98387 | 1745137 | 2.819% |
