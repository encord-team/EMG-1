# Split files

`primary_station_day.json` is the release's primary station-day split. Partition keys are `train`, `val`, and `test`. `eval/station_held_out/split.json` is the secondary station-held-out split. `eval/cross_task/split.json` is experimental.

`norm_stats_train_only.json` was refit on the v1.0.1 primary train partition (3,488 clips; the 2,689 train clips with historical probe features enter the fit) and has 30 features. It includes clips assigned to `val` and `test` under the v1.0.1 station-held-out split and must not be used for station-held-out or cross-task evaluation. The current reference baseline uses 48 features and computes normalization from its selected training partition in `baselines/run.py`.

`eval/station_held_out/` and `eval/cross_task/norm_stats_train_only.json` contain the secondary and experimental normalization files for the historical clip-dominant probe.
