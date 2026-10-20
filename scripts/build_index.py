#!/usr/bin/env python3
"""Rebuild index/<dataset>/ from the live bucket (for maintainers). The first argument says which dataset.

    python3 scripts/build_index.py 3ch-ego                                    refresh index/3ch-ego/ for the current version
    python3 scripts/build_index.py 8ch-mocap --version v1.0.2 --sums-sha256 HEX   move a dataset to a new release version
    python3 scripts/build_index.py 8ch-mocap --base-url https://data.example.com  a different bucket or mirror

Fetches SHA256SUMS and MANIFEST.parquet (plus raw/RAW_OBJECTS.csv and index/clips.parquet for 3ch-ego, or
index/takes.parquet and index/takes_extra.parquet for 8ch-mocap), checks each against its published digest, and
writes:

    index/<dataset>/RELEASE.json      version, base URL, bucket, digests, counts, totals and subset sizes
    index/<dataset>/files.csv         every release file: key, bytes, sha256
    index/<dataset>/SUMMARY.md        totals per folder, subset and the dataset's own groupings
    index/<dataset>/STRUCTURE.md      the directory structure of the bucket, repeated per-recording paths collapsed
    index/3ch-ego/raw_objects.csv     every raw MCAP object (3ch-ego only): clip_id, release_key, bytes, etag, part_size
    index/3ch-ego/clips.csv           one row per clip: station, date, split, tiers, task, hours and its files with sizes
    index/8ch-mocap/takes.csv         one row per take: person, session, tiers, partition, lag and its files with sizes

The SHA256SUMS digest is a release's identity. It is published out of band (the bucket-root README.md of the
3ch-ego bucket); pass it with --sums-sha256 when switching versions, because the script refuses a SHA256SUMS whose
digest it was not told to expect. Needs pyarrow: python3 -m pip install pyarrow, or
    uv run --with pyarrow scripts/build_index.py DATASET
Downloads are cached in --cache (default .cache/<dataset>/<version>/, git-ignored) and reused when their digest matches.
The structure page comes from the bucket's own listing when index/<dataset>/ holds one: bucket_objects.csv (every
object, written by scripts/list_bucket.py through R2's S3 API) or bucket_structure.json (per-path aggregates of a
listing through the Cloudflare API). The listing is cross-checked against the manifests and any difference is
reported and recorded in RELEASE.json. Without a listing, the page is built from the manifests alone.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import datetime as dt
import urllib.request
import io
import json
import re
import sys
from collections import Counter, defaultdict
from fnmatch import fnmatchcase
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import emg1_release as rel  # noqa: E402

try:
    import pyarrow.parquet as pq
except ImportError:
    raise SystemExit("pyarrow is required: python3 -m pip install pyarrow   (or: uv run --with pyarrow scripts/build_index.py DATASET)")

SUBSET_COMMAND = "python3 scripts/download.py {ds} {subset}"


# ------------------------------------------------------------------------------------------------ helpers

def get(cache: Path, info: dict, key: str, expected: str | None) -> bytes:
    path = cache / key
    if path.is_file() and expected and rel.sha256_file(path) == expected:
        return path.read_bytes()
    url = rel.object_url(info, key)
    print(f"fetching {url}", file=sys.stderr)
    data = rel.fetch(url, timeout=900)
    if expected and rel.sha256_bytes(data) != expected:
        raise SystemExit(f"{key}: digest {rel.sha256_bytes(data)} does not match SHA256SUMS ({expected})")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def parquet_rows(data: bytes, columns=None) -> list[dict]:
    table = pq.read_table(io.BytesIO(data))
    if columns:
        table = table.select([c for c in columns if c in table.column_names])
    return table.to_pylist()


def fmt(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def md_table(headers, rows) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(" ---: " if i else " --- " for i in range(len(headers))) + "|"]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(out)


def subset_entry(ds: str, name: str, keys, size: dict) -> dict:
    """Files and bytes of a selection; tools/download.py always adds SHA256SUMS and MANIFEST.parquet."""
    keys = list(keys)
    has_manifest = "MANIFEST.parquet" in keys
    return {
        "files": len(keys) + 1 + (0 if has_manifest else 1),
        "bytes": sum(size[k] for k in keys) + (0 if has_manifest else size["MANIFEST.parquet"]),
        "command": SUBSET_COMMAND.format(ds=ds, subset=name),
    }


def write_csv(path: Path, rows: list[dict], fieldnames=None):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames or list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def folder_table(size: dict, raw_rows=None) -> list:
    per: dict[str, list] = defaultdict(lambda: [0, 0])
    for k, b in size.items():
        top = k.split("/", 1)[0] + "/" if "/" in k else "(root files)"
        per[top][0] += 1
        per[top][1] += b
    rows = [(top, f"{c:,}", rel.human(b)) for top, (c, b) in sorted(per.items(), key=lambda kv: -kv[1][1])]
    rows.append(("**extracted release**", f"{len(size):,}", rel.human(sum(size.values()))))
    if raw_rows:
        rows.append(("raw/ (MCAP, not in SHA256SUMS)", f"{len(raw_rows):,}", rel.human(sum(int(r["bytes"]) for r in raw_rows))))
    return rows


def hours(rows, col):
    return sum(float(r[col] or 0) for r in rows)


# ------------------------------------------------------------------------------------------------ 3ch-ego

CLIP_COLUMNS = [
    "clip_id", "station", "date", "session_id", "station_day", "split", "clip_tier", "left_tier", "right_tier",
    "duration_s", "task_category", "clip_hours_with_emg", "both_gold_standard_hours",
]


def build_3ch(info, cache, sums, size):
    out_dir = rel.index_dir("3ch-ego")
    raw_csv = get(cache, info, "raw/RAW_OBJECTS.csv", sums["raw/RAW_OBJECTS.csv"])
    raw_rows = list(csv.DictReader(io.StringIO(raw_csv.decode("utf-8"))))
    raw_by_clip = {r["clip_id"]: r for r in raw_rows}
    clips = parquet_rows(get(cache, info, "index/clips.parquet", sums["index/clips.parquet"]),
                         CLIP_COLUMNS + ["sensor_path", "derived_sensor_path", "pose_path", "vendor_path"])
    frame_tables: Counter = Counter()
    for key in size:
        if key.startswith("index/video_frames/"):
            frame_tables[key.split("/")[2]] += 1
    clip_rows = []
    for c in sorted(clips, key=lambda c: c["clip_id"]):
        cid = c["clip_id"]
        sensors = c.get("sensor_path") or f"sensors/{cid}.h5"
        est = c.get("derived_sensor_path") or f"derived/sensors_est/{cid}_est.h5"
        pose = c.get("pose_path") or f"derived/wrist_poses_est/{cid}_est.h5"
        vendor = c.get("vendor_path") or f"vendor/{cid}.json"
        raw = raw_by_clip.get(cid, {})
        row = {col: fmt(c.get(col)) for col in CLIP_COLUMNS}
        row.update({
            "starter": "yes" if f"starter/sensors/{cid}.h5" in size else "",
            "sensors_key": sensors if sensors in size else "", "sensors_bytes": fmt(size.get(sensors)),
            "sensors_est_key": est if est in size else "", "sensors_est_bytes": fmt(size.get(est)),
            "wrist_poses_key": pose if pose in size else "", "wrist_poses_bytes": fmt(size.get(pose)),
            "vendor_key": vendor if vendor in size else "",
            "frame_tables": frame_tables.get(cid, 0),
            "raw_key": raw.get("release_key", ""), "raw_bytes": raw.get("bytes", ""), "raw_etag": raw.get("etag", ""),
        })
        clip_rows.append(row)

    sys.path.insert(0, str(rel.tools_dir("3ch-ego")))
    import starter_subset

    patterns = starter_subset.aws_patterns(list(size))
    subsets = {
        "starter": subset_entry("3ch-ego", "starter", (k for k in size if starter_subset.selected(k, patterns)), size),
        "training": subset_entry("3ch-ego", "training", (k for k in size if not any(fnmatchcase(k, p) for p in rel.TRAINING_EXCLUDE)), size),
        "full": subset_entry("3ch-ego", "full", (k for k in size if not any(fnmatchcase(k, p) for p in rel.FULL_EXCLUDE)), size),
        "raw": {"files": len(raw_rows), "bytes": sum(int(r["bytes"]) for r in raw_rows),
                "command": SUBSET_COMMAND.format(ds="3ch-ego", subset="raw")},
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "raw_objects.csv").write_bytes(raw_csv)
    write_csv(out_dir / "clips.csv", clip_rows)

    by_station = defaultdict(list)
    for r in clip_rows:
        by_station[r["station"]].append(r)
    station_rows = []
    for st, rows_ in sorted(by_station.items()):
        splits = Counter(r["split"] for r in rows_)
        station_rows.append((st, f"{len(rows_):,}", len({r["date"] for r in rows_}), f'{hours(rows_, "clip_hours_with_emg"):.1f}',
                             f'{hours(rows_, "both_gold_standard_hours"):.1f}',
                             f'{splits.get("train", 0)} / {splits.get("val", 0)} / {splits.get("test", 0)}',
                             rel.human(sum(int(r["raw_bytes"] or 0) for r in rows_))))
    order = {"train": 0, "val": 1, "test": 2}
    by_split = defaultdict(list)
    for r in clip_rows:
        by_split[r["split"] or "(none)"].append(r)
    split_rows = [(s, f"{len(rows_):,}", len({r["station_day"] for r in rows_}), f'{hours(rows_, "clip_hours_with_emg"):.1f}',
                   f'{hours(rows_, "both_gold_standard_hours"):.1f}')
                  for s, rows_ in sorted(by_split.items(), key=lambda kv: order.get(kv[0], 9))]
    tier_order = {"GOLD": 0, "STANDARD": 1, "EXTENDED": 2, "NONE": 3}
    tier_rows = [(t, f"{n:,}", f'{hours([r for r in clip_rows if r["clip_tier"] == t], "both_gold_standard_hours"):.1f}')
                 for t, n in sorted(Counter(r["clip_tier"] for r in clip_rows).items(), key=lambda kv: tier_order.get(kv[0], 9))]
    task_rows = [(t, f"{n:,}") for t, n in Counter(r["task_category"] for r in clip_rows).most_common()]
    sections = f"""## Stations

