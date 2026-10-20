# EMG-1 fusion hand-pose predictions (Wearable Devices)

A supplement to the EMG-1 8-channel dataset, v1.0.1. Supplement version 1.

- Published: 2026-10-20
- Location: the prefix `supplements/wd-fusion-predictions/v1/` in the EMG-1 8-channel bucket. It sits outside the frozen `v1.0.1/` prefix, changes no dataset file, and the dataset's `tools/download.py` does not fetch it.
- Maintainer: Vineeth Velmurugan, Encord. Contact: support@encord.com.

## What this is

Frame-by-frame predictions of 20 left-hand finger joint angles, in degrees, for 391 of the 920 v1.0.1 takes. They come from 8 of the 12 EMG-1 people (OP-001 to OP-008). The models that made them fuse the 8-channel EMG band with the ZED camera. Each person's model was trained on the other 7 of these 8 people, never on the person it predicts. It was then calibrated on about 2 minutes of that person's own motion-capture-labelled data. This is a reference result for new-person hand pose with a short labelled calibration. It is not a submission to EMG-1 tasks T1, T2 or T3 (`eval/TASKS.md`), and its numbers are not comparable with theirs.

## Who made it

Wearable Devices made these predictions. It trained the models and produced the predictions, the per-take metrics, the hand model, the marker diagram and the guide in `fusion_delivery_v10/`. Wearable Devices is also the company that collected the EMG-1 recordings. Encord checked the delivery, converted its time stamps to the EMG-1 clock, removed the takes that are not in v1.0.1, and publishes this supplement. Rights holders: Wearable Devices Ltd. for the files in `fusion_delivery_v10/` other than its `SHA256SUMS`, and Encord for this README, the `LICENSE` header and the two `SHA256SUMS` files.

## Relationship to EMG-1 v1.0.1

This supplement changes no file of EMG-1 8-channel v1.0.1, and the dataset's downloader, `tools/download.py`, does not fetch it. It has its own prefix, README, LICENSE and checksums. To score the predictions you also need the take files of v1.0.1 (see "Fetching the files").

## What Encord changed in the delivery

