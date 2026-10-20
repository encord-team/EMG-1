# EMG-1 8-channel dataset v1.0.1 (8ch-mocap): structure

Every object in the bucket `emg1-8ch-mocap-release`, listed through the Cloudflare API on 2026-10-20: 4,229 objects, 217.50 GB. Compared with the release manifests (`SHA256SUMS`, `MANIFEST.parquet`, the supplement's `SHA256SUMS`): objects only in the bucket: `BUCKET_README.md`, `v1.0.1/SHA256SUMS`; paths only in the manifests: 0; paths whose count or size differ: 0.

Paths that repeat per recording are collapsed: `<clip_id>` is a 3-channel clip such as
`20261005_egox-018_112656_888ded7e`, `<person>/<session>/<take>` is an 8-channel take such as `OP-001/s003/02`,
`<station>` and `<date>` are the raw-layer folders. Counts and sizes are totals over the collapsed paths; sizes are
decimal (GB = 10^9 bytes). Every individual key is in `files.csv` (and `raw_objects.csv`, `supplement_files.csv`,
`bucket_objects.csv` where present).

```
4,229 objects, 217.50 GB
├── supplements/                                           401 files, 194.65 MB
│   └── wd-fusion-predictions/                             401 files, 194.65 MB
│       └── v1/                                            401 files, 194.65 MB
│           ├── fusion_delivery_v10/                       398 files, 194.55 MB
│           │   ├── predictions/                           391 files, 193.24 MB
│           │   │   └── <person>__<session>__<take>_fusion.csv 391 files, 193.24 MB, e.g. OP-001__s003__01_fusion.csv
│           │   ├── GUIDE.md                               21.36 kB
│           │   ├── README.md                              5.31 kB
│           │   ├── SHA256SUMS                             41.94 kB
│           │   ├── calibration_manifest.json              106.44 kB
│           │   ├── hand_model.json                        27.00 kB
│           │   ├── marker_layout.png                      1.07 MB
│           │   └── per_take_metrics.csv                   41.49 kB
│           ├── LICENSE                                    20.47 kB
│           ├── README.md                                  28.90 kB
│           └── SHA256SUMS                                 50.13 kB
├── v1.0.1/                                                3,827 files, 217.30 GB
│   ├── baselines/                                         31 files, 735.49 MB
│   │   ├── contact_results/                               12 files, 13.02 MB
│   │   │   └── fold_<NN>.npz                              12 files, 13.02 MB, e.g. fold_00.npz
│   │   ├── results/                                       12 files, 722.45 MB
│   │   │   └── fold_<NN>.npz                              12 files, 722.45 MB, e.g. fold_00.npz
│   │   ├── README.md                                      2.15 kB
│   │   ├── T1_metrics.json                                5.36 kB
│   │   ├── T2_metrics.json                                7.47 kB
│   │   ├── frozen_config.json                             2.58 kB
│   │   ├── probe.py                                       2.01 kB
│   │   ├── reproduce.py                                   938 B
│   │   └── run.py                                         4.36 kB
│   ├── calibration/                                       12 files, 839.72 kB
│   │   └── <person>_Left.motive                           12 files, 839.72 kB, e.g. OP-001_Left.motive
│   ├── derived/                                           920 files, 4.81 GB
│   │   └── <person>/                                      920 files, 4.81 GB
│   │       └── <session>/                                 920 files, 4.81 GB
│   │           └── <take>/                                920 files, 4.81 GB
│   │               └── automatic_est.h5                   920 files, 4.81 GB
│   ├── eval/                                              12 files, 34.02 kB
│   │   ├── TASKS.md                                       4.41 kB
│   │   ├── __init__.py                                    0 B
│   │   ├── geom.py                                        1.31 kB
│   │   ├── make_targets.py                                2.44 kB
│   │   ├── probe_targets.py                               1.78 kB
│   │   ├── score.py                                       4.91 kB
│   │   ├── test_twelve_folds.py                           2.33 kB
│   │   ├── tests.py                                       1.70 kB
│   │   ├── vision.py                                      4.46 kB
│   │   ├── vision_core.py                                 8.20 kB
│   │   ├── vision_metrics.json                            470 B
│   │   └── vision_tests.py                                2.02 kB
│   ├── index/                                             7 files, 747.25 kB
│   │   ├── aggregate_facts.json                           555 B
│   │   ├── index_facts.json                               1.78 kB
│   │   ├── input_disposition.parquet                      33.91 kB
│   │   ├── takes.csv                                      568.48 kB
│   │   ├── takes.parquet                                  66.33 kB
│   │   ├── takes_extra.csv                                63.01 kB
│   │   └── takes_extra.parquet                            13.19 kB
│   ├── loader/                                            6 files, 16.99 kB
│   │   ├── README.md                                      2.73 kB
│   │   ├── dataset.py                                     2.85 kB
│   │   ├── golden.json                                    825 B
│   │   ├── quickstart.py                                  1.57 kB
│   │   ├── reader.py                                      4.39 kB
│   │   └── tests.py                                       4.62 kB
│   ├── reference/                                         6 files, 16.66 kB
│   │   └── t1_probe/                                      6 files, 16.66 kB
│   │       ├── README.md                                  965 B
│   │       ├── p8_extract.log                             155 B
│   │       ├── p8_model.log                               4.17 kB
│   │       ├── probe8_extract.py                          4.47 kB
│   │       ├── probe8_model.py                            4.90 kB
│   │       └── probe8_model2.py                           2.01 kB
│   ├── splits/                                            28 files, 534.80 kB
│   │   ├── default_smoke.json                             20.48 kB
│   │   ├── default_smoke_norm.json                        15.22 kB
│   │   ├── loso_fold_<NN>.json                            12 files, 245.48 kB, e.g. loso_fold_00.json
│   │   ├── loso_fold_<NN>_norm.json                       12 files, 218.22 kB, e.g. loso_fold_00_norm.json
│   │   ├── within_person_session.json                     20.46 kB
│   │   └── within_person_session_norm.json                14.93 kB
│   ├── starter/                                           10 files, 607.38 MB
│   │   ├── <person>/                                      9 files, 607.38 MB
│   │   │   └── <session>/                                 9 files, 607.38 MB
│   │   │       └── <take>/                                9 files, 607.38 MB
│   │   │           ├── take.c3d                           3 files, 6.66 MB
│   │   │           ├── take.h5                            3 files, 83.69 MB
│   │   │           └── take.mcap                          3 files, 517.03 MB
│   │   └── takes.json                                     63 B
│   ├── takes/                                             2,760 files, 211.14 GB
│   │   └── <person>/                                      2,760 files, 211.14 GB
│   │       └── <session>/                                 2,760 files, 211.14 GB
│   │           └── <take>/                                2,760 files, 211.14 GB
│   │               ├── take.c3d                           920 files, 2.39 GB
│   │               ├── take.h5                            920 files, 27.24 GB
│   │               └── take.mcap                          920 files, 181.51 GB
│   ├── tools/                                             9 files, 76.58 kB
│   │   ├── croissant.py                                   7.42 kB
│   │   ├── doc_stats.py                                   903 B
│   │   ├── download.py                                    47.16 kB
│   │   ├── index_dictionary.py                            12.43 kB
│   │   ├── marker_table.py                                1.01 kB
│   │   ├── metadata.py                                    2.98 kB
│   │   ├── tests.py                                       1.54 kB
│   │   ├── validate_layout.py                             1.69 kB
│   │   └── verify_download.py                             1.45 kB
│   ├── BUCKET_README.md                                   4.74 kB
│   ├── BUILD_PROVENANCE.json                              6.22 kB
│   ├── CHANGELOG.md                                       5.48 kB
│   ├── CITATION.cff                                       700 B
│   ├── CONTACT.md                                         648 B
│   ├── DATASHEET.md                                       6.28 kB
│   ├── GLOSSARY.md                                        2.48 kB
│   ├── INDEX_DICTIONARY.md                                10.40 kB
│   ├── KNOWN_ISSUES.md                                    4.68 kB
│   ├── LICENSE                                            20.00 kB
│   ├── LICENSE-CODE                                       11.36 kB
│   ├── MANIFEST.parquet                                   166.28 kB
│   ├── MARKERS.md                                         3.53 kB
│   ├── QUALITY_TIERS.md                                   2.33 kB
│   ├── README.md                                          8.21 kB
│   ├── SCHEMA.json                                        65.21 kB
│   ├── SCHEMA.md                                          21.16 kB
│   ├── SHA256SUMS                                         375.81 kB
│   ├── TERMS.md                                           2.67 kB
│   ├── VALIDATION.json                                    630 B
│   ├── clock_epochs.json                                  7.44 kB
│   ├── croissant.json                                     81.13 kB
│   ├── hours.json                                         447 B
│   ├── requirements.txt                                   155 B
│   ├── selection_waterfall.json                           367.87 kB
│   └── thresholds.json                                    591 B
└── BUCKET_README.md                                       4.00 kB
```
