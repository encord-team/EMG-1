# Changelog

## v1.0.1

920 takes from 12 people, 15.036 recording-window hours, selected from a vendor snapshot frozen at 2026-10-16 02:58 UTC. Relative to v1.0.0 this adds 277 takes, including 2 new people, and makes the changes below. All research metrics are regenerated under frozen model recipes. This build supersedes a 643-take staging build of v1.0.1 that was uploaded on 2026-10-15 for internal review and not distributed.

v1.0.1 was released on 2026-10-20 as a free and open dataset. Source code files (`*.py` and requirements files) are licensed under Apache-2.0 (`LICENSE-CODE`) and every other file under CC BY 4.0 (`LICENSE`); `CITATION.cff`, `CONTACT.md` and `TERMS.md` give the citation, contact and attribution terms. Downloads use `tools/download.py` with the base URL from the bucket-root README. Before public release, the documentation, licence files, citation and Croissant metadata were revised for open distribution and `tools/download.py` was added; that revision changed no take, derived, index, split, starter or calibration data. The `access` value embedded in the take files was therefore left as packaged and is superseded by `LICENSE`; see `KNOWN_ISSUES.md`.

- Automatic MediaPipe stereo estimates now cover 919 of 920 takes (v1.0.0: 252); 391 previously released takes gain them. Re-running the pinned vision chain reproduced earlier estimates to within 1 micrometre for 130 takes and changed 5 materially (OP-006/s004/04, OP-006/s004/05, OP-006/s004/08, OP-009/s002/13, OP-009/s002/14); see `KNOWN_ISSUES.md`.
- Band-to-mocap lag and the marker identity checks are now evaluated on every take with pinned code and reproduce the earlier per-take results. Lag is measured for 863 of 920 takes. The 5 previously released boundary fits are withheld (applied lag 0, `lag_boundary_unmeasured`).
- `splits/loso_fold_09.json` reassigns previously released takes (120 val to train), following the documented split rules applied to the enlarged cohort.
- `splits/within_person_session.json` reassigns previously released takes (15 test to excluded, 59 test to train, 30 val to train), following the documented split rules applied to the enlarged cohort.
- The subject-relative clock epoch of 7 takes (OP-005/s007/09-15) moves by up to 0.156 s and its stated uncertainty rises by 3.6 ms, because a vendor re-decision changed a clock anchor in their session; see `KNOWN_ISSUES.md`.
- 15 previously released takes (OP-008/s001/01-15) change `has_marker_fixes` because the vendor re-exported their marker files with corrected labels.
- 22 `take.mcap` files of previously released takes change only in their `/meta` summary message; video payloads are unchanged, and the matching `video/mcap_byte_offset` values in `take.h5` shift by the summary length change.
- Embedded vendor source records of previously released takes are refreshed from the frozen snapshot: session index (`session.index.json`) in 184, session log in 15, embedded person calibration in 72, vendor decision record (`decision.json`) in 163, raw marker labels in 15 takes. The vendor updated the calibration files of OP-008, OP-009, OP-010. Every embedded `manifest.json` drops its per-person subject block and every take drops `subject.yaml`.
- The starter set changes: OP-001/s003/01, OP-001/s007/01, OP-002/s008/01 replaced by OP-001/s003/02, OP-001/s016/11, OP-010/s001/07.
- `selection_waterfall.json` grows from 825 to 1130 records; 10 v1.0.0 records no longer appear under their old paths because the vendor moved or re-decided those recordings, and 41 existing records change their reason or category.
- Train-only normalization statistics are recomputed for 12 split files.
- `index/input_disposition.parquet` no longer lists raw input digests or sizes, which could confirm guesses of redacted or withheld values. Vision provenance lists raw-input digests for binary video inputs only; digests of code, calibration configuration and intermediate results remain.
- Rejections newer than the curated rejection taxonomy carry the short vendor decision reason under category `vendor_decision_reason_uncurated`.
- Every take records the withheld per-person `subject.yaml` in `meta/omissions`.

Corrections and additions since v1.0.0 that predate this rebuild:

The pre-release take and derived HDF5 containers were rebuilt for h5py >= 3.0 / HDF5 >= 1.10. Boundary lag corrections were withheld; MCAP pointers, arrival categories, within-person split rules and index flag names were corrected. The readiness and acceptance revisions did not change sensor values or HDF5 files.

This revision adds a dataset card, datasheet, glossary, marker and index dictionaries, quality-tier rules, contact-first task protocol, numpy vision scorer, frozen all-take LOSO baselines, partial-download verifier, Croissant metadata and a take metadata sidecar. The loader now supports starter-only layouts, explicit missing-file handling, a wrist-frame target and per-worker HDF5 caching with slice reads. Default world-frame outputs retain their prior values. Native TAK and SVO2 files are not included in v1.0.1.

## v1.0.0

Initial 643-take controlled-access dataset with raw and canonical marker representations, sensor and camera streams, automatic estimates, person and session splits, train-only normalization, provenance and checksums.

Legacy 1.0.0 version strings remain in HDF5 attributes, normalization JSON files, `SCHEMA.json` single-take examples and `canonical-R1-1.0.0` marker labels.
