# Datasheet: EMG-1 3-channel dataset v1.0.1

## Motivation

The dataset supports research on surface-EMG decoding of hand activity, egocentric activity recognition with wrist EMG, multimodal sensor fusion and human-computer interaction, using recordings of textile work in a factory. Author and maintainer: Vineeth Velmurugan (Encord). Funding: Encord. Physiological signals and images do not provide validated worker-performance scores or clinical evidence.

## Composition

There are 4,916 clips, 397.428 clip-hours with EMG and 271.779 hours of both-wrist GOLD or STANDARD quality segments. The raw layer contains original MCAP video, neural stereo depth and sensors; the extracted layer contains sensor HDF5 files; derived layers contain time estimates, quality tiers and automatic wrist-cap poses. Index rows and vendor sidecars are preserved for all clips, including 2 with PPG-only files and no loadable EMG sensor inputs. The `tools/release_stats.py` script recomputes the counts. The dataset spans 136 sessions over 68 station-days at 7 recording stations, with recording dates from 2026-09-29 to 2026-10-13 (UTC), and 637.0 per-wrist GOLD or STANDARD hours. No worker identifiers or per-person rows are supplied. Number of distinct workers: not reported. No per-person demographic data were collected or published.

| Primary partition | Clips | Clip-hours with EMG | Both-wrist quality hours | Station-days |
| --- | ---: | ---: | ---: | ---: |
| train | 3,488 | 281.695 | 191.070 | 49 |
| val | 734 | 59.860 | 40.347 | 9 |
| test | 694 | 55.872 | 40.362 | 10 |

The table is computed by `tools/release_stats.py` from the shipped clip index. Quality hours count segment-rule GOLD or STANDARD time, not independent task ground truth.

## Collection process

The recordings were collected for Encord by a commercial data-collection vendor. Encord holds the rights to release these recordings publicly, including the video. Recruitment, consent procedures, compensation and ethics review: not reported.

Recordings used Mudra Pro wrist bands, a ZED X Mini head stereo camera and two ZED X One GS wrist cameras during textile work in a factory. Amplitude scaling of the band EMG to physical units: not provided by the vendor. Electrode type and placement: not provided by the vendor. Vendor task titles and descriptions are free text; how the vendor produced them was not provided by the vendor. Task categories come from the vendor titles, mapped by the frozen keyword taxonomy in `taxonomy/KEYWORD_RULES.md`. The eight-category taxonomy is an unaudited keyword map; `other` includes multiple activities. Raw MCAP recorder metadata retains station hostnames and account-like recording strings, some in email format; these are stand-in values, not personal contact details. Extracted L1 files have account fields removed. Video is not visually anonymised.

## Preprocessing and cleaning

The extracted layer preserves band observations and separates estimated timestamps into `derived/sensors_est/`. The frozen quality rule grades each wrist and emits quality segments; all clips remain in the roster. Vendor session timestamps convert to clip time by subtracting `data.start_ts`. The host mapping is an estimate. Wrist poses are automatic optical cap estimates, not anatomical targets. See `provenance/METHODS.md` and `QUALITY_TIERS.md`.

## Uses

Primary research tasks are weakly labeled task recognition and multimodal timing analysis with explicit quality masks. The primary split is station-day grouped and is not person-disjoint. Station-held-out evaluation is confounded by a failing left band at its test station and head stamp slips at its validation station; the flag also occurs on all 752 egox-005 clips. Cross-task evaluation is experimental. Per-wrist results use the same canonical both-wrist windows, with only that wrist's features. Report metrics by wrist and use station-day bootstrap intervals.

Intended uses: research on surface-EMG decoding of hand activity, egocentric activity recognition with wrist EMG, multimodal sensor fusion and human-computer interaction.

Not intended for (guidance, not a licence restriction): biometric identification or re-identification, monitoring or evaluating workers or individuals, and clinical diagnosis or medical decisions.

## Distribution

The release is free and open, with no account, access key or agreement. Release date: 2026-10-20. Files are served over public HTTPS and downloaded with `tools/download.py`; the public base URL is given in the bucket-root `README.md`, outside the `v1.0.1/` prefix, and `BUCKET_README.md` lists the download commands. Licences: data under Creative Commons Attribution 4.0 International (CC BY 4.0) and source code (every `.py` file and `requirements*.txt`) under Apache License 2.0; see `LICENSE`, `LICENSE-CODE` and `TERMS.md`. Attribution: "EMG-1 3-channel dataset, Vineeth Velmurugan, Encord, 2026, CC BY 4.0". Cite with `CITATION.cff`; no DOI has been assigned yet. The raw destination object listing reconciles count, sizes and ETags; raw content verification is separate.

## Maintenance

Maintainer: Vineeth Velmurugan (Encord). Questions, errata, takedown and withdrawal requests: support@encord.com (see `CONTACT.md`). Errata: fixes ship as new versions with a `CHANGELOG.md` entry. Withdrawal: requests go to support@encord.com, and affected recordings are removed from later versions. Retention: released versions stay available unless a withdrawal or legal request requires removal. Known limitations and version changes are in `KNOWN_ISSUES.md` and `CHANGELOG.md`. The release label is v1.0.1.

Of the 271.779 both-wrist quality-segment hours, 0.084 h belong to the 2 PPG-only clips and cannot be loaded as EMG windows; 271.695 h are loadable.