A station is a recording kit, not a person. Partition counts are the primary station-day split.

{md_table(["station", "clips", "days", "clip-hours with EMG", "both-wrist GOLD/STANDARD hours", "train / val / test", "raw MCAP"], station_rows)}

## Primary split

{md_table(["partition", "clips", "station-days", "clip-hours with EMG", "both-wrist GOLD/STANDARD hours"], split_rows)}

## Clip quality tier

The clip tier is the worse of the two wrist tiers; quality segments inside lower-tier clips can still be usable
(`QUALITY_TIERS.md`).

{md_table(["clip tier", "clips", "both-wrist GOLD/STANDARD hours"], tier_rows)}

## Dominant vendor task category per clip

Unverified vendor titles mapped by the frozen keyword taxonomy (`TASK_LABELS.md`).

{md_table(["task category", "clips"], task_rows)}
"""
    counts = {"clips": len(clip_rows), "raw_objects": len(raw_rows), "raw_bytes": sum(int(r["bytes"]) for r in raw_rows),
              "stations": len(by_station), "clip_hours_with_emg": round(hours(clip_rows, "clip_hours_with_emg"), 3),
              "both_wrist_quality_hours": round(hours(clip_rows, "both_gold_standard_hours"), 3)}
    notes = ("Starter = 20 complete clips plus every index, split, taxonomy, loader, test, tool, baseline and document. "
             "Training = everything except wrist poses, video frame tables and raw MCAPs. Raw = the original MCAP recordings, "
             "listed in `raw/RAW_OBJECTS.csv` rather than `SHA256SUMS`.")
    return subsets, counts, sections, notes, raw_rows


# ------------------------------------------------------------------------------------------------ 8ch-mocap

TAKE_COLUMNS = ["source", "take_id", "subject_id", "session_id", "duration_s", "EMG_TIER", "MULTIMODAL_TIER",
                "default_smoke_partition", "transport", "lag_measured", "lag_ms", "emg_coverage", "failed_channels",
                "has_mediapipe_stereo_est"]
EXTRA_COLUMNS = ["take_id", "scenario_version", "has_rest_phase", "rest_posture", "ppg_nominal_hz"]


def build_8ch(info, cache, sums, size):
    out_dir = rel.index_dir("8ch-mocap")
    takes = parquet_rows(get(cache, info, "index/takes.parquet", sums["index/takes.parquet"]), TAKE_COLUMNS)
    extra = {r["take_id"]: r for r in parquet_rows(get(cache, info, "index/takes_extra.parquet", sums["index/takes_extra.parquet"]), EXTRA_COLUMNS)}
    take_rows = []
    for t in sorted(takes, key=lambda t: t["source"]):
        path = t["source"]
        x = extra.get(t["take_id"], {})
        row = {
            "take": path, "take_id": t["take_id"], "person": t["subject_id"], "session": t["session_id"],
            "duration_s": fmt(t.get("duration_s")), "emg_tier": t.get("EMG_TIER", ""), "multimodal_tier": t.get("MULTIMODAL_TIER", ""),
            "default_partition": t.get("default_smoke_partition", ""), "transport": t.get("transport", ""),
            "lag_measured": fmt(t.get("lag_measured")), "lag_ms": fmt(t.get("lag_ms")), "emg_coverage": fmt(t.get("emg_coverage")),
            "failed_channels": fmt(t.get("failed_channels")), "has_mediapipe_stereo_est": fmt(t.get("has_mediapipe_stereo_est")),
            "scenario_version": fmt(x.get("scenario_version")), "has_rest_phase": fmt(x.get("has_rest_phase")),
            "rest_posture": fmt(x.get("rest_posture")), "ppg_nominal_hz": fmt(x.get("ppg_nominal_hz")),
            "starter": "yes" if f"starter/{path}/take.h5" in size else "",
        }
        for name, key in (("take_h5", f"takes/{path}/take.h5"), ("take_c3d", f"takes/{path}/take.c3d"),
                          ("take_mcap", f"takes/{path}/take.mcap"), ("derived", f"derived/{path}/automatic_est.h5")):
            row[f"{name}_key"] = key if key in size else ""
            row[f"{name}_bytes"] = fmt(size.get(key))
        take_rows.append(row)

    subsets = {
        "starter": subset_entry("8ch-mocap", "starter", (k for k in size if not k.startswith(("takes/", "derived/"))), size),
        "benchmark": subset_entry("8ch-mocap", "benchmark", (k for k in size if fnmatchcase(k, "takes/*/take.h5") or k.startswith("derived/")), size),
        "novideo": subset_entry("8ch-mocap", "novideo", (k for k in size if not k.endswith(".mcap")), size),
        "full": subset_entry("8ch-mocap", "full", size, size),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "takes.csv", take_rows)

    # The Wearable Devices predictions supplement: its own SHA256SUMS outside v1.0.1, sizes from HEAD requests.
    sup = dict(info["supplement"])
    sup_base = f'{info["base_url"]}/{sup["prefix"]}'
    sup_sums_bytes = rel.fetch(f"{sup_base}/SHA256SUMS")
    sup_digest = rel.sha256_bytes(sup_sums_bytes)
    if sup_digest != sup["sha256sums_sha256"]:
        raise SystemExit(f"{sup['prefix']}/SHA256SUMS has digest {sup_digest}, expected {sup['sha256sums_sha256']}; "
                         "update SUPPLEMENTS in scripts/emg1_release.py if the supplement was republished")
    sup_sums = rel.parse_sums(sup_sums_bytes.decode("utf-8"))

    def head_size(key):
        req = urllib.request.Request(f"{sup_base}/{key}", method="HEAD", headers={"User-Agent": rel.USER_AGENT})
        for _attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    return key, int(r.headers.get("Content-Length") or 0)
            except OSError:
                continue
        return key, 0

    print(f"sizing {len(sup_sums)} supplement files with HEAD requests", file=sys.stderr)
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        sup_sizes = dict(pool.map(head_size, sorted(sup_sums)))
    sup_rows = [{"key": f'{sup["prefix"]}/{k}', "bytes": sup_sizes[k], "sha256": sup_sums[k]} for k in sorted(sup_sums)]
    sup_rows.append({"key": f'{sup["prefix"]}/SHA256SUMS', "bytes": len(sup_sums_bytes), "sha256": sup_digest})
    write_csv(out_dir / "supplement_files.csv", sup_rows, ["key", "bytes", "sha256"])
    sup.update({"files": len(sup_rows), "bytes": sum(r["bytes"] for r in sup_rows),
                "command": SUBSET_COMMAND.format(ds="8ch-mocap", subset="supplement"),
                "readme_url": f"{sup_base}/README.md"})
    subsets["supplement"] = {"files": sup["files"], "bytes": sup["bytes"], "command": sup["command"]}


    tier_order = {"GOLD": 0, "STANDARD": 1, "EXTENDED": 2}
    by_person = defaultdict(list)
    for r in take_rows:
        by_person[r["person"]].append(r)
    person_rows = []
    for p, rows_ in sorted(by_person.items()):
        emg = Counter(r["emg_tier"] for r in rows_)
        mm = Counter(r["multimodal_tier"] for r in rows_)
        part = Counter(r["default_partition"] for r in rows_)
        person_rows.append((p, len(rows_), len({r["session"] for r in rows_}), f'{hours(rows_, "duration_s") / 3600:.2f}',
                            f'{emg.get("GOLD", 0)} / {emg.get("STANDARD", 0)} / {emg.get("EXTENDED", 0)}',
                            f'{mm.get("GOLD", 0)} / {mm.get("STANDARD", 0)} / {mm.get("EXTENDED", 0)}',
                            f'{part.get("train", 0)} / {part.get("val", 0)} / {part.get("test", 0)}',
                            sum(1 for r in rows_ if r["starter"]),
                            rel.human(sum(int(r["take_mcap_bytes"] or 0) for r in rows_))))
    part_order = {"train": 0, "val": 1, "test": 2}
    part_rows = [(p, n, f'{hours([r for r in take_rows if r["default_partition"] == p], "duration_s") / 3600:.3f}')
                 for p, n in sorted(Counter(r["default_partition"] for r in take_rows).items(), key=lambda kv: part_order.get(kv[0], 9))]
    emg_rows = [(t, n, f'{hours([r for r in take_rows if r["emg_tier"] == t], "duration_s") / 3600:.3f}')
                for t, n in sorted(Counter(r["emg_tier"] for r in take_rows).items(), key=lambda kv: tier_order.get(kv[0], 9))]
    mm_rows = [(t, n, f'{hours([r for r in take_rows if r["multimodal_tier"] == t], "duration_s") / 3600:.3f}')
               for t, n in sorted(Counter(r["multimodal_tier"] for r in take_rows).items(), key=lambda kv: tier_order.get(kv[0], 9))]
    transport_rows = Counter(r["transport"] for r in take_rows).most_common()
    lag_measured = sum(1 for r in take_rows if r["lag_measured"] == "true")
    est = sum(1 for r in take_rows if r["has_mediapipe_stereo_est"] == "true")
    sections = f"""## People

