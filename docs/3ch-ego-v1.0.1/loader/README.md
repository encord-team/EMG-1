# Python loader for v1.0.1

`requirements.txt` is the tested CPU quickstart environment. `requirements-core.txt` omits PyTorch for NumPy-only loading, and `requirements-video.txt` adds MCAP and boto3 helpers. Install `requirements.txt`, then run `python -B loader/example.py ROOT --starter` and `python -B -m unittest discover -s tests`. Add `loader/` to `PYTHONPATH` when importing from another directory. The starter requires its clip sidecars under `vendor/`, the index CSVs, split files and taxonomy. A full download needs both `sensors/` and `derived/sensors_est/`.

`EMGWindowDataset(root, split_name='primary', partition='train')` gives fixed-size two-wrist EMG and interpolated band IMU with masks. `available_only=True` drops unavailable windows and prints the count. `split=None, clip_ids=[...]` handles explicit selections, including starter clips. Passing excluded clip IDs with a partition raises an error. `label='vendor_segment'` returns a weak task category and validity mask; the segment clock conversion uses an estimated host anchor. `pose_targets=True` opts into sparse automatic optical-cap targets. PyTorch `num_workers` can parallelize access; close the dataset after use. `iter_clip_windows` yields the same window dictionaries grouped by clip and closes handles automatically.

`video_frame_at` reads encoded frames from local MCAPs or a range callback. The destination listing in `raw/RAW_OBJECTS.csv` is reconciled. `video_frame_at_s3` reads that listing and binds every range request to its destination ETag with `If-Match`; it needs an S3-compatible client. For the public HTTPS release, pass `video_frame_at` a `read_range` callback that sends HTTPS range requests, as shown in `raw/README.md`.

Requires Python 3.12 or 3.13; macOS arm64 prebuilt wheels require macOS 14 or newer. Partition keys are `train`, `val`, and `test`.

`ClipReader(root, clip_id)` opens one clip's L1 sensor and estimated-clock HDF5 files and reuses open handles for repeated windows. `export_frame_tables` reads MCAP indexes to write five frame-time tables without decoding images; it requires a fresh output directory and an indexed raw MCAP.
