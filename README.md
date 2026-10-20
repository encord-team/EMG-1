# EMG-1: Electromyography and Egocentric Video for Hand Movement Research

EMG-1 is an open dataset collection from Encord Data Labs, pairing wrist electromyography (EMG) with video and
motion data from human hand movements and manipulation tasks.

Cameras can tell us where a hand is, but they cannot always capture how it moves. Hands become occluded, objects
obscure movement, and visual tracking can fail during complex manipulation. EMG measures the electrical activity
of muscles, providing an additional signal that can help researchers understand hand movements beyond what is
visible.

EMG-1 contains two complementary datasets: a large-scale collection of real-world recordings using 3-channel wrist
EMG, and a smaller, controlled 8-channel dataset with optical motion-capture ground truth.

Both are released to support research into hand-pose estimation, multimodal learning, human movement
understanding and learning from human demonstrations.

## Datasets

| | EMG-1 3-channel | EMG-1 8-channel |
| --- | --- | --- |
| Focus | Large-scale real-world recordings | Controlled recordings with motion-capture ground truth |
| EMG channels | 3 | 8 |
| Duration | 397 clip-hours, including 271.8 hours of good-quality both-wrist EMG | 15 hours |
| Recordings | 4,916 clips | 920 takes |
| Participants | See dataset documentation | 12 |
| Data size | 313.6 GB extracted; 43.2 TB raw | 217 GB complete |
| Version | v1.0.1 | v1.0.1 |

## 1. EMG-1 3-channel: Real-world hand movements at scale

The 3-channel dataset contains recordings of people performing real-world tasks, with wrist EMG synchronized to
egocentric video and additional sensor measurements.

The release comprises 4,916 clips totaling 397 hours of recordings. Of these, 271.8 hours contain good-quality
EMG signals from both wrists.

The dataset provides a large and varied collection for studying muscle activity during natural manipulation,
including movements that can be difficult to recover reliably from video alone.

Release contents:

* 4,916 clips
* 397 total clip-hours
* 271.8 hours of good-quality both-wrist EMG
* 313.6 GB of extracted data across 44,417 files
* 43.2 TB of raw MCAP recordings containing video and sensor streams

Dataset location: `s3://emg1-3ch-ego-release/v1.0.1/`

See the dataset's [README.md](docs/3ch-ego-v1.0.1/README.md) for the full recording format, directory structure
and sensor details, and [`index/3ch-ego/`](index/3ch-ego/) for the listing of every file in the bucket.

## 2. EMG-1 8-channel: Hand movements with motion-capture ground truth

The 8-channel dataset contains synchronized EMG and optical motion-capture recordings from 12 participants.

Unlike the larger 3-channel collection, this dataset was recorded in a controlled environment with independently
measured hand motion. It supports research into the relationship between muscle activity and hand pose,
including evaluation of EMG-based pose prediction methods.

Release contents:

* 920 recorded takes
* 12 participants
* 15 hours of recordings
* 217 GB of complete data, including 181 GB of video
* 35 GB of data excluding video
* Additional Wearable Devices hand-pose predictions (187 MB)

Dataset location: `s3://emg1-8ch-mocap-release/v1.0.1/`

The Wearable Devices prediction supplement is available at `supplements/wd-fusion-predictions/v1/`.

See [BUCKET_README.md](docs/8ch-mocap-v1.0.1/BUCKET_README.md) for the full recording format, directory
structure and sensor details, and [`index/8ch-mocap/`](index/8ch-mocap/) for the listing of every file in the bucket.

## Accessing the data

The datasets are distributed separately from this GitHub repository due to their size.

Each release includes documentation and file manifests to help users identify, download and verify the files
they need.

Files are provided in their original release structure, including:

* `README.md` / `BUCKET_README.md` — Dataset-specific documentation
* `MANIFEST.parquet` — File manifest
* `SHA256SUMS` — SHA-256 checksums for file integrity verification

Users should consult the documentation accompanying each dataset before loading or processing the recordings.

This repository holds what you need to find and fetch them:

* [`USAGE.md`](USAGE.md) — the public download URLs and how to pull a subset of either dataset with one command
* [`scripts/`](scripts/) — the download and listing scripts
* [`index/`](index/) — a listing of every file in each bucket, so nothing has to be crawled
* [`docs/`](docs/) — each release's documentation, and a short guide per dataset

## License

EMG-1 is owned by Encord and released under two licenses, assigned by file type.

| What | License | Text |
| --- | --- | --- |
| Code: every `*.py` file and every `requirements*.txt` file, in this repository and in the releases, plus this repository's `pyproject.toml`, `uv.lock` and `.python-version` | Apache License 2.0 (`Apache-2.0`) | [`LICENSE`](LICENSE), [`NOTICE`](NOTICE) |
| Everything else: the recordings and all other dataset files, the prediction supplement, and in this repository the documentation (`README.md`, `USAGE.md`, `CHANGELOG.md`, `docs/`), the file indexes (`index/`) and `tools/README.md` | Creative Commons Attribution 4.0 International (`CC-BY-4.0`) | [`LICENSE-DATA`](LICENSE-DATA) |

Copyright 2026 Encord. `pyproject.toml`, `uv.lock` and `.python-version` are build configuration for the scripts and
are treated as code. Third-party packages installed as dependencies (for example `pyarrow`) keep their own licenses.

The folders `docs/3ch-ego-v1.0.1/`, `docs/8ch-mocap-v1.0.1/` and `docs/8ch-mocap-supplement-wd-fusion-v1/` are
byte-for-byte copies of files in the releases and are not edited here. Where they differ from this section, this
section takes precedence; the release files will be corrected in the next release of each. In particular, the
supplement v1 `LICENSE` and `README.md` name Wearable Devices Ltd. as rights holder of the files in
`fusion_delivery_v10/` and ask for a credit line naming Wearable Devices Ltd. Both statements are superseded:
Wearable Devices Ltd. produced those files for Encord, Encord owns the whole supplement, and it is licensed CC BY 4.0
like the rest of EMG-1. Likewise, the 8-channel v1.0.1 `LICENSE` reads "Rights holder: Encord"; the intended notice
is "Copyright 2026 Encord", as in the 3-channel `LICENSE`.

## Citation

If you use EMG-1 in your research, please credit the relevant dataset:

> EMG-1 3-channel dataset, Vineeth Velmurugan, Encord, 2026, CC BY 4.0.
>
> EMG-1 8-channel dataset, Vineeth Velmurugan, Encord, 2026, CC BY 4.0.

and, if you use the prediction supplement:

> EMG-1 fusion hand-pose predictions, Encord, 2026, CC BY 4.0.

## About

EMG-1 is released by Encord Data Labs, the research division of Encord.