Person codes are pseudonyms; every take records the left hand. Partition counts are the `default_smoke` loader split
(the official evaluation is the 12 leave-one-person-out folds in `splits/loso_fold_*.json`).

{md_table(["person", "takes", "sessions", "hours", "EMG GOLD / STD / EXT", "multimodal GOLD / STD / EXT", "train / val / test", "starter", "video"], person_rows)}

## Default split (`splits/default_smoke.json`)

{md_table(["partition", "takes", "hours"], part_rows)}

## Quality tiers

`EMG_TIER` grades the EMG alone; `MULTIMODAL_TIER` adds marker, video and lag conditions (`QUALITY_TIERS.md`).

{md_table(["EMG tier", "takes", "hours"], emg_rows)}

{md_table(["multimodal tier", "takes", "hours"], mm_rows)}

## Other facts

- Band transport: {", ".join(f"{t} {n}" for t, n in transport_rows)}.
- Band-to-mocap lag measured and applied on {lag_measured} of {len(take_rows)} takes.
- Automatic MediaPipe stereo hand estimates (`derived/`) exist for {est} of {len(take_rows)} takes.
- Starter takes: {", ".join(r["take"] for r in take_rows if r["starter"])}.

## Supplement: Wearable Devices fusion hand-pose predictions

`{sup["prefix"]}/` in the same bucket, outside the frozen `v1.0.1/` prefix: {len(sup_rows)} files,
{rel.human(sup["bytes"])}, listed in `supplement_files.csv`. Frame-by-frame predictions of 20 finger joint angles for
391 of the 920 takes (people OP-001 to OP-008), CC BY 4.0, with its own `SHA256SUMS` (digest `{sup_digest}`).
`python3 scripts/download.py 8ch-mocap supplement` fetches it; its README is at `{sup_base}/README.md`.
"""
    counts = {"takes": len(take_rows), "people": len(by_person), "sessions": len({(r["person"], r["session"]) for r in take_rows}),
              "hours": round(hours(take_rows, "duration_s") / 3600, 3), "supplement": sup}
    notes = ("Starter = 3 complete takes (HDF5, C3D and video) plus the index, splits, loader, eval, baselines, calibration "
             "and documents. Benchmark = every take's `take.h5` and `derived/` estimates (tasks T1, T2, T3). "
             "Novideo = everything except the `take.mcap` video containers.")
    return subsets, counts, sections, notes, []



# ------------------------------------------------------------------------------------------------ structure

# Path components that stand for one recording, person, session, take, station or date are collapsed into
# placeholders, so the structure page shows the shape of the dataset instead of thousands of similar keys.
PLACEHOLDERS = [
    (re.compile(r"^\d{8}_egox-\d{3}_\d{6}_[0-9a-f]{8}$"), "<clip_id>"),
    (re.compile(r"^(\d{8}_egox-\d{3}_\d{6}_[0-9a-f]{8})(_est\.h5|\.h5|\.json|\.mcap)$"), "<clip_id>\\2"),
    (re.compile(r"^OP-\d{3}$"), "<person>"),
    (re.compile(r"^OP-\d{3}_Left\.motive$"), "<person>_Left.motive"),
    (re.compile(r"^OP-\d{3}__s\d{3}__\d{2}_fusion\.csv$"), "<person>__<session>__<take>_fusion.csv"),
    (re.compile(r"^s\d{3}$"), "<session>"),
    (re.compile(r"^\d{2}$"), "<take>"),
    (re.compile(r"^egox-\d{3}$"), "<station>"),
    (re.compile(r"^\d{8}$"), "<date>"),
    (re.compile(r"^(loso_fold_)\d{2}(.*)$"), "\\1<NN>\\2"),
    (re.compile(r"^(fold_)\d{2}(\.npz)$"), "\\1<NN>\\2"),
]


def collapse(component: str) -> str:
    for pattern, replacement in PLACEHOLDERS:
        if pattern.match(component):
            return pattern.sub(replacement, component)
    return component


def aggregate(keys: dict) -> dict:
    """Collapse keys (key -> bytes) into entries: collapsed path -> files, bytes, example key."""
    entries: dict = {}
    for key, size in keys.items():
        path = "/".join(collapse(c) for c in key.split("/"))
        e = entries.setdefault(path, {"files": 0, "bytes": 0, "example": key})
        e["files"] += 1
        e["bytes"] += size or 0
    return entries


def structure_page(title: str, entries: dict, intro: str) -> str:
    """A tree of the entries (collapsed path -> files, bytes, example), counted per folder."""
    tree: dict = {}
    for path, e in entries.items():
        parts = path.split("/")
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part + "/", {})
        node[parts[-1]] = {"__files": e["files"], "__bytes": e["bytes"], "__example": e.get("example", path)}

    def totals(node):
        if "__files" in node:
            return node["__files"], node["__bytes"]
        files = size = 0
        for child in node.values():
            f, b = totals(child)
            files += f
            size += b
        return files, size

    lines = []

    def render(node, prefix=""):
        items = sorted(node.items(), key=lambda kv: (not kv[0].endswith("/"), kv[0]))
        for i, (name, child) in enumerate(items):
            last = i == len(items) - 1
            branch = "└── " if last else "├── "
            files, size = totals(child)
            if "__files" in child:
                example = child["__example"].rsplit("/", 1)[-1]
                detail = rel.human(size) if files == 1 else f"{files:,} files, {rel.human(size)}" + (f", e.g. {example}" if example != name else "")
            else:
                detail = f"{files:,} files, {rel.human(size)}"
            lines.append(f"{prefix}{branch}{name:<{max(1, 58 - len(prefix) - 4)}} {detail}")
            if "__files" not in child:
                render(child, prefix + ("    " if last else "│   "))

    render(tree)
    files, size = totals(tree)
    body = "\n".join(lines)
    return f"""# {title}: structure

