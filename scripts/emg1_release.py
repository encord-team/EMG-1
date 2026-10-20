"""Shared registry and helpers for the EMG-1 release scripts. Standard library only.

EMG-1 is published as two separate datasets, each in its own public bucket with its own release tree. Every
script takes the dataset as its first argument, so there is never any doubt which bucket a command talks to:

    3ch-ego    EMG-1 3-channel dataset   emg1-3ch-ego-release    factory textile work, 4,916 five-minute clips
    8ch-mocap  EMG-1 8-channel dataset   emg1-8ch-mocap-release  free hand movement with mocap, 920 takes

The values that change between versions (base URL, version prefix, published digests, counts, subset sizes) live
in index/<dataset>/RELEASE.json, written by scripts/build_index.py. DATASETS below holds the fallbacks. The base
URL can be overridden per dataset with EMG1_BASE_URL_3CH_EGO or EMG1_BASE_URL_8CH_MOCAP (for a mirror or a custom
domain).
"""
from __future__ import annotations

import csv
import hashlib
import http.client
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
USER_AGENT = "emg1-release-repo/1.0 (Python urllib)"

DATASETS = {
    "3ch-ego": {
        "id": "3ch-ego",
        "dataset": "EMG-1 3-channel dataset",
        "tagline": "3-channel wrist EMG, IMU and PPG with egocentric video during factory textile work",
        "bucket": "emg1-3ch-ego-release",
        "base_url": "https://pub-b29550bc5a1c44e08e91624ebf1cb243.r2.dev",
        "version": "v1.0.1",
        "release_date": "2026-10-20",
        "sha256sums_sha256": "724dc60071da364309cb69f7d62a3c608dd4310f6cb3570e66c9d1a86e282ed0",
        "dest": "emg1-3ch-v1.0.1",
        "unit": "clip",
        "has_raw": True,
    },
    "8ch-mocap": {
        "id": "8ch-mocap",
        "dataset": "EMG-1 8-channel dataset",
        "tagline": "8-channel forearm EMG, IMU and PPG with OptiTrack hand markers and stereo video during free hand movement",
        "bucket": "emg1-8ch-mocap-release",
        "base_url": "https://pub-91c561c2860c47e9b776fa8dff99271e.r2.dev",
        "version": "v1.0.1",
        "release_date": "2026-10-20",
        "sha256sums_sha256": "f3b335e64fea3edd31da96b6fc577eb23591bd87150f21d30b10c57e7393f8a0",
        "dest": "emg1-8ch-v1.0.1",
        "unit": "take",
        "has_raw": False,
    },
}
# Supplements live in a bucket outside the frozen version prefix, with their own SHA256SUMS; the release's own
# tools/download.py does not fetch them, so scripts/download.py handles them itself.
SUPPLEMENTS = {
    "8ch-mocap": {
        "name": "EMG-1 fusion hand-pose predictions (Wearable Devices), supplement v1",
        "prefix": "supplements/wd-fusion-predictions/v1",
        "sha256sums_sha256": "80394007f3ffa446f0b0b743784ce26865c94dab67e2b8cccf08e3522eb383dd",
        "dest": "emg1-wd-fusion-v1",
    },
}
ALIASES = {"3ch": "3ch-ego", "ego": "3ch-ego", "3ch-ego": "3ch-ego", "8ch": "8ch-mocap", "mocap": "8ch-mocap", "8ch-mocap": "8ch-mocap"}
DATASET_CHOICES = ("3ch-ego", "3ch", "8ch-mocap", "8ch")

# What an "item" looks like per dataset: a clip ID, or a person / session / take path.
ITEM_RE = {
    "3ch-ego": re.compile(r"\d{8}_egox-\d{3}_\d{6}_[0-9a-f]{8}"),
    "8ch-mocap": re.compile(r"OP-\d{3}(/s\d{3}(/\d{2})?)?"),
}
ITEM_EXAMPLE = {"3ch-ego": "20261005_egox-018_112656_888ded7e", "8ch-mocap": "OP-001/s003/02 (or OP-001/s003, or OP-001)"}

# Exclude patterns of the documented 3ch-ego subsets (its BUCKET_README.md); the starter selection comes from
# tools/3ch-ego/starter_subset.py.
TRAINING_EXCLUDE = ["derived/wrist_poses_est/*", "index/video_frames/*", "*.mcap"]
FULL_EXCLUDE = ["*.mcap"]


def resolve(name: str) -> str:
    """The canonical dataset id for a name or alias, or a readable error."""
    key = (name or "").strip().lower()
    if key not in ALIASES:
        options = ", ".join(f"{k} (or {a})" for k, a in (("3ch-ego", "3ch"), ("8ch-mocap", "8ch")))
        raise SystemExit(f"unknown dataset {name!r}; choose one of: {options}")
    return ALIASES[key]


def index_dir(ds: str) -> Path:
    return REPO / "index" / resolve(ds)


def tools_dir(ds: str) -> Path:
    return REPO / "tools" / resolve(ds)


def docs_dir(ds: str, info: dict | None = None) -> Path:
    info = info or release(ds)
    return REPO / "docs" / f'{resolve(ds)}-{info["version"]}'