- **Time stamps are on the EMG-1 clock.** The delivered time column, `t_lsl_ns`, was on the recording computer's raw LSL clock. For each take, Encord subtracted the origin of the take's clock epoch (`clock_epoch_id` in `index/takes.csv`), the same exact integer shift that v1.0.1 applies to every stream of that take, and renamed the column `t_ns`. Every other byte of every prediction CSV is as delivered, and the row counts and row order are unchanged. In `calibration_manifest.json`, the two time fields of each calibration take, `from_t_lsl_ns` and `to_t_lsl_ns`, were converted the same way and renamed `from_t_ns` and `to_t_ns`. The raw values are not published, because they reveal the order and spacing of different people's recordings and the clock origins that v1.0.1 keeps private.
- **Takes outside v1.0.1 were removed.** The delivery predicted 455 takes. 64 of them are not in v1.0.1: 55 were excluded when the v1.0.1 recordings were selected (see the dataset's `selection_waterfall.json`), and 9 (OP-003 sessions s003 and s004) are from recordings that were never delivered to Encord, so they are not in the dataset. Their prediction files and `per_take_metrics.csv` rows were removed, and their IDs were removed from the manifest's `scored.same_session` and `scored.new_session` lists. The 6 calibration takes that are not in v1.0.1 (OP-003/s001) keep `trial_id`, `frames` and `whole_take`, lose their two time fields, and carry `"in_v1_0_1": false`. Every other calibration take carries `"in_v1_0_1": true`. The manifest's `training.takes` and `takes_without_valid_window` lists are unchanged; they hold IDs only. 62 of the 427 distinct training takes are not in v1.0.1.
- **`per_joint_metrics.csv` is withheld until it is recomputed on the v1.0.1 takes.** The delivered file pools scored rows from up to 59 of the 64 removed takes (the other 5, all in OP-003/s001, have calibration rows only), including every same-session row of OP-003, and it cannot be recomputed from the per-take rows. Wearable Devices has not stated yet whether it will provide a recomputed file.
- **Line 3 of `README.md` and `GUIDE.md`** now reads `Wearable Devices, 2026-10-14.` A sentence that restricted sharing was removed from it. Wearable Devices approved publishing its files under CC BY 4.0 with that sentence removed.
- **Line 154 of `GUIDE.md`**, in the section 5 manifest excerpt, gave the end of the calibration in `OP-002/s001/06` on the raw clock. That number was replaced by `...`, as the excerpt already does for the other times, because together with the converted times it would reveal a private clock origin. Wearable Devices approved this change.
- No other line of the two vendor documents was changed. Corrections to their text are listed under Errata below.
- **Checksums.** `fusion_delivery_v10/SHA256SUMS` was regenerated over the files shipped here only. The top-level `SHA256SUMS` covers every other file in this supplement. The delivery's zip archive is not published.
- `hand_model.json` and `marker_layout.png` are unchanged.

## Inputs and protocol

- **Inputs for each camera frame.** The model sees 1 s of 8-channel EMG centred on the frame time, plus the ZED camera's view of the hand at that frame. The window includes 0.5 s of EMG after the frame, so the predictions are offline. Wearable Devices did not specify the camera hand-pose component.
- **Band-to-mocap alignment.** Wearable Devices has not stated yet which band-to-mocap alignment it used. For comparison, v1.0.1 applies a per-take band-to-mocap lag (`lag_ms` in `index/takes.csv`); for the 344 of the 391 predicted takes with a measured lag it has median 28 ms and range -112 to 200 ms.
- **No camera hand.** When the camera found no hand, the frame was predicted from EMG alone. These frames are not flagged. Wearable Devices reports that they make up 0 to 2.4% of a person's frames; Encord has not checked this.
- **One model per person.** Each model was trained on the other 7 of these 8 people, with motion-capture joint angles as labels, and never saw a take of the person it predicts (checked for all 8 models in `calibration_manifest.json`).
- **Calibration of a new person.** The calibration used the first 120 s of 1 s windows that have both a camera hand and a valid motion-capture label (Encord infers the label condition from the data; see Errata item 6), takes in recording order. It used the first session of the person in the data that the models used: s003 for OP-001 and s002 for OP-004, whose earlier sessions are not in v1.0.1 and were not used by the models; s001 for the other 6 people, including OP-003, whose s001 is not in v1.0.1 but was used. Every frame up to 1 s after the last calibration window has role `calibration`. Calibration needs motion capture of the new person, so this is not a calibration-free result.
- **Angles.** The 20 angles are defined from the OptiTrack skin markers in `fusion_delivery_v10/GUIDE.md` section 6. Wearable Devices scored against angles from its own processing of the marker data.

## Coverage

Each prediction row has a `role`:

- `calibration`: the model was calibrated on this row. Never score it.
- `scored_same_session`: the rest of the calibration session.
- `scored_new_session`: later sessions, after the band was taken off and put on again. Some of them were recorded within 5 hours of the calibration session, one about 10 minutes after it (see Errata item 17).

| Person | Calibration session | Calibration span | v1.0.1 takes | Predicted v1.0.1 takes | Calibration-only takes | Same-session takes | Later-session takes | Scored takes without vendor metrics | v1.0.1 takes without predictions |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| OP-001 | s003 | 128.7 s, 5 takes | 120 | 120 | 4 | 6 | 110 | 0 | 0 |
| OP-002 | s001 | 138.8 s, 3 takes | 216 | 87 | 2 | 9 | 76 | 7 | 129 |
| OP-003 | s001, not in v1.0.1 | 154.3 s, 6 takes, none in v1.0.1 | 77 | 2 | 0 | 0 | 2 | 0 | 75 |
| OP-004 | s002 | 236.7 s, 5 takes | 75 | 75 | 4 | 10 | 61 | 2 | 0 |
| OP-005 | s001 | 469.0 s, 9 takes; 6 without a labelled window | 155 | 25 | 8 | 6 | 11 | 5 | 130 |
| OP-006 | s001 | 123.2 s, 3 takes | 81 | 52 | 2 | 13 | 37 | 2 | 29 |
| OP-007 | s001 | 122.7 s, 3 takes | 15 | 15 | 2 | 13 | 0 | 0 | 0 |
| OP-008 | s001 | 242.2 s, 5 takes; 2 without a labelled window | 45 | 15 | 4 | 11 | 0 | 2 | 30 |
| OP-009 to OP-012 | none | none | 136 | 0 | 0 | 0 | 0 | 0 | 136 |
| Total | | | 920 | 391 | 26 | 68 | 297 | 18 | 529 |

How to read the table:

- Calibration span is the time covered by `calibration` rows, summed over the calibration takes, as in GUIDE section 3.3. It is computed from the delivered manifest and includes takes that are not shipped.
- The take in which the calibration ends starts with `calibration` rows and counts as a same-session take. Each person from OP-001 to OP-008 except OP-003 has one such take.
- Scored takes without vendor metrics have scored rows but empty metric fields in `per_take_metrics.csv` (see Errata item 11).
- The 393 v1.0.1 takes of OP-001 to OP-008 without predictions (OP-002 129, OP-003 75, OP-005 130, OP-006 29, OP-008 30) were not in the data that the models used: no model trained on them or predicted them, and no list in `calibration_manifest.json` names them.
- OP-009 to OP-012 were seen by no model and have no predictions.

Rows per person and role:

| Person | Rows | Calibration | Scored same-session | Scored later-session |
|---|---:|---:|---:|---:|
| OP-001 | 300,709 | 7,238 | 8,802 | 284,669 |
| OP-002 | 289,470 | 7,559 | 26,199 | 255,712 |
| OP-003 | 3,091 | 0 | 0 | 3,091 |
| OP-004 | 222,075 | 7,762 | 20,470 | 193,843 |
| OP-005 | 80,960 | 26,425 | 19,880 | 34,655 |
| OP-006 | 173,473 | 7,388 | 45,036 | 121,049 |
| OP-007 | 53,047 | 7,289 | 45,758 | 0 |
| OP-008 | 50,877 | 13,923 | 36,954 | 0 |
| Total | 1,173,702 | 77,584 | 203,099 | 893,019 |

For each person, every row outside the calibration span is held out from that person's model, but every person's takes trained the other 7 models.

## Files

| Path | Content |
|---|---|
| `README.md` | this page |
| `LICENSE` | licence for this supplement |
| `SHA256SUMS` | SHA-256 of every other file in this supplement |
| `fusion_delivery_v10/README.md`, `fusion_delivery_v10/GUIDE.md` | Wearable Devices' summary and full guide, unchanged except line 3 of both and line 154 of `GUIDE.md` (see "What Encord changed") |
| `fusion_delivery_v10/predictions/OP-xxx__sNNN__TT_fusion.csv` | 391 files, one per take, one row per ZED frame that has a full 1 s EMG window |
| `fusion_delivery_v10/per_take_metrics.csv` | Wearable Devices' accuracy per take, on scored rows only; header plus 391 rows as delivered |
| `fusion_delivery_v10/calibration_manifest.json` | per person: training takes, calibration takes and cut times, scored takes |
| `fusion_delivery_v10/hand_model.json` | per person: segment lengths and bend rolls, used only for the mm metric |
| `fusion_delivery_v10/marker_layout.png` | Wearable Devices' schematic of the marker positions on the back of a left hand |
| `fusion_delivery_v10/SHA256SUMS` | SHA-256 of every other file in `fusion_delivery_v10/` |

Prediction columns:

- `trial_id`: text, `OP-xxx/sNNN/TT`. This equals the `source` column of `index/takes.csv` and the take's path under `takes/`; the index `take_id` is `OP-xxx_sNNN_TT`.
- `t_ns`: int64 nanoseconds on the take's EMG-1 clock, the same clock as the take's `/video/t_ns` and `/markers/t_ns`. It increases strictly within each file.
- `role`: as above.
- 20 columns ending in `_deg`: degrees, 2 decimals, not clipped.

The CSVs are comma-separated with one header row, ASCII and LF line endings. Column names contain dots.

Other fields:

- `per_take_metrics.csv` `median_mm` and `p95_mm` are means over 15 joint positions of the per-joint median and P95.
- In `calibration_manifest.json`, `calibration.takes[].frames` counts the calibration rows of that take, not all of its frames.
- `hand_model.json` `takes` and `frames` count every take of the person with valid markers in the data that the models used, including takes that are not in v1.0.1 (OP-001 147 takes, OP-003 20, OP-004 90) and the scored takes themselves.
- `base_to_knuckle` means marker `_1` to `_2`.
- An empty field means not computed.

Wearable Devices has not stated yet how `mean_mm` and `fk_floor_mm.n` in `hand_model.json` are defined.

## Fetching the files

Start in the folder that holds your EMG-1 release folder `emg1-8ch-v1.0.1` (the `emg1` folder, if you followed the dataset's `BUCKET_README.md`), so that the supplement folder is created next to it. If you have not fetched the dataset yet, any folder works for this step. On macOS, use `shasum -a 256` in place of `sha256sum`.

```sh
mkdir emg1-wd-fusion-v1 && cd emg1-wd-fusion-v1
curl -fsSL -o SHA256SUMS "<BASE_URL>/supplements/wd-fusion-predictions/v1/SHA256SUMS"
sha256sum SHA256SUMS      # must equal the supplement digest listed in the bucket-root README
while read -r h f; do curl -fsSL --create-dirs -o "$f" "<BASE_URL>/supplements/wd-fusion-predictions/v1/$f"; done < SHA256SUMS
sha256sum -c SHA256SUMS   # every line must end in OK
(cd fusion_delivery_v10 && sha256sum -c SHA256SUMS)
```

The take files come from the dataset itself. From inside your EMG-1 release folder (`emg1-8ch-v1.0.1`, created as its `BUCKET_README.md` describes), fetch the `take.h5` files of the predicted takes. With the supplement folder next to the release folder, as above, this fetches exactly the 391 predicted takes (10.8 GB), with one `--include` pattern per prediction file. If you put the supplement folder elsewhere, replace `../emg1-wd-fusion-v1` with its path:

```sh
python3 -B tools/download.py <BASE_URL> . --sums-sha256 <SHA256SUMS_DIGEST> --include $(ls ../emg1-wd-fusion-v1/fusion_delivery_v10/predictions | sed -E 's#^(OP-[0-9]{3})__(s[0-9]{3})__([0-9]{2})_fusion\.csv$#takes/\1/\2/\3/take.h5#')
```

To fetch whole people instead, use one pattern per person, for example `--include 'takes/OP-002/*/take.h5'`. All takes of the 8 people are 784 files (22.9 GB), about twice the predicted set.

`<BASE_URL>` and `<SHA256SUMS_DIGEST>` are the dataset's, from the bucket-root README. Open the CSVs read-only. Re-saving a CSV in a spreadsheet program breaks the check.

## Scoring against EMG-1 v1.0.1

1. Match each CSV to its take: `OP-002/s001/07` is `takes/OP-002/s001/07/take.h5`.
2. The rows are already on the take's clock. Join each row to the nearest `/video/t_ns`, and drop rows with no frame time within 8 ms. Encord measured this join on all 391 takes: 98.9% of the 1,173,702 rows lie within 1 ms of a frame time and 99.87% within 8 ms. The other 1,539 rows (0.13%) lie 8.0 to 17.2 ms from the nearest frame time, and 1,320 of them fall in a gap of more than 25 ms in the v1.0.1 frame log. Every take has at least 99.6% of its rows within 8 ms. Score at the row times as given. Wearable Devices has not stated yet whether a row describes the frame it coincides with or the one before; on the 365 predicted takes with scored rows, which Encord scored this way, moving every row one frame (16.7 ms) later or earlier changed a take's mean angle MAE by at most 0.44 deg (median 0.08 deg over takes).
3. Build the truth from `markers/canonical` (metres; frames x 23 x 3; T1 to P4, then WR, RAD, ULN), masked by `markers/canonical_valid`, at `markers/t_ns`.
4. Compute the 20 angles as GUIDE section 6 defines them, using the marker names below. Interpolate each angle linearly to the row times. An angle has no truth where one of its markers is invalid, or where its samples have a gap over 50 ms.
5. Score only rows whose `role` starts with `scored_`. Report the two scored roles separately. Average per person first, then over people with equal weight.

| Wearable Devices marker | EMG-1 canonical |
|---|---|
| `thumb_1` to `thumb_4` | `T1` to `T4` |
| `index_1` to `index_4` | `I1` to `I4` |
| `middle_1` to `middle_4` | `M1` to `M4` |
| `ring_1` to `ring_4` | `R1` to `R4` |
| `pinky_1` to `pinky_4` | `P1` to `P4` |
| `wrist`, `radial`, `ulnar` | `WR`, `RAD`, `ULN` |

The mapping is by number. Encord checked it against `hand_model.json`: segment lengths from `markers/canonical` on each person's predicted takes agree with the vendor's to within 1.8 mm for all 8 people, OP-003 on its 2 predicted takes (median difference per person at most 0.57 mm). With the numbering shifted by one marker (vendor `_1` to `_2` compared with canonical 2 to 3, and `_2` to `_3` with 3 to 4, so 10 segments per person), the largest difference per person is 17.9 mm or more, and the median difference per person is 5.8 to 11.6 mm. The two sets of documents name the markers differently: Wearable Devices calls `_1` the MCP knuckle, while v1.0.1 `MARKERS.md` calls I1 the index base and I2 the index knuckle. v1.0.1 lists the anatomical placement of every marker as unconfirmed (take.h5 `markers/anatomical_mapping_status`).

**Your numbers will not match the vendor's metric files exactly.** The vendor's truth came from its own processing of the marker data, not from `markers/canonical`, and GUIDE section 6 does not fix every detail of the palm-frame construction. `gain_deg` and `gain_pct` need each model's training-mean pose, and the mm metrics need the vendor's posing conventions; neither is shipped.

## Errata to `fusion_delivery_v10/README.md` and `GUIDE.md`

The two vendor files ship as delivered except line 3 of both and line 154 of `GUIDE.md`, and their corrections are listed here instead of being edited into their text. Wearable Devices approved this approach. Read them with these corrections. The numbers were measured by Encord on the files shipped here unless an item says otherwise.

1. **Time column (vendor README "Prediction columns"; GUIDE sections 1, 4.1, 5, 8.2 and 11).** Where these files name the time column `t_lsl_ns`, read `t_ns`: int64 nanoseconds on the take's EMG-1 clock, the same clock as take.h5 `/video/t_ns` and `/markers/t_ns`. Where they name the manifest fields `from_t_lsl_ns` and `to_t_lsl_ns`, read `from_t_ns` and `to_t_ns`. In the GUIDE section 8.2 code, join on `t_ns`, with your truth table on the take's clock.
2. **"About one frame (~16 ms) earlier" (GUIDE sections 4.2 and 8.2).** After conversion the rows coincide with the v1.0.1 frame times: rows sit a median 0.049 ms after their nearest `/video/t_ns` (median distance 0.205 ms), and per-take median offsets lie between 0.002 and 0.142 ms. Do not "shift ours by one frame first"; that would move every row about 16.7 ms off the frame times. Wearable Devices has not stated yet whether each row describes the frame it coincides with or the one before (see step 2 of "Scoring against EMG-1 v1.0.1").
3. **ZED frame log (GUIDE section 4.2).** The frame-log file that section names is from the raw recording layout. v1.0.1 keeps a copy of that frame log inside each take.h5, under `/source/take/video/`. Its times are already on the EMG-1 clock and equal `/video/t_ns` exactly (checked on all 391 predicted takes), so use `/video/t_ns`, and do not apply the section's one-frame offset to it.
4. **Counts (GUIDE sections 1, 2, 3.3 and 10).** "8 people, 455 takes" and "455 files" describe the delivery. This supplement has 391 prediction files; the GUIDE 3.3 table, including its row counts, also describes the 455-take delivery. Use the Coverage tables above. GUIDE section 10's "from 15 to 147 takes" becomes 2 to 120 takes per person here.
5. **"People with one session (OP-007, OP-008)" (GUIDE sections 3.2 and 10).** This holds for the data these models used. v1.0.1 has 3 sessions (45 takes) for OP-008, of which only s001 has predictions; OP-007 has 1 session in v1.0.1.
6. **Calibration rule (vendor README "How a prediction is made"; GUIDE sections 1 and 3.2; the manifest's `calibration.rule`).** The 120 s budget counts only 1 s windows that have a camera hand and a valid motion-capture label; the text names the camera condition only. OP-005's calibration covers 469.0 s over 9 takes, 6 of which (s001/01, s001/02, s001/04, s001/05, s001/06, s001/07) are in `takes_without_valid_window`. OP-008's covers 242.2 s over 5 takes, 2 of which (s001/02, s001/04) are in that list. OP-004's covers 236.7 s over 5 takes, none of them in that list, so its extra time lies inside its calibration takes, in windows that did not count towards the budget. GUIDE section 3.2's "a little longer than 120 s" understates the spans of OP-004 (236.7 s), OP-005 (469.0 s) and OP-008 (242.2 s).
7. **"Which camera frames did the calibration see?" (GUIDE section 5).** The `calibration` rows are an exclusion mask, not the list of samples the calibration used: they include the 1 s guard and, for OP-005 and OP-008, whole takes that gave no labelled window. Use them to exclude rows.
8. **`takes_without_valid_window` (GUIDE section 5).** It is not a subset of the training takes: it shares no take with `training.takes` in any of the 8 models. It holds 28 distinct take IDs, 26 of them in v1.0.1.
9. **Typical range table (GUIDE section 6.2).** Recomputed as the pooled 1st to 99th percentile of the 1,096,118 scored rows shipped here, 15 of the 20 angles differ from the table by more than 3 deg at one end or both (also 15 of 20 on the full delivery). Examples: `ring.mcp_flex_deg` is listed as -7 to 45 and measures -21.3 to 64.2; `pinky.pip_flex_deg` is listed as 15 to 75 and measures -0.6 to 84.8; `thumb.cmc_abd_deg` is listed as 9 to 48 and measures 0.3 to 61.0; `ring.dip_flex_deg` is listed as 2 to 37 and measures 0.8 to 53.5. Treat the table as illustrative only.
10. **The "4.5 mm median" FK floor (vendor README "Metrics"; GUIDE section 7.3).** 4.45 mm is the mean over the 8 people of each person's mean, over 15 joint positions, of the per-joint median floor (`fk_floor_mm.mean.median_mm` in `hand_model.json`); it is not a median. Per-joint median floors run from 0.75 mm (OP-007 thumb.mcp) to 14.47 mm (OP-004 thumb.tip); fingertip floors run from 3.38 mm (OP-008 ring.tip) to 14.47 mm. The floor is the hand model's own error against the measured markers. It is not a hard lower bound on the predicted-versus-true mm error, because both hands are posed with the same model, so identical angles give 0 mm. Read it as the scale below which an mm difference says little about accuracy in space.
11. **"Several takes of OP-005" (GUIDE sections 7.2 and 11).** In this supplement 18 scored takes have empty metrics: OP-002 7, OP-004 2, OP-005 5, OP-006 2, OP-008 2. All 18 are in `takes_without_valid_window`. In v1.0.1 their canonical markers have all 23 markers valid in 87.3 to 100% of motion-capture frames (14 of them at 100%).
12. **`per_joint_metrics.csv` (vendor README "Files"; GUIDE sections 2, 7.2 and 8.3).** It is not in this supplement (see "What Encord changed").
13. **Zip and unzipping (vendor README "Checking the files"; GUIDE sections 2 and 9).** There is no zip archive. `fusion_delivery_v10/SHA256SUMS` covers the files shipped here; run its check inside `fusion_delivery_v10/`.
14. **"Ask us" (GUIDE section 5).** Send requests to support@encord.com.
15. **Hand model takes (vendor README "Kinematic model"; GUIDE section 7.3).** "Every take of theirs with valid markers" includes takes outside v1.0.1 and the scored takes themselves (see "Other fields").
16. **`marker_layout.png`, pinky.** The labels read `pinky_1` to `pinky_4` as mcp, pip, dip and tip, the same order as the other fingers and as GUIDE section 6.0. Each label sits just below its own dot (the index, middle, ring and pinky tip labels sit above), but the `pinky_3` label sits almost midway between the `pinky_3` and `pinky_2` dots, so it is easy to read against the wrong dot, which shifts the pinky labels by one joint. The numbering defines the markers; use the mapping table above.
17. **"Later session = days after calibrating" (GUIDE section 10).** A later session is a band re-wear, not necessarily a later day. For the 7 people whose calibration session is in v1.0.1, 5 later sessions start 0.16 to 4.59 h after the calibration session ends: OP-006/s002 (0.16 h), OP-004/s003 (3.24 h), OP-004/s004 (3.37 h), OP-004/s005 (3.88 h), OP-002/s002 (4.59 h). They hold 54 of these people's 295 later-session takes and 20% of their later-session rows. Every other later session starts at least 26.4 h after. Consider reporting later-session results for these two groups separately. The times come from `take_start_subject_relative_s` and `duration_s` in `index/takes.csv`.

## Licence

The files in this supplement are licensed under the Creative Commons Attribution 4.0 International licence (CC BY 4.0, https://creativecommons.org/licenses/by/4.0/). Rights holders: Wearable Devices Ltd. for the files in `fusion_delivery_v10/` other than its `SHA256SUMS`; Encord for this README, the `LICENSE` header and the two `SHA256SUMS` files. Wearable Devices approved publishing every file it wrote, `marker_layout.png` included, under CC BY 4.0. The full text is in `LICENSE`. The supplement contains no code files; the commands and code snippets inside `README.md` and `GUIDE.md` are part of those documents and are licensed under CC BY 4.0. Any code file that Encord adds later is licensed under Apache-2.0, like the EMG-1 code. The licences of EMG-1 v1.0.1 are unchanged.

## Attribution

Credit these predictions as "EMG-1 fusion hand-pose predictions, Wearable Devices Ltd., 2026, CC BY 4.0", link the licence, and say whether you changed the files. Also credit the dataset as "EMG-1 8-channel dataset, Vineeth Velmurugan, Encord, 2026, CC BY 4.0", and cite it with the dataset's `CITATION.cff`.

## Contact and withdrawal

Send questions, errata, takedown and withdrawal requests to support@encord.com. Name this supplement and, where it applies, the take paths. Fixes ship as new supplement versions.

Each person's predictions come from a model trained on the other 7 people. If a person withdraws, their prediction files and metric rows are removed in the next supplement version. The models are not retrained. Copies already downloaded cannot be recalled.

## Caveats

- **Not comparable with T1, T2, T3 or the dataset splits.** The inputs differ (camera plus EMG), the test person gets a labelled 2-minute calibration, the windows are offline with 0.5 s of future EMG, and the outputs are joint angles, not fingertip proximity (T1), wrist-frame marker positions (T2) or fingertip positions (T3). Training is leave-one-of-8-out, not the dataset's 12-fold LOSO. The calibration rows lie inside LOSO test takes, so exclude them in any LOSO comparison. The default split's test people (OP-009 and OP-010) have no predictions. The dataset's `within_person_session` split holds out each person's last session, while `scored_new_session` here covers every later session, so those are not comparable either.
- **Several meanings of calibration.** "Calibration" here is the vendor's per-person 2-minute calibration. It is unrelated to the 10 s CAL window of T3, to the Motive files in the dataset's `calibration/` folder, and to the camera and motion-capture metadata in each take.h5 `calibration/` group.
- **The vendor's truth is not `markers/canonical`.** See Errata item 11 for the 18 scored takes that the vendor could not score but whose canonical markers are valid.
- **OP-003.** Its calibration session is not in v1.0.1, and only 2 of its predicted takes are (OP-003/s006/01 and 02, both later-session takes); its other 75 v1.0.1 takes have no predictions.
- **Session numbers.** Session numbers are those of v1.0.1, which keeps the numbering of the recordings, so some numbers have no take in v1.0.1 (for example OP-001 s001 and s002, and OP-004 s001). "First session" in the vendor files means the first session in the data that the models used (see "Calibration of a new person").
- **No confidence values.** The predictions carry no per-frame confidence, and frames predicted from EMG alone are not flagged.
- **Predictions are not clipped.** The 10 flexion columns that are magnitudes in the truth (GUIDE section 6.1) go below 0 in 0.15 to 1.22% of the scored rows shipped here, with a minimum of -57.72 deg (`index.pip_flex_deg`).
- **The mm errors exclude palm placement error.** The metric files pose the fingers on the frame's measured wrist and knuckle markers, using each person's own segment lengths. See Errata item 10 for the kinematic floor.
- **Marker-instrumented hands.** The camera saw hands wearing skin markers, so accuracy may not carry over to bare hands.
- **Anthropometrics.** `hand_model.json` holds per-person hand segment lengths, measured marker to marker and including skin offsets. They can be derived from the released markers, except for OP-003: its values pool 20 takes, 18 of them not in v1.0.1.
- **Training takes outside the release.** 62 of the 427 distinct training takes are not in v1.0.1.
