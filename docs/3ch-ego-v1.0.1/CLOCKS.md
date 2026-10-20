# Clock fields and limits

| Field | Source | Meaning | Use |
| --- | --- | --- | --- |
| `t_dev` | band payload | device tick | Detect resets and gaps; it is not an absolute time. |
| `t_host_ns` | band payload | recorder host timestamp in ns | Original observation; may have packet timing jitter. |
| `t_ns_est` | derived clock fit | estimated host-aligned ns | Align band and other sensor samples approximately. |
| `qc_t_ns_est` | frozen quality fit | estimated quality clock in ns | Defines the released quality segments. |
| MCAP `log_time` | recorder | message recording time in ns | Used by `video_frame_at`. |
| image header stamp | camera message | camera-provided stamp in ns | Can slip on some stations; do not substitute for log time. |

The whole-clip tier rule checks full-rate band clocks against 2133.33 Hz within 0.5%, caps gaps above 50 ms at STANDARD and above 1000 ms at EXTENDED, and treats p99 host jitter above 33.3 ms or 1000 ms as progressively worse. See `derived/quality/tier_rule.py` for all conditions and interactions. `clock_nonlinear` means the maximum departure of fitted host-clock residual knots from a line through their endpoints exceeds 5 ms in any band stream, as defined in `SCHEMA.json`. These checks establish signal usability, not frame-exposure synchronization. Camera-IMU and odometry source stamps were rounded in extraction. The vendor segment anchor `data.start_ts` is exact for clip-relative vendor milliseconds, while the alignment to host nanoseconds is estimated and can be disputed. The clip ID records UTC time to whole seconds. Against first retimed EMG host time, its p10 and p90 offsets are 0.09 s and 0.873 s over 4,914 clips (`tools/clock_audit.py`). `vendor_segments` flags a 10 s or larger disagreement with that clip-ID anchor or between wrist anchors as `host_anchor_disputed_est`. The shipped audit marks 0 clips disputed. This comparison does not resolve all possible vendor-to-host mapping disagreements; independent raw-clock validation remains pending.

The segment rule instead rejects one-second windows with a step above 0.70 ms, applies a one-second guard to saturated windows, excludes bands with p99 host jitter above 1000 ms and drops runs shorter than 10 s. See `derived/quality/SEGMENT_RULE.txt`.

L1 band arrays retain t_host_ns, t_dev, within-package sample index i, and package sequence. PPG packet timestamps (pkg_t_dev and pkg_t_host_ns), t_mono_ns, and per-sample MCAP log_time are omitted from L1; these recorder fields remain in the original raw MCAPs. Frame and tag log_time fields listed in the schema are separate.