{intro}

Paths that repeat per recording are collapsed: `<clip_id>` is a 3-channel clip such as
`20261005_egox-018_112656_888ded7e`, `<person>/<session>/<take>` is an 8-channel take such as `OP-001/s003/02`,
`<station>` and `<date>` are the raw-layer folders. Counts and sizes are totals over the collapsed paths; sizes are
decimal (GB = 10^9 bytes). Every individual key is in `files.csv` (and `raw_objects.csv`, `supplement_files.csv`,
`bucket_objects.csv` where present).

```
{files:,} objects, {rel.human(size)}
{body}
```
"""


def bucket_listing(ds: str) -> tuple | None:
    """The bucket's own listing as (entries, meta), from bucket_objects.csv (every object, via scripts/list_bucket.py)
    or bucket_structure.json (per-path aggregates, via the Cloudflare API), or None."""
    objects = rel.index_dir(ds) / "bucket_objects.csv"
    if objects.is_file():
        rows = rel.read_csv(objects)
        keys = {r["key"]: int(r["bytes"]) for r in rows}
        return aggregate(keys), {"source": "bucket_objects.csv", "objects": len(keys), "bytes": sum(keys.values())}
    structure = rel.index_dir(ds) / "bucket_structure.json"
    if structure.is_file():
        data = json.loads(structure.read_text())
        entries = data["entries"]
        files = sum(e["files"] for e in entries.values())
        size = sum(e["bytes"] for e in entries.values())
        if files != data["objects"] or size != data["bytes"]:
            raise SystemExit(f"{structure}: entries add up to {files} objects / {size} bytes, header says "
                             f"{data['objects']} / {data['bytes']}")
        return entries, {"source": "bucket_structure.json", "objects": files, "bytes": size,
                         "listed_utc": data.get("listed_utc"), "method": data.get("method")}
    return None


def bucket_cross_check(bucket: dict, expected: dict) -> dict:
    """Compare the bucket's entries with the manifest-derived entries (both collapsed path -> files, bytes)."""
    only_bucket = sorted(set(bucket) - set(expected))
    only_manifest = sorted(set(expected) - set(bucket))
    mismatched = sorted(p for p in set(bucket) & set(expected)
                        if bucket[p]["files"] != expected[p]["files"] or bucket[p]["bytes"] != expected[p]["bytes"])
    for path in only_bucket:
        print(f"bucket has objects the manifests do not list: {path} ({bucket[path]['files']} files)", file=sys.stderr)
    for path in only_manifest:
        print(f"manifests list a path the bucket does not have: {path}", file=sys.stderr)
    for path in mismatched:
        print(f"bucket and manifests differ on {path}: {bucket[path]} vs {expected[path]}", file=sys.stderr)
    return {"only_in_bucket": only_bucket, "only_in_manifests": only_manifest, "mismatched": mismatched}


