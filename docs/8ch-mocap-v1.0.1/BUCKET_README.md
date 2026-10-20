# Download and verify EMG-1 8-channel v1.0.1

EMG-1 8-channel v1.0.1 is free and open. Source code files (`*.py` and requirements files) are licensed under Apache-2.0 and every other file under CC BY 4.0; see `LICENSE`, `LICENSE-CODE` and `TERMS.md`. The files are served over HTTPS from a publicly readable bucket, and downloads need no account or credentials.

## Base URL

This tree does not record the download address. The bucket-root README, which sits outside the checksummed `v1.0.1/` prefix, gives the base URL and the SHA-256 digests of `SHA256SUMS` and `MANIFEST.parquet` for this version. Replace `<BASE_URL>` below with that base URL and `<SHA256SUMS_DIGEST>` with the digest it lists, without the version prefix or a trailing slash. `tools/download.py` adds the `v1.0.1/` prefix itself; `--version` selects another one.

## First download, from an empty parent directory

`tools/download.py` ships inside the release, so a first-time user fetches it on its own first. Start in a new, empty parent directory, not inside an existing release folder:

```sh
mkdir emg1 && cd emg1
curl -fsSL -o SHA256SUMS "<BASE_URL>/v1.0.1/SHA256SUMS"
curl -fsSL --create-dirs -o tools/download.py "<BASE_URL>/v1.0.1/tools/download.py"
sha256sum SHA256SUMS
grep '  tools/download.py$' SHA256SUMS | sha256sum -c -
```

The first `sha256sum` must print the `SHA256SUMS` digest given in the bucket-root README, and the second check must print `tools/download.py: OK`. On macOS, use `shasum -a 256` in place of `sha256sum`. Then run the tool once. It creates the release folder `emg1-8ch-v1.0.1` beside the two bootstrap files and downloads the top-level documents, `MANIFEST.parquet`, `SHA256SUMS`, `index/`, `splits/`, `starter/`, `loader/`, `tools/`, `eval/`, `baselines/`, `reference/` and `calibration/`:

```sh
python -B tools/download.py <BASE_URL> ./emg1-8ch-v1.0.1 --sums-sha256 <SHA256SUMS_DIGEST> --exclude 'takes/*' --exclude 'derived/*'
cd emg1-8ch-v1.0.1
```

The release folder holds its own `SHA256SUMS` and `tools/download.py`, so the bootstrap copies in the parent directory can be deleted.

## More data, from inside the release folder

Run the commands below from the release folder, the directory that holds `tools/`, `SHA256SUMS` and `MANIFEST.parquet`, with `.` as the destination. Each command adds files to the same folder, and an interrupted command resumes when run again. Put `<BASE_URL>` and the destination before the options. A file is selected when it matches at least one `--include` pattern (or no `--include` is given) and no `--exclude` pattern. Patterns are shell-style wildcards matched against paths inside the release, such as `takes/OP-001/s003/02/take.h5`, and `*` also matches `/`. `SHA256SUMS` and `MANIFEST.parquet` are always downloaded, and every file is checked against `SHA256SUMS`. Add `--list` to preview a selection without downloading.

Benchmark data: take HDF5 files for T1 and T2, and derived estimates for T3.

```sh
python -B tools/download.py <BASE_URL> . --include 'takes/*/take.h5' --include 'derived/*'
```

Everything except video: all files except the `take.mcap` video containers, including the starter ones.

```sh
python -B tools/download.py <BASE_URL> . --exclude '*.mcap'
```

The complete release, video included:

```sh
python -B tools/download.py <BASE_URL> .
```

| Task | Additional files | Approximate size |
|---|---|---:|
| T1/T2 | `takes/*/take.h5` | 27.24 GB |
| T3 | `derived/*` | 4.81 GB |
| Video | `takes/*/take.mcap` | 181.51 GB |

Native TAK and SVO2 files are not included in v1.0.1.

## Verify

From the release folder, run `python -B tools/verify_download.py . --ignore-missing` on a partial download. It verifies every present path against `SHA256SUMS` and reports absent entries separately. Omit `--ignore-missing` to require the complete tree. A standard shell alternative, also run inside the release folder, is `sha256sum -c --ignore-missing SHA256SUMS` for a partial download and `sha256sum -c SHA256SUMS` for a complete one. Before trusting the tree, compare the SHA-256 digests of the downloaded `SHA256SUMS` and `MANIFEST.parquet` with the digests in the bucket-root README. `tools/download.py` prints the `SHA256SUMS` digest when it starts, and `--sums-sha256 <digest>` makes it stop if the digest differs. The checksum file includes the manifest, while the manifest excludes itself and the checksum file to avoid recursive hashes.

The starter quickstart is `python -B loader/quickstart.py . --starter`; `python -B loader/tests.py .` tests the available layout. HDF5 requires h5py >= 3.0 / HDF5 >= 1.10. Install the pinned requirements from `requirements.txt`; it includes CPU PyTorch.

Report download or checksum problems to support@encord.com.
