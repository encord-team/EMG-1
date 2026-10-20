#!/usr/bin/env python3
"""Download an EMG-1 dataset, or part of it, with one command. The first argument says which dataset.

    python3 scripts/download.py 3ch-ego   starter                  1.5 GB   20 clips, every index, loader, splits, docs
    python3 scripts/download.py 3ch-ego   training                 298 GB   all 4,916 clips' sensors + clock estimates
    python3 scripts/download.py 3ch-ego   full                     314 GB   the whole extracted release (no raw MCAPs)
    python3 scripts/download.py 3ch-ego   clip CLIP_ID [--raw]     65 MB    one clip; --raw adds its ~9 GB raw MCAP
    python3 scripts/download.py 3ch-ego   raw                      43 TB    every raw MCAP recording (asks first)

    python3 scripts/download.py 8ch-mocap starter                  1.3 GB   3 takes, index, splits, loader, eval, baselines, docs
    python3 scripts/download.py 8ch-mocap benchmark                32 GB    every take's HDF5 + derived estimates (tasks T1-T3)
    python3 scripts/download.py 8ch-mocap novideo                  35 GB    everything except the video containers
    python3 scripts/download.py 8ch-mocap full                     217 GB   everything, stereo video included
    python3 scripts/download.py 8ch-mocap take OP-001/s003/02 [--video]     one take, a session (OP-001/s003) or a person (OP-001)
    python3 scripts/download.py 8ch-mocap supplement               195 MB   Wearable Devices fusion hand-pose predictions (CC BY 4.0)

    python3 scripts/download.py DATASET custom --include 'vendor/*' --exclude '*.mcap'    your own selection

DATASET is 3ch-ego (alias 3ch) or 8ch-mocap (alias 8ch). Options:
  --dest DIR      the release folder (default: emg1-3ch-v1.0.1 or emg1-8ch-v1.0.1 in the current directory;
                  the supplement goes to emg1-wd-fusion-v1, beside the release folder as its README expects)
  --list          dry run: print what would be downloaded
  --workers N     parallel downloads (default 8)
  --raw           3ch-ego: also fetch matching raw MCAP objects (clip, custom)
  --video         8ch-mocap: also fetch the take.mcap video containers (take, custom)
  --yes           skip the confirmation for 3ch-ego raw
  --no-verify     skip the verification pass after the download
Anything else is passed on to the release's tools/download.py (for example --timeout, --retries, --quiet); put the
wrapper's own options before the first --include or --exclude.

This is a thin wrapper around tools/<dataset>/download.py, each release's own standard-library downloader. It fills
in the bucket's public base URL, the version prefix and the published SHA256SUMS digest from index/<dataset>/RELEASE.json
and turns subset names into the include and exclude patterns the release documents. Every file is checked against
its SHA-256 digest, and running the same command again resumes an interrupted download. Python 3.8+, no packages.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import importlib.util
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import emg1_release as rel  # noqa: E402

# Subsets per dataset. 'arg' names a required item (clip ID, or take/session/person path).
SUBSETS = {
    "3ch-ego": {
        "starter": {"help": "20 complete clips plus every index, split, loader, test, tool, baseline and document"},
        "training": {"exclude": rel.TRAINING_EXCLUDE, "help": "all clips' sensors and clock estimates; no poses, frame tables or raw MCAPs"},
        "full": {"exclude": rel.FULL_EXCLUDE, "help": "the whole extracted release, everything but the raw MCAPs"},
        "clip": {"arg": "CLIP_ID", "help": "one clip's extracted files; --raw adds its raw MCAP"},
        "raw": {"include": ["raw/*.mcap"], "raw": True, "help": "every raw MCAP recording (43 TB)"},
        "custom": {"help": "your own --include / --exclude patterns"},
    },
    "8ch-mocap": {
        "starter": {"exclude": ["takes/*", "derived/*"], "help": "3 complete takes plus index, splits, loader, eval, baselines, calibration and documents"},
        "benchmark": {"include": ["takes/*/take.h5", "derived/*"], "help": "every take's HDF5 and derived estimates (tasks T1, T2, T3), no video"},
        "novideo": {"exclude": ["*.mcap"], "help": "everything except the take.mcap video containers"},
        "full": {"help": "everything, stereo video included"},
        "take": {"arg": "TAKE", "help": "one take (OP-001/s003/02), a session (OP-001/s003) or a person (OP-001); --video adds the MCAPs"},
        "supplement": {"supplement": True, "help": "the Wearable Devices fusion hand-pose predictions, outside v1.0.1 (195 MB)"},
        "custom": {"help": "your own --include / --exclude patterns"},
    },
}
# Documented starter selection of 3ch-ego (BUCKET_README.md); used only if tools/3ch-ego/starter_subset.py or
# index/3ch-ego/files.csv is unavailable, otherwise it is computed from them as the release's verifier does.
FALLBACK_3CH_STARTER_INCLUDE = [
    "starter/*", "vendor/*", "index/*.csv", "index/*.parquet", "splits/*", "eval/*", "taxonomy/*", "loader/*",
    "tests/*", "tools/*", "baseline/*", "baselines/*", "cameras/*", "provenance/*", "raw/RAW_OBJECTS.csv",
    "raw/README.md", "copy_manifest.csv", "LICENSE", "LICENSE-CODE", "MANIFEST.parquet", "BUCKET_README.md",
    "CHANGELOG.md", "CITATION.cff", "CLOCKS.md", "CONTACT.md", "DATASHEET.md", "EVALUATION.md", "GLOSSARY.md",
    "KNOWN_ISSUES.md", "POSES.md", "QUALITY_TIERS.md", "README.md", "SCHEMA.json", "SCHEMA.md", "TASK_LABELS.md",
    "TERMS.md", "VALIDATION.json", "croissant.json", "requirements-core.txt", "requirements-video.txt",
    "requirements.txt",
]
FALLBACK_3CH_STARTER_EXCLUDE = ["index/video_frames/*", "*.mcap"]


def starter_patterns_3ch():
    """The 3ch-ego starter selection as (includes, excludes), from the release's own rule and the file index."""
    try:
        sys.path.insert(0, str(rel.tools_dir("3ch-ego")))
        import starter_subset  # vendored from the 3ch-ego release

        keys = [r["key"] for r in rel.load_files("3ch-ego")]
        patterns = starter_subset.aws_patterns(keys)
        include = starter_subset.download_includes(patterns)
        exclude = [p for mode, p in patterns if mode == "exclude" and p != "*"]
        return include, exclude
    except (ImportError, SystemExit, OSError, KeyError):
        return list(FALLBACK_3CH_STARTER_INCLUDE), list(FALLBACK_3CH_STARTER_EXCLUDE)


