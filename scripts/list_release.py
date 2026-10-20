#!/usr/bin/env python3
"""List what is in an EMG-1 bucket, without downloading any data. The first argument says which dataset.

    python3 scripts/list_release.py 3ch-ego --summary                        totals per folder and subset
    python3 scripts/list_release.py 3ch-ego 'sensors/*egox-018*'             files matching a glob ('*' also matches '/')
    python3 scripts/list_release.py 3ch-ego --clip 20261005_egox-018_112656_888ded7e     everything of one clip, raw MCAP included
    python3 scripts/list_release.py 8ch-mocap --summary
    python3 scripts/list_release.py 8ch-mocap --take OP-001/s003/02          one take; --take OP-001/s003 a session; --take OP-001 a person
    python3 scripts/list_release.py 8ch-mocap --supplement                   the Wearable Devices predictions supplement, outside v1.0.1
    python3 scripts/list_release.py 8ch-mocap 'takes/*/take.h5' --urls > urls.txt     one URL per line, for curl, wget or aria2c
    python3 scripts/list_release.py DATASET --json                           JSON lines: key, bytes, sha256 or etag, url
    python3 scripts/list_release.py DATASET --refresh --summary              read the live bucket, not the committed index

DATASET is 3ch-ego (alias 3ch) or 8ch-mocap (alias 8ch). The listing comes from index/<dataset>/ in this repository,
a snapshot of the bucket written by scripts/build_index.py. --refresh fetches SHA256SUMS (and raw/RAW_OBJECTS.csv
for 3ch-ego) from the bucket instead, plus MANIFEST.parquet for sizes if pyarrow is installed. The 3ch-ego raw MCAP
objects (43 TB) are listed only with --raw or --clip. Standard library only.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from fnmatch import fnmatchcase
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import emg1_release as rel  # noqa: E402


def rows_from_index(ds):
    files = [{"key": r["key"], "bytes": r["bytes"], "digest": r["sha256"], "kind": "file"} for r in rel.load_files(ds)]
    files += [{"key": r["key"], "bytes": r["bytes"], "digest": r["sha256"], "kind": "supplement"} for r in rel.load_supplement_files(ds)]
    raw = [
        {"key": r["release_key"], "bytes": r["bytes"], "digest": r["etag"], "kind": "raw", "clip_id": r["clip_id"]}
        for r in rel.load_raw(ds)
    ]
    return files, raw


def rows_from_bucket(info):
    sums_bytes = rel.fetch(rel.object_url(info, "SHA256SUMS"))
    digest = rel.sha256_bytes(sums_bytes)
    if digest != info["sha256sums_sha256"]:
        print(
            f"note: the bucket's SHA256SUMS digest is {digest}, index/{info['id']}/RELEASE.json has "
            f"{info['sha256sums_sha256']}; a new version may have been published (scripts/build_index.py refreshes the index)",
            file=sys.stderr,
        )
    sums = rel.parse_sums(sums_bytes.decode("utf-8"))
    sizes: dict = {}
    try:
        import pyarrow.parquet as pq  # optional

        table = pq.read_table(io.BytesIO(rel.fetch(rel.object_url(info, "MANIFEST.parquet"))), columns=["key", "bytes"])
        sizes = dict(zip(table["key"].to_pylist(), table["bytes"].to_pylist()))
    except ImportError:
        print("note: pyarrow is not installed, so --refresh cannot show sizes", file=sys.stderr)
    files = [{"key": k, "bytes": sizes.get(k), "digest": d, "kind": "file"} for k, d in sorted(sums.items())]
    sup = info.get("supplement")
    if sup:
        sup_sums = rel.parse_sums(rel.fetch(f'{info["base_url"]}/{sup["prefix"]}/SHA256SUMS').decode("utf-8"))
        files += [{"key": f'{sup["prefix"]}/{k}', "bytes": None, "digest": d, "kind": "supplement"} for k, d in sorted(sup_sums.items())]
    raw = []
    if info["has_raw"]:
        raw_text = rel.fetch(rel.object_url(info, "raw/RAW_OBJECTS.csv")).decode("utf-8")
        raw = [
            {"key": r["release_key"], "bytes": int(r["bytes"]), "digest": r["etag"], "kind": "raw", "clip_id": r["clip_id"]}
            for r in csv.DictReader(io.StringIO(raw_text))
        ]
    return files, raw


def select(files, raw, patterns, item=None, with_raw=False, with_supplement=False):
    rows = [r for r in files if r["kind"] != "supplement" or with_supplement or item]
    if with_raw or item:
        rows += raw
    if item:
        needle = item if "/" in item else item  # clip ids and OP-001/s003/02 paths are both substrings of their keys
        rows = [r for r in rows if needle in r["key"]]
    if patterns:
        rows = [r for r in rows if any(fnmatchcase(r["key"], p) for p in patterns)]
    return rows


def print_rows(rows, args, info):
    if args.json:
        for r in rows:
            name = "etag" if r["kind"] == "raw" else "sha256"
            print(json.dumps({"key": r["key"], "bytes": r["bytes"], name: r["digest"], "url": rel.object_url(info, r["key"])}))
        return
    if args.urls:
        for r in rows:
            print(rel.object_url(info, r["key"]))
        return
    width = max((len(rel.human(r["bytes"])) for r in rows), default=0)
    for r in rows:
        print(f'{rel.human(r["bytes"]):>{width}}  {r["key"]}')
    total = sum(r["bytes"] or 0 for r in rows)
    unknown = sum(1 for r in rows if r["bytes"] is None)
    note = f" ({unknown} without a known size)" if unknown else ""
    sys.stdout.flush()
    print(f"\n{len(rows):,} objects, {rel.human(total)}{note}", file=sys.stderr)


def print_summary(files, raw, info):
    per: dict[str, list] = {}
    supplement = [r for r in files if r["kind"] == "supplement"]
    files = [r for r in files if r["kind"] != "supplement"]
    unknown = any(r["bytes"] is None for r in files)
    size_of = (lambda b: "?") if unknown else rel.human
    for r in files:
        top = r["key"].split("/", 1)[0] + "/" if "/" in r["key"] else "(root files)"
        c = per.setdefault(top, [0, 0])
        c[0] += 1
        c[1] += r["bytes"] or 0
    print(f'{info["dataset"]} {info["version"]}  ({info["id"]}, bucket {info["bucket"]})')
    print(f'{info["base_url"]}/{info["version"]}/\n')
    print(f'{"folder":<26}{"files":>8}{"size":>12}')
    for top, (count, size) in sorted(per.items(), key=lambda kv: -kv[1][1]):
        print(f"{top:<26}{count:>8,}{size_of(size):>12}")
    total = sum(r["bytes"] or 0 for r in files)
    print(f'{"extracted release":<26}{len(files):>8,}{size_of(total):>12}')
    if raw:
        print(f'{"raw/ MCAP (--raw)":<26}{len(raw):>8,}{rel.human(sum(r["bytes"] for r in raw)):>12}')
    if supplement:
        sup_total = sum(r["bytes"] or 0 for r in supplement)
        print(f'{"supplements/ (--supplement)":<26}{len(supplement):>8,}{(rel.human(sup_total) if sup_total else chr(63)):>12}')
    subsets = info.get("subsets")
    if subsets:
        print(f'\n{"subset":<12}{"files":>8}{"size":>12}  command')
        for name, s in subsets.items():
            print(f'{name:<12}{s["files"]:>8,}{rel.human(s["bytes"]):>12}  {s["command"]}')


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dataset", choices=rel.DATASET_CHOICES, metavar="DATASET")
    ap.add_argument("patterns", nargs="*", metavar="PATTERN", help="shell-style globs on the key; '*' also matches '/'")
    ap.add_argument("--clip", "--take", "--person", "--item", dest="item", metavar="ITEM",
                    help="everything that belongs to one clip (3ch-ego) or one take, session or person (8ch-mocap)")
    ap.add_argument("--raw", action="store_true", help="3ch-ego: include the raw MCAP objects")
    ap.add_argument("--supplement", action="store_true", help="8ch-mocap: include the predictions supplement (outside v1.0.1)")
    ap.add_argument("--summary", action="store_true", help="totals per folder and subset instead of a file list")
    ap.add_argument("--urls", action="store_true", help="print one download URL per line")
    ap.add_argument("--json", action="store_true", help="print JSON lines")
    ap.add_argument("--refresh", action="store_true", help="read the bucket instead of index/<dataset>/")
    args = ap.parse_args(argv)
    ds = rel.resolve(args.dataset)
    if args.item and not rel.ITEM_RE[ds].fullmatch(args.item):
        ap.error(f"for {ds} the item looks like {rel.ITEM_EXAMPLE[ds]} (see index/{ds}/)")
    info = rel.release(ds)
    files, raw = rows_from_bucket(info) if args.refresh else rows_from_index(ds)
    if args.summary:
        print_summary(files, raw, info)
        return 0
    rows = select(files, raw, args.patterns, item=args.item, with_raw=args.raw, with_supplement=args.supplement)
    if not rows:
        print("nothing matched", file=sys.stderr)
        return 1
    print_rows(rows, args, info)
    return 0


if __name__ == "__main__":
    sys.exit(main())
