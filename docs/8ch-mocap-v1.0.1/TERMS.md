# Terms of use, v1.0.1

EMG-1 8-channel v1.0.1 is free and open. Anyone may download, use, share and adapt it, including for commercial work, under the two licences below. Downloads need no account or credentials. This page summarises the licences; the texts in `LICENSE` and `LICENSE-CODE` are the terms that apply.

## Licences

The two licences are assigned by file type, and `LICENSE` states the same rule:

All source code files, that is every `*.py` file and every requirements file such as `requirements.txt`, are licensed under the Apache License 2.0 (SPDX `Apache-2.0`); the full text is in `LICENSE-CODE`. Every other file in this release, including the recordings, derived estimates, index, splits, calibration files, metadata and documentation, is licensed under the Creative Commons Attribution 4.0 International licence (SPDX `CC-BY-4.0`); the full text is in `LICENSE`.

Files that sit next to the code but are not source code, such as READMEs, JSON configuration and metric files, logs and saved predictions, are therefore CC BY 4.0.

Every `take.h5` and `take.mcap` file still carries an `access` value written during original packaging. That value predates the open release and does not apply; `LICENSE` and `LICENSE-CODE` supersede it (see `KNOWN_ISSUES.md`).

Encord holds the rights to release these recordings publicly, including the video.

## Attribution

When you share the data or publish work that uses it, credit it as:

> EMG-1 8-channel dataset, Vineeth Velmurugan, Encord, 2026, CC BY 4.0

Also link to the licence (https://creativecommons.org/licenses/by/4.0/) and say whether you changed the data. For papers, cite the dataset with `CITATION.cff`. When you redistribute the code, include `LICENSE-CODE`, keep its notices and mark the files you changed.

## Responsible use

This section is guidance. It is not a licence restriction.

- The video is not visually anonymised and faces were not blurred. Do not try to identify or re-identify the people in the recordings, and do not link the data with other sources for that purpose.
- The dataset is not intended for biometric identification or re-identification of people, for monitoring workers or other individuals, or for clinical diagnosis or medical decisions.
- Contact labels, marker identity repairs, quality tiers, lag and camera keypoints are automatic estimates, not human annotations. `KNOWN_ISSUES.md` lists their limits.
- After a withdrawal request, the affected recordings are removed from later versions. Use the latest version when you can.

## Questions and requests

Send questions, errata, takedown and withdrawal requests to support@encord.com (see `CONTACT.md`).