def build_command(ds, subset, dest, info, *, item=None, raw=False, video=False, workers=None, list_only=False, extra=()):
    """The tools/<dataset>/download.py command line for a subset."""
    ds = rel.resolve(ds)
    spec = SUBSETS[ds][subset]
    cmd = [
        sys.executable, "-B", str(rel.tools_dir(ds) / "download.py"), info["base_url"], str(dest),
        "--version", info["version"], "--sums-sha256", info["sha256sums_sha256"],
    ]
    include = list(spec.get("include", []))
    exclude = list(spec.get("exclude", []))
    raw = raw or spec.get("raw", False)
    if ds == "3ch-ego" and subset == "starter":
        include, exclude = starter_patterns_3ch()
    elif ds == "3ch-ego" and subset == "clip":
        c = item
        include = [
            f"sensors/{c}.h5", f"derived/sensors_est/{c}_est.h5", f"derived/wrist_poses_est/{c}_est.h5",
            f"vendor/{c}.json", f"index/video_frames/{c}/*",
        ]
        if raw:
            include.append(f"raw/*/*/{c}.mcap")
    elif ds == "8ch-mocap" and subset == "take":
        include = [f"takes/{item}/*", f"derived/{item}/*"]
        if not video:
            exclude.append("*.mcap")
    elif ds == "8ch-mocap" and subset == "custom" and not video:
        pass  # the user's own patterns decide; --video is only a reminder that MCAPs are large
    if ds == "3ch-ego" and raw:
        cmd.append("--raw")
    if include:
        cmd += ["--include", *include]
    if exclude:
        cmd += ["--exclude", *exclude]
    if workers:
        cmd += ["--workers", str(workers)]
    if list_only:
        cmd.append("--list")
    cmd += list(extra)
    return cmd


