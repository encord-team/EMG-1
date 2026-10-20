# EMG-1 3-channel dataset v1.0.1 (3ch-ego): structure

Every object in the bucket `emg1-3ch-ego-release`, listed through the Cloudflare API on 2026-10-20: 49,334 objects, 43.53 TB. Compared with the release manifests (`SHA256SUMS`, `MANIFEST.parquet`, `raw/RAW_OBJECTS.csv`): objects only in the bucket: `README.md`, `v1.0.1/SHA256SUMS`; paths only in the manifests: 0; paths whose count or size differ: 0.

Paths that repeat per recording are collapsed: `<clip_id>` is a 3-channel clip such as
`20261005_egox-018_112656_888ded7e`, `<person>/<session>/<take>` is an 8-channel take such as `OP-001/s003/02`,
`<station>` and `<date>` are the raw-layer folders. Counts and sizes are totals over the collapsed paths; sizes are
decimal (GB = 10^9 bytes). Every individual key is in `files.csv` (and `raw_objects.csv`, `supplement_files.csv`,
`bucket_objects.csv` where present).

```
49,334 objects, 43.53 TB
├── v1.0.1/                                                49,333 files, 43.53 TB
│   ├── baseline/                                          6 files, 6.52 MB
│   │   ├── README.md                                      592 B
│   │   ├── features.json                                  6.12 MB
│   │   ├── metrics.json                                   4.63 kB
│   │   ├── model.npz                                      4.26 kB
│   │   ├── predictions.csv                                387.60 kB
│   │   └── reproduce.py                                   1.45 kB
│   ├── baselines/                                         6 files, 91.15 MB
│   │   ├── README.md                                      3.07 kB
│   │   ├── SUPPORT.md                                     877 B
│   │   ├── extract_features.py                            842 B
│   │   ├── features.parquet                               91.12 MB
│   │   ├── metrics.json                                   11.93 kB
│   │   └── run.py                                         12.06 kB
│   ├── cameras/                                           2 files, 708 B
│   │   ├── head_stereo.json                               210 B
│   │   └── streams.json                                   498 B
│   ├── derived/                                           9,839 files, 79.79 GB
│   │   ├── quality/                                       7 files, 45.10 MB
│   │   │   ├── SEGMENT_RULE.txt                           7.02 kB
│   │   │   ├── qc3v3.jsonl                                24.74 MB
│   │   │   ├── segment_hours_1013.txt                     8.88 kB
│   │   │   ├── segment_rule.py                            36.68 kB
│   │   │   ├── segments.jsonl                             16.83 MB
│   │   │   ├── tier_rule.py                               32.83 kB
│   │   │   └── tier_rule_tiers.jsonl                      3.45 MB
│   │   ├── sensors_est/                                   4,916 files, 64.59 GB
│   │   │   └── <clip_id>_est.h5                           4,916 files, 64.59 GB, e.g. 20260929_egox-005_060356_c7c94f56_est.h5
│   │   └── wrist_poses_est/                               4,916 files, 15.15 GB
│   │       ├── <clip_id>_est.h5                           4,914 files, 15.15 GB, e.g. 20260929_egox-005_060356_c7c94f56_est.h5
│   │       ├── availability.json                          2.39 MB
│   │       └── fragmentation.json                         442 B
│   ├── eval/                                              5 files, 692.57 kB
│   │   ├── cross_task/                                    2 files, 348.72 kB
│   │   │   ├── norm_stats_train_only.json                 136.58 kB
│   │   │   └── split.json                                 212.14 kB
│   │   ├── station_held_out/                              2 files, 340.37 kB
│   │   │   ├── norm_stats_train_only.json                 128.20 kB
│   │   │   └── split.json                                 212.18 kB
│   │   └── score.py                                       3.47 kB
│   ├── index/                                             24,586 files, 881.22 MB
│   │   ├── video_frames/                                  24,580 files, 838.27 MB
│   │   │   └── <clip_id>/                                 24,580 files, 838.27 MB
│   │   │       ├── depth.parquet                          4,916 files, 8.35 MB
│   │   │       ├── head_left.parquet                      4,916 files, 804.80 MB
│   │   │       ├── head_right.parquet                     4,916 files, 8.37 MB
│   │   │       ├── wrist_left.parquet                     4,916 files, 8.37 MB
│   │   │       └── wrist_right.parquet                    4,916 files, 8.38 MB
│   │   ├── clips.csv                                      12.71 MB
│   │   ├── clips.parquet                                  1.56 MB
│   │   ├── segments.csv                                   22.23 MB
│   │   ├── segments.parquet                               1.15 MB
│   │   ├── video_streams.csv                              5.07 MB
│   │   └── video_streams.parquet                          225.18 kB
│   ├── loader/                                            4 files, 31.68 kB
│   │   ├── emg1_ego/                                      2 files, 28.77 kB
│   │   │   ├── __init__.py                                17.50 kB
│   │   │   └── video.py                                   11.27 kB
│   │   ├── README.md                                      2.15 kB
│   │   └── example.py                                     758 B
│   ├── provenance/                                        2 files, 7.15 kB
│   │   ├── METHODS.md                                     4.41 kB
│   │   └── publish.py                                     2.74 kB
│   ├── raw/                                               4,918 files, 43.22 TB
│   │   ├── <station>/                                     4,916 files, 43.22 TB
│   │   │   └── <date>/                                    4,916 files, 43.22 TB
│   │   │       └── <clip_id>.mcap                         4,916 files, 43.22 TB, e.g. 20260929_egox-005_060356_c7c94f56.mcap
│   │   ├── RAW_OBJECTS.csv                                782.21 kB
│   │   └── README.md                                      4.76 kB
│   ├── sensors/                                           4,916 files, 231.46 GB
│   │   └── <clip_id>.h5                                   4,916 files, 231.46 GB, e.g. 20260929_egox-005_060356_c7c94f56.h5
│   ├── splits/                                            3 files, 329.44 kB
│   │   ├── README.md                                      900 B
│   │   ├── norm_stats_train_only.json                     113.53 kB
│   │   └── primary_station_day.json                       215.01 kB
│   ├── starter/                                           62 files, 1.32 GB
│   │   ├── derived/                                       40 files, 337.02 MB
│   │   │   ├── sensors_est/                               20 files, 274.99 MB
│   │   │   │   └── <clip_id>_est.h5                       20 files, 274.99 MB, e.g. 20260929_egox-011_105918_8d906897_est.h5
│   │   │   └── wrist_poses_est/                           20 files, 62.03 MB
│   │   │       └── <clip_id>_est.h5                       20 files, 62.03 MB, e.g. 20260929_egox-011_105918_8d906897_est.h5
│   │   ├── sensors/                                       20 files, 981.75 MB
│   │   │   └── <clip_id>.h5                               20 files, 981.75 MB, e.g. 20260929_egox-011_105918_8d906897.h5
│   │   ├── clips.json                                     1.00 kB
│   │   └── raw_copy_keys.csv                              3.18 kB
│   ├── taxonomy/                                          2 files, 123.98 kB
│   │   ├── KEYWORD_RULES.md                               899 B
│   │   └── title_to_category_v1.json                      123.08 kB
│   ├── tests/                                             4 files, 41.56 kB
│   │   ├── test_acceptance.py                             19.00 kB
│   │   ├── test_open_release.py                           4.44 kB
│   │   ├── test_revision.py                               10.89 kB
│   │   └── test_v2.py                                     7.22 kB
│   ├── tools/                                             33 files, 149.82 kB
│   │   ├── bucket_readme.py                               1.52 kB
│   │   ├── build_checksums.py                             1.21 kB
│   │   ├── build_croissant.py                             2.38 kB
│   │   ├── build_raw_objects.py                           2.21 kB
│   │   ├── build_schema.py                                21.91 kB
│   │   ├── build_validation.py                            2.90 kB
│   │   ├── camera_specs.py                                1.52 kB
│   │   ├── check_copy_plan.py                             568 B
│   │   ├── check_symlinks.py                              911 B
│   │   ├── check_taxonomy.py                              552 B
│   │   ├── check_vendor_segments.py                       905 B
│   │   ├── clock_audit.py                                 733 B
│   │   ├── download.py                                    47.16 kB
│   │   ├── finalize_raw_and_checksums.py                  1.23 kB
│   │   ├── infer_part_size.py                             631 B
│   │   ├── method_constants.py                            558 B
│   │   ├── pose_coverage.py                               754 B
│   │   ├── pose_timing_stats.py                           622 B
│   │   ├── regenerate_docs.py                             37.52 kB
│   │   ├── release_stats.py                               3.74 kB
│   │   ├── scan_prior_account_patterns.py                 1.42 kB
│   │   ├── scan_privacy.py                                6.30 kB
│   │   ├── simulate_starter.py                            1.00 kB
│   │   ├── starter_subset.py                              1.52 kB
│   │   ├── support_table.py                               520 B
│   │   ├── task_stats.py                                  865 B
│   │   ├── test_publish.py                                2.40 kB
│   │   ├── test_raw_finalize.py                           784 B
│   │   ├── tier_constants.py                              401 B
│   │   ├── verify_download.py                             1.16 kB
│   │   ├── verify_raw.py                                  798 B
│   │   ├── verify_release.py                              1.28 kB
│   │   └── write_bucket_root_readme.py                    1.88 kB
│   ├── vendor/                                            4,919 files, 7.03 MB
│   │   ├── <clip_id>.json                                 4,916 files, 5.15 MB, e.g. 20260929_egox-005_060356_c7c94f56.json
│   │   ├── segments.csv                                   1.57 MB
│   │   ├── segments.parquet                               202.13 kB
│   │   └── titles.csv                                     117.94 kB
│   ├── BUCKET_README.md                                   6.95 kB
│   ├── CHANGELOG.md                                       2.29 kB
│   ├── CITATION.cff                                       722 B
│   ├── CLOCKS.md                                          2.60 kB
│   ├── CONTACT.md                                         592 B
│   ├── DATASHEET.md                                       5.77 kB
│   ├── EVALUATION.md                                      4.39 kB
│   ├── GLOSSARY.md                                        2.58 kB
│   ├── KNOWN_ISSUES.md                                    4.45 kB
│   ├── LICENSE                                            19.94 kB
│   ├── LICENSE-CODE                                       11.36 kB
│   ├── MANIFEST.parquet                                   1.96 MB
│   ├── POSES.md                                           1.50 kB
│   ├── QUALITY_TIERS.md                                   2.82 kB
│   ├── README.md                                          7.88 kB
│   ├── SCHEMA.json                                        108.88 kB
│   ├── SCHEMA.md                                          48.18 kB
│   ├── SHA256SUMS                                         5.75 MB
│   ├── TASK_LABELS.md                                     2.00 kB
│   ├── TERMS.md                                           2.60 kB
│   ├── VALIDATION.json                                    1.38 kB
│   ├── copy_manifest.csv                                  605.28 kB
│   ├── croissant.json                                     63.95 kB
│   ├── requirements-core.txt                              111 B
│   ├── requirements-video.txt                             52 B
│   └── requirements.txt                                   416 B
└── README.md                                              7.55 kB
```