# ------------------------------------------------------------------------------------------------ main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dataset", choices=rel.DATASET_CHOICES, metavar="DATASET")
    ap.add_argument("--version", metavar="vX.Y.Z")
    ap.add_argument("--base-url", metavar="URL")
    ap.add_argument("--sums-sha256", metavar="HEX", help="published digest of SHA256SUMS for this version")
    ap.add_argument("--release-date", metavar="YYYY-MM-DD")
    ap.add_argument("--cache", type=Path, metavar="DIR")
    args = ap.parse_args(argv)

    ds = rel.resolve(args.dataset)
    info = rel.release(ds)
    if args.version:
        info["version"] = args.version
    if args.base_url:
        info["base_url"] = args.base_url.rstrip("/")
    if args.release_date:
        info["release_date"] = args.release_date
    expected_sums = args.sums_sha256 or info["sha256sums_sha256"]
    cache = args.cache or (rel.REPO / ".cache" / ds / info["version"])

    sums_bytes = get(cache, info, "SHA256SUMS", None)
    digest = rel.sha256_bytes(sums_bytes)
    if digest != expected_sums:
        raise SystemExit(
            f"SHA256SUMS at {rel.object_url(info, 'SHA256SUMS')} has digest {digest}, expected {expected_sums}.\n"
            f"If that is the published digest for {ds} {info['version']}, rerun with --sums-sha256 {digest}"
        )
    (cache / "SHA256SUMS").write_bytes(sums_bytes)
    sums = rel.parse_sums(sums_bytes.decode("utf-8"))
    manifest = get(cache, info, "MANIFEST.parquet", sums["MANIFEST.parquet"])

    rows = parquet_rows(manifest, ["key", "bytes", "sha256"])
    files = {r["key"]: {"key": r["key"], "bytes": int(r["bytes"]), "sha256": r["sha256"]} for r in rows}
    files["MANIFEST.parquet"] = {"key": "MANIFEST.parquet", "bytes": len(manifest), "sha256": sums["MANIFEST.parquet"]}
    for key in sorted(set(sums) - set(files)):
        print(f"warning: {key} is in SHA256SUMS but not in MANIFEST.parquet", file=sys.stderr)
    for key in sorted(set(files) - set(sums)):
        print(f"warning: {key} is in MANIFEST.parquet but not in SHA256SUMS", file=sys.stderr)
    mismatched = [k for k, r in files.items() if k in sums and sums[k] != r["sha256"]]
    if mismatched:
        raise SystemExit(f"{len(mismatched)} digests differ between SHA256SUMS and MANIFEST.parquet, e.g. {mismatched[0]}")
    files_list = [files[k] for k in sorted(files)]
    size = {r["key"]: r["bytes"] for r in files_list}

    builder = build_3ch if ds == "3ch-ego" else build_8ch
    subsets, counts, sections, notes, raw_rows = builder(info, cache, sums, size)

    out_dir = rel.index_dir(ds)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "files.csv", files_list, ["key", "bytes", "sha256"])
    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    release = {
        "id": ds,
        "dataset": info["dataset"],
        "tagline": info["tagline"],
        "version": info["version"],
        "release_date": info["release_date"],
        "bucket": info["bucket"],
        "base_url": info["base_url"],
        "dest": info["dest"],
        "unit": info["unit"],
        "has_raw": info["has_raw"],
        "sha256sums_sha256": digest,
        "manifest_sha256": sums["MANIFEST.parquet"],
        "files": len(files_list),
        "bytes": sum(size.values()),
        **counts,
        "subsets": subsets,
        "generated_utc": generated,
    }
    (out_dir / "RELEASE.json").write_text(json.dumps(release, indent=2) + "\n")

    subset_rows = [(name, f'{s["files"]:,}', rel.human(s["bytes"]), f'`{s["command"]}`') for name, s in subsets.items()]
    summary = f"""# {info["dataset"]} {info["version"]} ({ds}): what is in the bucket

Generated by `scripts/build_index.py {ds}` on {generated} from the release's own manifests at
`{info["base_url"]}/{info["version"]}/` (bucket `{info["bucket"]}`).

- `SHA256SUMS` digest: `{digest}`
- `MANIFEST.parquet` digest: `{sums["MANIFEST.parquet"]}`

## Folders

{md_table(["folder", "files", "size"], folder_table(size, raw_rows))}

## Subsets

{md_table(["subset", "files", "size", "command"], subset_rows)}

{notes} Sizes are decimal (GB = 10^9 bytes).

{sections}"""
    (out_dir / "SUMMARY.md").write_text(summary)

    # ---- STRUCTURE.md: from the bucket's own listing when one is in index/<dataset>/, cross-checked against the
    # manifests; from the manifests alone otherwise.
    expected_keys = {f'{info["version"]}/{k}': b for k, b in size.items()}
    for r in raw_rows:
        expected_keys[r["release_key"]] = int(r["bytes"])
    for r in rel.load_supplement_files(ds):
        expected_keys[r["key"]] = r["bytes"]
    expected = aggregate(expected_keys)
    listing = bucket_listing(ds)
    if listing:
        entries, meta = listing
        check = bucket_cross_check(entries, expected)
        how = (f"through the Cloudflare API on {meta['listed_utc'][:10]}" if meta.get("listed_utc")
               else "through R2's S3 API (`scripts/list_bucket.py`)")
        extras = ", ".join(f"`{p}`" for p in check["only_in_bucket"]) or "none"
        intro = (f"Every object in the bucket `{info['bucket']}`, listed {how}: {meta['objects']:,} objects, "
                 f"{rel.human(meta['bytes'])}. Compared with the release manifests (`SHA256SUMS`, `MANIFEST.parquet`"
                 + (", `raw/RAW_OBJECTS.csv`" if raw_rows else "") + (", the supplement's `SHA256SUMS`" if "supplement" in info else "")
                 + f"): objects only in the bucket: {extras}; paths only in the manifests: "
                 f"{len(check['only_in_manifests'])}; paths whose count or size differ: {len(check['mismatched'])}.")
        release["bucket_listing"] = {**{k: v for k, v in meta.items()}, **check}
        (out_dir / "RELEASE.json").write_text(json.dumps(release, indent=2) + "\n")
    else:
        entries = expected
        intro = (f"Every object of the release in the bucket `{info['bucket']}`, from the release's own manifests "
                 f"(`SHA256SUMS`, `MANIFEST.parquet`" + (", `raw/RAW_OBJECTS.csv`" if raw_rows else "") +
                 (", the supplement's `SHA256SUMS`" if "supplement" in info else "") + ").")
    (out_dir / "STRUCTURE.md").write_text(structure_page(f'{info["dataset"]} {info["version"]} ({ds})', entries, intro))
    unit = f'{counts.get("clips", counts.get("takes"))} {info["unit"]}s'
    print(f"index/{ds}/: {len(files_list):,} files, {unit} -> RELEASE.json, files.csv, SUMMARY.md and the per-{info['unit']} table",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
