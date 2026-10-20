# Window-label evaluation

Both splits use canonical one-second both-wrist windows. Per-wrist models use exactly those windows, with left features `f0` to `f23` or right features `f24` to `f47`. Within each wrist, the first 12 columns summarize EMG and the next 12 summarize band IMU. Training subsamples one in twenty windows deterministically; testing uses every eligible window. The primary split is the headline; `station_held_out` is secondary. Cross-task is experimental.

Canonical test keys are the rows of `baselines/features.parquet` whose selected split column equals `test`. Build a submission by selecting those rows, copying `clip_id,start_t_ns,station_day,label`, and adding your model output as `prediction`. The CSV header is `clip_id,start_t_ns,station_day,label,prediction`. A starter-only submission cannot be scored because it lacks the full canonical test set. Join `station_day` from `index/clips.csv`; the loader does not return it. Run `python -B eval/score.py predictions.csv --split primary --root .` to enforce the canonical test keys, labels and station-days.

Reference scores: `python -B baselines/run.py --root . --check` uses shipped features. `--recompute --check` requires all `sensors/` and `derived/sensors_est/` files (about 296.05 GB); it writes a separate recomputed file and compares it with the shipped features and metrics. `baselines/extract_features.py --split-file` only validates a supported split path and still scores both splits. For a grown release, `python -B baselines/run.py --root . --recompute --output-dir ../baseline_next` writes new features and metrics outside the shipped tree in one command.

Balanced accuracy and macro-F1 use classes with at least 30 test windows and 3 supporting station-days. Confidence intervals resample station-days 400 times with seed 20261015 and report the 2.5 and 97.5 percentiles.

| Split | Model | BA | 95% CI | Macro-F1 | 95% CI | Accuracy | Sewing/idle AUROC | Test windows |
| --- | --- | ---: | --- | ---: | --- | ---: | ---: | ---: |
| primary | Seeded chance | 0.125 | [0.123, 0.126] | 0.114 | [0.098, 0.122] | 0.125 | n/a | 137,952 |
| primary | EMG | 0.145 | [0.139, 0.150] | 0.094 | [0.068, 0.110] | 0.349 | 0.688 | 137,952 |
| primary | EMG and band IMU | 0.202 | [0.166, 0.217] | 0.189 | [0.144, 0.203] | 0.360 | 0.683 | 137,952 |
| primary | Left wrist EMG + band IMU | 0.164 | [0.155, 0.167] | 0.126 | [0.097, 0.139] | 0.355 | 0.696 | 137,952 |
| primary | Right wrist EMG + band IMU | 0.170 | [0.146, 0.180] | 0.138 | [0.102, 0.153] | 0.358 | 0.640 | 137,952 |
| primary | Majority | 0.143 | [0.143, 0.143] | 0.075 | [0.047, 0.096] | 0.358 | n/a | 137,952 |
| station_held_out | Seeded chance | 0.127 | [0.123, 0.131] | 0.110 | [0.102, 0.113] | 0.126 | n/a | 46,774 |
| station_held_out | EMG | 0.143 | [0.136, 0.148] | 0.095 | [0.084, 0.116] | 0.341 | 0.636 | 46,774 |
| station_held_out | EMG and band IMU | 0.136 | [0.089, 0.142] | 0.111 | [0.081, 0.124] | 0.232 | 0.491 | 46,774 |
| station_held_out | Left wrist EMG + band IMU | 0.146 | [0.134, 0.147] | 0.101 | [0.092, 0.117] | 0.331 | 0.528 | 46,774 |
| station_held_out | Right wrist EMG + band IMU | 0.130 | [0.110, 0.136] | 0.104 | [0.092, 0.108] | 0.246 | 0.431 | 46,774 |
| station_held_out | Majority | 0.143 | [0.143, 0.143] | 0.076 | [0.075, 0.081] | 0.364 | n/a | 46,774 |
primary test covers 10 station-days; overlock appears on 1 test station-day and is omitted from balanced accuracy and macro-F1 when below the three-day floor. Per-class support still includes it.
station_held_out test covers 7 station-days; overlock appears on 1 test station-day and is omitted from balanced accuracy and macro-F1 when below the three-day floor. Per-class support still includes it.
primary EMG balanced accuracy 0.145 has a 95% interval overlapping majority 0.143.
station_held_out EMG balanced accuracy 0.143 has a 95% interval overlapping majority 0.143.
primary balanced-accuracy intervals overlap: EMG vs majority.
station_held_out balanced-accuracy intervals overlap: EMG vs majority; EMG and band IMU vs chance; Left wrist EMG + band IMU vs majority; Right wrist EMG + band IMU vs chance.
The station-held-out intervals reflect day variation within a single test station, not station-to-station variation. Overlapping intervals are descriptive, not a formal equivalence test. These probes do not validate vendor labels.
