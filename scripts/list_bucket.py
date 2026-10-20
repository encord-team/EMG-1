#!/usr/bin/env python3
"""List every object in an EMG-1 bucket through R2's S3 API (for maintainers). The first argument says which dataset.

    R2_ACCESS_KEY_ID=... R2_SECRET_ACCESS_KEY=... python3 scripts/list_bucket.py 3ch-ego
    R2_ACCESS_KEY_ID=... R2_SECRET_ACCESS_KEY=... python3 scripts/list_bucket.py 8ch-mocap --prefix supplements/

Writes index/<dataset>/bucket_objects.csv: key, bytes, etag, last_modified, storage_class, one row per object in
the bucket, sorted by key. scripts/build_index.py then builds index/<dataset>/STRUCTURE.md from this complete
listing and cross-checks the release manifests against what the bucket really holds.

Needs an R2 API token with read access to the bucket (Cloudflare dashboard > R2 > Manage API tokens > Create,
"Object Read only" is enough), which gives an Access Key ID and a Secret Access Key. The account id defaults to
the EMG-1 account; override with CLOUDFLARE_ACCOUNT_ID. Standard library only (the request is signed with
AWS Signature Version 4, region "auto", as R2 expects). Public read access is not enough to list a bucket: R2
serves objects by key only.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import hmac
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import emg1_release as rel  # noqa: E402

DEFAULT_ACCOUNT_ID = "648e9264d754b034e3259a2587ab37e5"
FIELDS = ["key", "bytes", "etag", "last_modified", "storage_class"]
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
S3NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"


def sign(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def signed_get(host: str, path: str, params: dict, access_key: str, secret: str) -> bytes:
    """GET https://host/path?params with an AWS SigV4 signature (service s3, region auto)."""
    now = dt.datetime.now(dt.timezone.utc)
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date = now.strftime("%Y%m%d")
    scope = f"{date}/auto/s3/aws4_request"
    query = "&".join(f"{urllib.parse.quote(k, safe='-_.~')}={urllib.parse.quote(str(v), safe='-_.~')}" for k, v in sorted(params.items()))
    headers = {"host": host, "x-amz-content-sha256": EMPTY_SHA256, "x-amz-date": amz_date}
    canonical_headers = "".join(f"{k}:{headers[k]}\n" for k in sorted(headers))
    signed_headers = ";".join(sorted(headers))
    canonical = "\n".join(["GET", path, query, canonical_headers, signed_headers, EMPTY_SHA256])
    string_to_sign = "\n".join(["AWS4-HMAC-SHA256", amz_date, scope, hashlib.sha256(canonical.encode()).hexdigest()])
    k = sign(sign(sign(sign(("AWS4" + secret).encode(), date), "auto"), "s3"), "aws4_request")
    signature = hmac.new(k, string_to_sign.encode(), hashlib.sha256).hexdigest()
    headers["Authorization"] = (f"AWS4-HMAC-SHA256 Credential={access_key}/{scope}, SignedHeaders={signed_headers}, "
                                f"Signature={signature}")
    req = urllib.request.Request(f"https://{host}{path}?{query}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code} from R2: {e.read().decode('utf-8', 'replace')[:400]}") from None


def list_objects(account: str, bucket: str, access_key: str, secret: str, prefix: str | None) -> list[dict]:
    """Every object under the prefix (ListObjectsV2, following continuation tokens)."""
    host = f"{account}.r2.cloudflarestorage.com"
    rows: list[dict] = []
    token = None
    while True:
        params = {"list-type": "2", "max-keys": "1000"}
        if prefix:
            params["prefix"] = prefix
        if token:
            params["continuation-token"] = token
        root = ET.fromstring(signed_get(host, f"/{bucket}", params, access_key, secret))
        for c in root.findall(f"{S3NS}Contents"):
            rows.append({
                "key": c.findtext(f"{S3NS}Key"),
                "bytes": int(c.findtext(f"{S3NS}Size") or 0),
                "etag": (c.findtext(f"{S3NS}ETag") or "").strip('"'),
                "last_modified": c.findtext(f"{S3NS}LastModified") or "",
                "storage_class": c.findtext(f"{S3NS}StorageClass") or "",
            })
        print(f"  {len(rows):,} objects so far", file=sys.stderr)
        if (root.findtext(f"{S3NS}IsTruncated") or "false").lower() != "true":
            break
        token = root.findtext(f"{S3NS}NextContinuationToken")
        if not token:
            break
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dataset", choices=rel.DATASET_CHOICES, metavar="DATASET")
    ap.add_argument("--prefix", metavar="PREFIX", help="list only keys under this prefix (default: the whole bucket)")
    ap.add_argument("--out", type=Path, metavar="CSV", help="default: index/<dataset>/bucket_objects.csv")
    args = ap.parse_args(argv)

    access_key = os.environ.get("R2_ACCESS_KEY_ID")
    secret = os.environ.get("R2_SECRET_ACCESS_KEY")
    if not (access_key and secret):
        raise SystemExit("set R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY (an R2 API token with Object Read access)")
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", DEFAULT_ACCOUNT_ID)
    ds = rel.resolve(args.dataset)
    info = rel.release(ds)
    print(f"listing {info['bucket']} (account {account})" + (f" under {args.prefix}" if args.prefix else ""), file=sys.stderr)
    rows = sorted(list_objects(account, info["bucket"], access_key, secret, args.prefix), key=lambda r: r["key"])

    out = args.out or (rel.index_dir(ds) / "bucket_objects.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    total = sum(r["bytes"] for r in rows)
    print(f"{len(rows):,} objects, {rel.human(total)} -> {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
