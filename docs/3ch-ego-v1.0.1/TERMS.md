# Terms of use

## Licences

This release is free and open. No account, access key, registration or agreement is needed to download or use it.

Source code is every file whose name ends in .py and every requirements*.txt file, wherever it is in the release. Source code is licensed under the Apache License, Version 2.0 (SPDX identifier Apache-2.0). Every other file is data and is licensed under the Creative Commons Attribution 4.0 International licence (SPDX identifier CC-BY-4.0). Data includes the sensor, derived and raw MCAP files with their ego video, the index tables, splits, vendor sidecars, feature tables, metrics, metadata and documentation, and also the README and other non-code files inside code folders such as tools/, loader/, baselines/, baseline/, eval/ and tests/.

`LICENSE` states the same split and holds the full CC BY 4.0 text. `LICENSE-CODE` holds the full Apache-2.0 text. The licence texts are the legal terms; this file summarises them.

## Attribution

CC BY 4.0 lets you copy, redistribute and adapt the data, including for commercial purposes, provided you give attribution. When you share the data or material adapted from it, use this credit line:

    EMG-1 3-channel dataset, Vineeth Velmurugan, Encord, 2026, CC BY 4.0

Link to the licence (https://creativecommons.org/licenses/by/4.0/) and say whether you changed the material. In papers, cite the dataset with `CITATION.cff`. Redistributed code keeps the Apache-2.0 notice requirements described in `LICENSE-CODE`.

## Responsible use (guidance)

This section is guidance. It does not add restrictions to either licence.

The dataset is intended for research on surface-EMG decoding of hand activity, egocentric activity recognition with wrist EMG, multimodal sensor fusion and human-computer interaction.

It is not intended for:

- biometric identification or re-identification of people;
- monitoring or evaluating workers or other individuals;
- clinical diagnosis or medical decisions.

Please keep these limits in mind:

- Vendor task labels and automatic wrist poses are not human ground truth. See `KNOWN_ISSUES.md` and `TASK_LABELS.md`.
- The ego video is not visually anonymised and may show people in the workplace. Please do not try to identify anyone in the recordings.
- Raw MCAP recorder metadata keeps station hostnames and account-like strings, some in email format. These are stand-in values, not personal contact details. Extracted L1 files have the account fields removed.

## Contact

Send questions, errata, takedown requests and withdrawal requests to support@encord.com. See `CONTACT.md`.