def release(ds: str) -> dict:
    """index/<dataset>/RELEASE.json merged over the DATASETS fallbacks; the environment wins for the base URL."""
    ds = resolve(ds)
    info = dict(DATASETS[ds])
    path = index_dir(ds) / "RELEASE.json"
    if path.is_file():
        info.update(json.loads(path.read_text()))
    env = os.environ.get("EMG1_BASE_URL_" + ds.upper().replace("-", "_"))
    if env:
        info["base_url"] = env
    info["base_url"] = info["base_url"].rstrip("/")
    info["id"] = ds
    if ds in SUPPLEMENTS and "supplement" not in info:
        info["supplement"] = dict(SUPPLEMENTS[ds])
    return info


def object_url(info: dict, key: str) -> str:
    """Public URL of a release key.

    Keys are paths below the version prefix ('sensors/<clip>.h5', 'takes/OP-001/s003/02/take.h5'). The 3ch-ego raw
    MCAP keys from raw/RAW_OBJECTS.csv already carry the prefix ('v1.0.1/raw/...'), and supplement keys start with
    'supplements/'; both are relative to the bucket root and are used as they are.
    """
    if key.startswith(info["version"] + "/") or key.startswith("supplements/"):
        return f'{info["base_url"]}/{key}'
    return f'{info["base_url"]}/{info["version"]}/{key}'


def fetch(url: str, timeout: float = 120.0, attempts: int = 8) -> bytes:
    """GET a public object. Resumes a cut-short response with a Range request and retries network hiccups."""
    data = bytearray()
    total = None
    last = "unknown error"
    for attempt in range(1, attempts + 1):
        headers = {"User-Agent": USER_AGENT}
        if data:
            headers["Range"] = f"bytes={len(data)}-"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as response:
                if data and response.status != 206:  # the server ignored Range: start over
                    data = bytearray()
                if total is None:
                    length = response.headers.get("Content-Length")
                    total = int(length) if length and not data else None
                try:
                    data += response.read()
                except http.client.IncompleteRead as e:
                    data += e.partial
                    raise
            if total is None or len(data) == total:
                return bytes(data)
            last = f"{len(data)} of {total} bytes"
        except urllib.error.HTTPError as e:
            if e.code == 416 and total is not None and len(data) == total:
                return bytes(data)
            if e.code in (408, 429, 500, 502, 503, 504) and attempt < attempts:
                last = f"HTTP {e.code}"
            else:
                raise SystemExit(f"HTTP {e.code} for {url}") from None
        except (urllib.error.URLError, http.client.HTTPException, TimeoutError, OSError) as e:
            last = str(getattr(e, "reason", e))
        time.sleep(min(2 ** attempt, 30))
    raise SystemExit(f"cannot fetch {url} after {attempts} attempts ({last})")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 << 20), b""):
            h.update(block)
    return h.hexdigest()


def parse_sums(text: str) -> dict[str, str]:
    """SHA256SUMS lines ('<hex>  <key>') as {key: digest}."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        sep = "  " if "  " in line else " *"
        digest, key = line.split(sep, 1)
        out[key] = digest.lower()
    return out


def read_csv(path: Path) -> list[dict]:
    if not path.is_file():
        raise SystemExit(f"missing {path.relative_to(REPO)}: run scripts/build_index.py {path.parent.name}, or git pull")
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_files(ds: str) -> list[dict]:
    """index/<dataset>/files.csv rows: key, bytes (int or None), sha256."""
    rows = read_csv(index_dir(ds) / "files.csv")
    for r in rows:
        r["bytes"] = int(r["bytes"]) if r["bytes"] else None
    return rows


def load_raw(ds: str) -> list[dict]:
    """index/3ch-ego/raw_objects.csv rows: clip_id, release_key, bytes (int), etag, part_size. Empty for 8ch-mocap."""
    if not DATASETS[resolve(ds)]["has_raw"]:
        return []
    rows = read_csv(index_dir(ds) / "raw_objects.csv")
    for r in rows:
        r["bytes"] = int(r["bytes"])
    return rows


def load_supplement_files(ds: str) -> list[dict]:
    """index/<dataset>/supplement_files.csv rows (key relative to the bucket root, bytes, sha256), or []."""
    path = index_dir(ds) / "supplement_files.csv"
    if not path.is_file():
        return []
    rows = read_csv(path)
    for r in rows:
        r["bytes"] = int(r["bytes"]) if r["bytes"] else None
    return rows


def load_units(ds: str) -> list[dict]:
    """One row per clip (index/3ch-ego/clips.csv) or per take (index/8ch-mocap/takes.csv)."""
    ds = resolve(ds)
    return read_csv(index_dir(ds) / ("clips.csv" if ds == "3ch-ego" else "takes.csv"))


def human(n) -> str:
    """Decimal units (GB = 10^9 bytes), as in the release documentation."""
    if n is None:
        return "?"
    n = float(n)
    for unit in ("B", "kB", "MB", "GB", "TB"):
        if n < 1000 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.2f} {unit}"
        n /= 1000
    return f"{n:.2f} TB"
