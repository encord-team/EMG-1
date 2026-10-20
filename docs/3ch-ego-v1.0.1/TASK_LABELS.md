# Vendor task labels

`vendor/titles.csv` lists the distinct preserved titles and their occurrence counts. The title and description in each `vendor/<clip_id>.json` sidecar are vendor free text. How the vendor produced them was not provided by the vendor; task categories come from these titles, mapped by the frozen keyword taxonomy. They have not been independently reviewed as human ground truth. `vendor/segments.parquet` preserves titles, session-relative millisecond bounds and eight keyword-derived categories, but the per-segment descriptions remain in the sidecars. `vendor_segments(clip_id, clock='clip')` returns both title and description after subtracting the clip's `data.start_ts`. `tools/task_stats.py` recomputes the following table from shipped segment rows.

| Category | Occurrences | Vendor hours | Example title |
| --- | ---: | ---: | --- |
| sewing | 2642 | 147.420 | Sewing white fabric piece |
| overlock | 71 | 3.937 | Sewing fabric on overlock machine |
| aligning/handling fabric | 1809 | 89.153 | Aligning fabric for sewing |
| folding | 392 | 19.700 | Folding red hoodie |
| inspecting | 874 | 44.729 | Inspecting white fabric piece |
| machine adjustment | 153 | 6.089 | Threading the sewing machine |
| idle | 3237 | 28.196 | idle |
| other | 1223 | 56.071 | Threading drawstring through hoodie |

`other` includes cutting or trimming, phone or break, and band or sensor adjustment. Such activities may have EMG artifacts or different task meaning. The mapping is taxonomy version 2, applying the same frozen keyword rule to all titles. It is not a human audit. Use a reduced class set or a minimum per-class test support for headline metrics. A small automated check can compare every segment title's mapped category against `taxonomy/title_to_category_v1.json`; it validates consistency, not correctness. A clip's `task_category` in the index is its dominant vendor category, not a time-aligned window label.

Clips with no vendor segment (27) are assigned `other`.
