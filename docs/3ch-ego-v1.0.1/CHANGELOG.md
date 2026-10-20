# v1.0.1

Release date: 2026-10-20.

## Licence

v1.0.1 is released free and open. The data are licensed under CC BY 4.0 and the source code (every `.py` file and `requirements*.txt`) under Apache-2.0; see `LICENSE`, `LICENSE-CODE` and `TERMS.md`. No account, access key or agreement is needed, and files are served over public HTTPS. Earlier staging copies of v1.0.1 granted no licence. Until 2026-10-19, staging copies of v1.0.1 were prepared for controlled access; that plan was dropped before release.

## Clips

v1.0.1 has 4,916 clips, 1,112 more than the 3,804 clips of v1.0.0. The first increment added 1,066 recordings, for 4,870 clips cumulative. The final top-up adds 46 recordings since the first increment; they were recorded on 2026-10-12 and 2026-10-13, uploaded on 2026-10-16 and included up to the cutoff of 2026-10-17 23:59:59 UTC. Existing clip split assignments and quality thresholds remain fixed. Station-days that were new in the first increment were placed whole by the seeded rule recorded in `splits/primary_station_day.json`. The final top-up adds no new station-days: all 46 of its recordings fall on station-days already in the release and take their partitions.

## Raw recordings

The copy plan in `copy_manifest.csv` lists 4,916 raw MCAP objects (43.22 TB). The raw objects are reconciled by destination key, size and ETag in `raw/RAW_OBJECTS.csv`.

## Derived files

The historical clip-dominant probe and primary train-only normalization were refit on the v1.0.1 primary train partition (3,488 clips; the 2,689 train clips with historical probe features enter the fit). The `station_held_out` and `cross_task` train-only normalizations were refit on their own train partitions (3,048 and 3,255 fit clips). The window-level reference benchmark, canonical scorer, schema, and integrity files describe the cumulative release.

The frozen rule files in `derived/quality/` (`SEGMENT_RULE.txt`, `tier_rule.py` and `segment_rule.py`) are byte-identical to the rules that produced the tiers and segments, so `rule_sha256_16` in `segments.jsonl` matches the shipped `segment_rule.py`; staging copies had edited comments. `derived/quality/segment_hours_1013.txt` is the 2026-10-13 report for the first 3,804 clips; its first line relates it to the release totals.
