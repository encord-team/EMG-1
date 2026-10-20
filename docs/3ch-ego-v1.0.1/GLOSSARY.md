# Glossary

- **Clip:** One vendor recording chunk, usually about five minutes.
- **Station:** Recording kit; it does not identify a worker.
- **Station-day:** All clips from one kit on one date, the primary split unit.
- **Quality segment:** Half-open interval assigned a signal tier on the frozen quality clock.
- **Band:** Wrist-worn Mudra Pro device.
- **Cap:** Optical tag rig observed on a wrist, not an anatomical wrist position.
- **MCAP log time:** Recorder timestamp on a message, used for video lookup.
- **Header stamp:** Time carried inside a camera message; it can slip.
- **Vendor segment:** Unverified task title and description from a vendor sidecar.
- **L0:** Original MCAP archive. **L1:** Extracted sensor layer.

- **Frozen:** The release uses fixed, published rule thresholds.
- **Rail fraction:** Share of EMG samples at or near the signal range limit.
- **QC:** Signal quality control based on observed samples and clocks.
- **Failing band:** The known degraded left band at the held-out station; 0.71 of 54.92 band-hours are still GOLD under the segment rule.
- **Tier:** GOLD, STANDARD, EXTENDED or NONE signal-usability grade.
- **ON_TIME/UNKNOWN:** Pose timing state judged aligned or not established by the automatic image-to-band check.
- **MULTI_FACE:** Automatic cap-pose detection state using several visible tag faces.
- **Dropouts:** Lost or delayed sensor packages or samples; inspect affected duration, not only a clip flag.
- **ETag:** Object storage identity token. A multipart ETag combines part MD5 values and is not a SHA256 file digest.
- **Range read:** A request for a bounded byte interval of a raw MCAP object.
- **CC BY 4.0:** Creative Commons Attribution 4.0 International, the licence of the data; source code (every `.py` file and `requirements*.txt`) is under Apache-2.0.
- **Base URL:** Public HTTPS address of the release bucket, given in the bucket-root `README.md` and passed to `tools/download.py`.
- **SHA256SUMS:** Per-file digest list for verifying downloaded release files.
- **MANIFEST.parquet:** Table of release keys, byte sizes and SHA256 digests.
- **Release key:** Object path below the bucket, including the `v1.0.1/` prefix for raw destination objects.
- **MF / SU:** Multi-face pose estimate / screened single-face estimate.
- **IPPE:** Infinitesimal plane-based pose estimation from planar tag corners.

- **SLIPPED:** A camera header timestamp jumps relative to the recorder host clock; use the timing validity mask rather than treating it as exposure time. This flag occurs on egox-005 and egox-013 clips.