def verify_command(ds, subset, dest):
    """The release's verifier for what was just downloaded, or None with a reason."""
    ds = rel.resolve(ds)
    verifier = rel.tools_dir(ds) / "verify_download.py"
    if ds == "3ch-ego":
        if subset == "raw":
            return None, "raw objects are checked by size and ETag as they download; tools/3ch-ego/verify_raw.py re-checks one"
        cmd = [sys.executable, "-B", str(verifier), str(dest)]
        if subset == "starter":
            cmd += ["--subset", "starter"]
        elif subset == "full":
            cmd.append("--require-all")
        return cmd, None
    if importlib.util.find_spec("pyarrow") is None:
        return None, ("tools/8ch-mocap/verify_download.py needs pyarrow (python3 -m pip install pyarrow); "
                      f"alternatively: cd {dest} && shasum -a 256 -c --ignore-missing SHA256SUMS")
    cmd = [sys.executable, "-B", str(verifier), str(dest)]
    if subset != "full":
        cmd.append("--ignore-missing")
    return cmd, None


def download_supplement(info, dest, *, list_only=False, workers=8) -> int:
    """Fetch a supplement prefix: its SHA256SUMS (checked against the published digest), then every listed file,
    each checked against its digest. Files already present and correct are skipped, so reruns resume."""
    sup = info["supplement"]
    base = f'{info["base_url"]}/{sup["prefix"]}'
    sums_bytes = rel.fetch(f"{base}/SHA256SUMS")
    digest = rel.sha256_bytes(sums_bytes)
    if digest != sup["sha256sums_sha256"]:
        print(f"{sup['prefix']}/SHA256SUMS has digest {digest}, expected {sup['sha256sums_sha256']}; refusing to continue",
              file=sys.stderr)
        return 2
    sums = rel.parse_sums(sums_bytes.decode("utf-8"))
    sizes = {r["key"]: r["bytes"] for r in rel.load_supplement_files(info["id"])}
    if list_only:
        for key in sorted(sums):
            print(f'{rel.human(sizes.get(sup["prefix"] + "/" + key)):>10}  {key}')
        total = sum(b or 0 for b in sizes.values())
        print(f"total: {len(sums) + 1} files (SHA256SUMS included), {rel.human(total) if total else 'size unknown'}",
              file=sys.stderr)
        return 0
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "SHA256SUMS").write_bytes(sums_bytes)
    done = {"downloaded": 0, "skipped": 0, "failed": 0}

    def one(item):
        key, expected = item
        path = dest / key
        if path.is_file() and rel.sha256_file(path) == expected:
            return "skipped", key
        try:
            data = rel.fetch(f"{base}/{key}")
        except SystemExit as e:
            print(f"failed {key}: {e}", file=sys.stderr)
            return "failed", key
        if rel.sha256_bytes(data) != expected:
            print(f"failed {key}: digest mismatch", file=sys.stderr)
            return "failed", key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return "downloaded", key

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers or 8)) as pool:
        for i, (state, key) in enumerate(pool.map(one, sorted(sums.items())), 1):
            done[state] += 1
            if state == "downloaded":
                print(f"[{i}/{len(sums)}] {key}", file=sys.stderr)
    print(f"{sup['name']}: downloaded {done['downloaded']} skipped {done['skipped']} failed {done['failed']} -> {dest}/",
          file=sys.stderr)
    return 1 if done["failed"] else 0


