# Hosting: the R2 buckets behind this repository

For maintainers. Users never need this page.

## Where the data is

| | `3ch-ego` | `8ch-mocap` |
| --- | --- | --- |
| Dataset | EMG-1 3-channel dataset v1.0.1 | EMG-1 8-channel dataset v1.0.1 |
| Cloudflare R2 bucket | `emg1-3ch-ego-release` | `emg1-8ch-mocap-release` |
| Public base URL | `https://pub-b29550bc5a1c44e08e91624ebf1cb243.r2.dev` | `https://pub-91c561c2860c47e9b776fa8dff99271e.r2.dev` |
| Layout | `README.md` at the bucket root (the bootstrap page, outside any version prefix) and `v1.0.1/` | `BUCKET_README.md` at the bucket root, `v1.0.1/` and `supplements/` |
| Identity | `v1.0.1/SHA256SUMS` digest `724dc600…e282ed0`, published in the bucket-root README | `v1.0.1/SHA256SUMS` digest `f3b335e6…7393f8a0`, published in the bucket-root `BUCKET_README.md` and recorded in `index/8ch-mocap/RELEASE.json` |
| Raw layer | `v1.0.1/raw/<station>/<date>/<clip>.mcap`, 43.22 TB, reconciled by size and ETag in `raw/RAW_OBJECTS.csv` | none; video is inside `takes/*/take.mcap` |
| Supplements | none | `supplements/wd-fusion-predictions/v1/` (Wearable Devices predictions, own `SHA256SUMS` digest `80394007…2eb383dd`, 195 MB) |

Both buckets are the "immutable prefix" kind: objects under a published prefix are never modified, corrections
ship as a new prefix with a `CHANGELOG.md` entry. Both are served through their r2.dev development hostnames.

Public access on R2 is a hostname attached to the bucket, not a per-object ACL: everything in the bucket is
readable by anyone, and nothing can list it (hence `index/` in this repository). Enabling or disabling the hostname
happens in the Cloudflare dashboard (R2 > bucket > Settings > Public access) or with Wrangler:

```sh
npx wrangler r2 bucket dev-url enable emg1-8ch-mocap-release                                   # r2.dev subdomain
npx wrangler r2 bucket domain add emg1-8ch-mocap-release --domain data.example.com --zone-id Z  # custom domain
```

## To do on the buckets

- **Both bucket-root READMEs still say "Public base URL: to be announced"** (`README.md` in the 3ch-ego bucket,
  `BUCKET_README.md` in the 8ch-mocap bucket). Every release document and the supplement's README send readers to
  that file for the base URL and the `SHA256SUMS` digests. Regenerate them with the public URLs (the 3ch-ego
  release ships `tools/write_bucket_root_readme.py` for its own) and re-upload them at the bucket roots. Until
  then, this repository's `USAGE.md` and `index/<dataset>/RELEASE.json` are the only places that state the URLs.

## Known limits of the r2.dev hostnames

Cloudflare documents the r2.dev subdomain as development-only:

- **Rate limited** at an unpublished threshold; parallel downloaders can see HTTP 429. `tools/download.py`
  retries with backoff and honours `Retry-After`, but a busy release day may still throttle.
- **No CDN cache.** Every request reaches R2 and counts as a billable class B operation.
- **No Cloudflare features in front of it**: no Cache Rules, WAF, Access, custom TLS or redirects.
- **Random, permanent hostnames**, and `*.r2.dev` is sometimes blocked by corporate web filters because it has
  been abused for phishing.

Range requests (used by the 3ch-ego loader's `video_frame_at` to read single frames out of the raw MCAPs) and CORS
(from the bucket's CORS policy) work on it.

## Recommended before announcing widely

1. Connect a custom domain per bucket on an Encord zone (for example `emg1-3ch.encord.com` and
   `emg1-8ch.encord.com`, or one domain with two subpaths through a Worker). It removes the rate limit and puts
   Cloudflare's CDN, WAF and Cache Rules in front of the buckets.
2. Add a Cache Rule for those hostnames: cache everything, long edge TTL. Objects are immutable, so caching is
   safe. Cloudflare's cache has a per-object size limit that depends on the plan; the 9 GB raw MCAPs bypass it,
   which is fine.
3. Keep the r2.dev hostnames enabled so links already published keep working.
4. Point this repository at the new hostnames: `python3 scripts/build_index.py 3ch-ego --base-url https://...`
   (and the same for `8ch-mocap`) rewrites `index/<dataset>/RELEASE.json`, which `scripts/download.py` and
   `scripts/list_release.py` read. Regenerate the bucket-root READMEs too.

Users can override a base URL at any time with `EMG1_BASE_URL_3CH_EGO=https://...` or
`EMG1_BASE_URL_8CH_MOCAP=https://...` in the environment.

## Publishing a new dataset version

1. Build the release tree with the release's own tools (shipped under `v1.0.1/tools/` of each bucket).
2. Upload it under a new prefix, `v1.0.2/` (3ch-ego: raw objects under `v1.0.2/raw/<station>/<date>/`).
3. Regenerate the bucket-root `README.md` with the new version's `SHA256SUMS` digest.
4. In this repository: refresh the bucket listing, either `python3 scripts/list_bucket.py <dataset>` with an R2
   token (`R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, writes `bucket_objects.csv`) or a listing through the
   Cloudflare API aggregated into `index/<dataset>/bucket_structure.json` (its format is documented in
   `index/README.md`); then `python3 scripts/build_index.py <dataset> --version v1.0.2 --sums-sha256 <digest>`
   (needs pyarrow), copy the new version's `tools/*.py`, licences and root docs into `tools/<dataset>/` and
   `docs/<dataset>-v1.0.2/` (checking each copy against the new `SHA256SUMS`, as `tools/README.md` shows), update
   `README.md` and `docs/<dataset>.md`, try `python3 scripts/download.py <dataset> starter --list` and
   `python3 scripts/list_release.py <dataset> --summary`, and tag the commit.
