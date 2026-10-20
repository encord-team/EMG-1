# Release tools (vendored)

Byte-identical copies of each release's own download and verification tools, one folder per dataset, so that a
fresh clone can download and verify a release without first trusting anything fetched over the network.

| Folder | File | Role |
| --- | --- | --- |
| `3ch-ego/` | `download.py` | The release's downloader: standard library only, SHA-256 check of every file, resumable, `--raw` for the raw MCAPs. `scripts/download.py 3ch-ego ...` wraps it. |
| `3ch-ego/` | `verify_download.py` | Re-hashes a downloaded tree against `SHA256SUMS` (`--subset starter`, `--require-all`). |
| `3ch-ego/` | `starter_subset.py` | The starter selection rule shared by the downloader, the verifier and `scripts/download.py`. |
| `3ch-ego/` | `verify_raw.py` | Checks one downloaded raw MCAP against its reconciled size and ETag (needs `loader/` in the tree). |
| `8ch-mocap/` | `download.py` | The same downloader (the two releases ship the identical file). `scripts/download.py 8ch-mocap ...` wraps it. |
| `8ch-mocap/` | `verify_download.py` | Re-hashes a downloaded tree against `SHA256SUMS` and `MANIFEST.parquet` (`--ignore-missing` for partial trees; needs pyarrow). |

Do not edit them. Their digests are the ones each release publishes in its `SHA256SUMS` (also in
`index/<dataset>/files.csv`). To check a copy by hand against its bucket:

```sh
curl -fsSL https://pub-b29550bc5a1c44e08e91624ebf1cb243.r2.dev/v1.0.1/SHA256SUMS -o /tmp/SHA256SUMS   # 3ch-ego
shasum -a 256 /tmp/SHA256SUMS        # must print 724dc60071da364309cb69f7d62a3c608dd4310f6cb3570e66c9d1a86e282ed0
grep '  tools/download.py$' /tmp/SHA256SUMS
shasum -a 256 tools/3ch-ego/download.py
```

The remaining release tools (checksum builders, release statistics, index dictionaries, privacy scans) are in each
bucket under `v1.0.1/tools/` and come with the starter download.