def run(cmd) -> int:
    print("+ " + " ".join(shlex.quote(c) for c in cmd), file=sys.stderr)
    return subprocess.call(cmd)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="scripts/download.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("dataset", choices=rel.DATASET_CHOICES, metavar="DATASET")
    ap.add_argument("subset", metavar="SUBSET")
    ap.add_argument("item", nargs="?", metavar="ITEM")
    ap.add_argument("--dest", metavar="DIR")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--workers", type=int, metavar="N")
    ap.add_argument("--raw", action="store_true")
    ap.add_argument("--video", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--no-verify", action="store_true")
    # Everything from the first --include / --exclude (or any other option this wrapper does not know) onwards goes to
    # tools/download.py untouched, so glob lists are never mistaken for this parser's positionals.
    argv = list(sys.argv[1:] if argv is None else argv)
    known = {"--dest", "--list", "--workers", "--raw", "--video", "--yes", "--no-verify", "-h", "--help"}
    split = next((i for i, a in enumerate(argv) if a.startswith("-") and a.split("=")[0] not in known), len(argv))
    args, extra = ap.parse_known_args(argv[:split])
    extra = list(extra) + argv[split:]

    ds = rel.resolve(args.dataset)
    subsets = SUBSETS[ds]
    if args.subset not in subsets:
        names = ", ".join(subsets)
        ap.error(f"{ds} has the subsets: {names}")
    spec = subsets[args.subset]
    if spec.get("arg"):
        if not args.item or not rel.ITEM_RE[ds].fullmatch(args.item):
            ap.error(f"{ds} {args.subset} needs a {spec['arg']} such as {rel.ITEM_EXAMPLE[ds]} "
                     f"(listed in index/{ds}/)")
    elif args.item:
        ap.error(f"unexpected argument {args.item!r}")
    if args.raw and ds != "3ch-ego":
        ap.error("--raw applies to 3ch-ego only; 8ch-mocap has no raw layer (use --video for its MCAPs)")
    if args.video and ds != "8ch-mocap":
        ap.error("--video applies to 8ch-mocap only (3ch-ego video is inside the raw MCAPs: --raw)")

    info = rel.release(ds)
    if spec.get("supplement"):
        if args.raw or args.video or extra:
            ap.error("the supplement takes only --dest, --list and --workers")
        dest = Path(args.dest or info["supplement"]["dest"])
        print(f'{info["supplement"]["name"]}  ({info["bucket"]}/{info["supplement"]["prefix"]})', file=sys.stderr)
        return download_supplement(info, dest, list_only=args.list, workers=args.workers)
    dest = Path(args.dest or info["dest"])
    if ds == "3ch-ego" and args.subset == "raw" and not (args.list or args.yes):
        print("The 3ch-ego raw layer is 4,916 MCAP objects, 43.22 TB. Most users want one clip instead:\n"
              "    python3 scripts/download.py 3ch-ego clip CLIP_ID --raw", file=sys.stderr)
        if input("Download all of it? Type yes to continue: ").strip().lower() != "yes":
            return 2

    known = info.get("subsets", {}).get(args.subset)
    print(f'{info["dataset"]} {info["version"]}  ({info["bucket"]})', file=sys.stderr)
    if known:
        print(f"{args.subset}: {known['files']:,} files, {rel.human(known['bytes'])} -> {dest}/", file=sys.stderr)
    cmd = build_command(
        ds, args.subset, dest, info, item=args.item, raw=args.raw, video=args.video, workers=args.workers,
        list_only=args.list, extra=extra,
    )
    rc = run(cmd)
    if rc != 0 or args.list or args.no_verify:
        return rc

    verify, reason = verify_command(ds, args.subset, dest)
    if verify is None:
        print(f"verification skipped: {reason}", file=sys.stderr)
        return 0
    rc = run(verify)
    if ds == "3ch-ego" and args.subset == "clip" and args.raw:
        print(f"The raw MCAP was checked by size and ETag. Re-check it any time with:\n"
              f"    python3 tools/3ch-ego/verify_raw.py {dest} {args.item}   (needs loader/ in the tree, e.g. after 'starter')",
              file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main())
