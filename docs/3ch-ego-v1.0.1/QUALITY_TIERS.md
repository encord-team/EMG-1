# Frozen EMG quality tiers

A quality tier describes signal usability, not task or worker identity. The whole-clip grades in `index/clips` come from `derived/quality/tier_rule.py`; `index/segments` and the both-wrist quality-hour headline come from `derived/quality/segment_rule.py` and its frozen specification `SEGMENT_RULE.txt`.

| Tier | Meaning |
| --- | --- |
| GOLD | All three channels meet grade A; ordinary 20-450 Hz bandpass and 50 Hz comb filtering suffice. |
| STANDARD | All channels meet grade A or B; mask saturation `|v|>=0.99` with 250 ms on both sides, and use a 50 Hz comb plus 45-55 Hz band-stop when mains is elevated. |
| EXTENDED | Expert handling for a weak electrode, contact loss, lower coverage, reset clock or unverified wear. |
| NONE | Ordinary EMG analysis is unsuitable, including low-rate/low-resolution configuration, incorrect wrist association or multiple failed electrodes. |

Channel grade A requires rail fraction at most 0.0005 and 49-51 Hz power fraction at most 0.30. Grade B allows rail fraction at most 0.005 and mains fraction at most 0.85. Grade C permits rail fraction at most 0.05; a dead or flatter channel fails. Rate/configuration checks precede spectral checks. A band can be capped lower for gaps, clock irregularity, static wear or wrist-camera IMU disagreement. The clip tier is the worse wrist tier. Quality segments split a clip by usable intervals, so their hours can exceed hours selected by clip tier alone. `index/segments.csv` is the released segment authority. The script `tools/release_stats.py` recomputes document counts.

## Segment rule

The segment rule uses one-second windows on the frozen quality clock. It excludes a band for missing or invalid EMG, unsuitable recorder configuration, a reset device clock, p99 host jitter above 1000 ms, contradicted wrist association or missing band IMU. Within an eligible band it excludes windows with more than a 0.70 ms inter-sample step, hard saturation, and one-second neighbours of saturated windows. It drops usable runs shorter than 10 s. Both-wrist segments intersect the left and right runs and take the worse tier. These gates are stricter than the whole-clip grade, which masks saturation by 250 ms on each side and uses different gap limits. The released segment intervals and their hours are therefore not implied by `clip_tier`.

The source-rule comments mention `../tiers/tier_rule.py` and `qc3_final.json`; those are stale build-relative paths. Use the files under `derived/quality/` and the released indexes as the reproducible release sources.

The whole-clip GOLD or STANDARD selection totals 288.177 clip-hours; the released both-wrist GOLD or STANDARD segment intervals total 271.779 hours.

An unresolved wrist association caps a band at STANDARD; a contradicted association excludes it.
