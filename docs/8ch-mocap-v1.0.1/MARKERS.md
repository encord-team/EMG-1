# Hand and marker set

Every take records the left wrist and hand. Dominance is not published per person. Markers are on skin, not joint centres.

The first 20 labels are finger markers. Indices are zero based. Vendor spelling and order vary by person and take. The canonical labels are in `markers/canonical_labels`; use each take’s `markers/labels` and `markers/canonical_aliases` for the observed spelling.

| Index | Canonical | Anatomical landmark |
|---:|---|---|
| 0 | T1 | thumb base |
| 1 | T2 | thumb knuckle |
| 2 | T3 | thumb mid |
| 3 | T4 | thumb tip |
| 4 | I1 | index base |
| 5 | I2 | index knuckle |
| 6 | I3 | index mid |
| 7 | I4 | index tip |
| 8 | M1 | middle base |
| 9 | M2 | middle knuckle |
| 10 | M3 | middle mid |
| 11 | M4 | middle tip |
| 12 | R1 | ring base |
| 13 | R2 | ring knuckle |
| 14 | R3 | ring mid |
| 15 | R4 | ring tip |
| 16 | P1 | pinky base |
| 17 | P2 | pinky knuckle |
| 18 | P3 | pinky mid |
| 19 | P4 | pinky tip |
| 20 | WR | wrist centre |
| 21 | RAD | radial wrist |
| 22 | ULN | ulnar wrist |

`canonical_aliases` follows vendor order, while `canonical_labels` follows the order above. Do not zip these arrays. The arrays will be renamed in a future release.

## MediaPipe 21 keypoints to markers

The scorer uses palm points for alignment and scores only the five T4, I4, M4, R4 and P4 fingertip proxies. The fixed correspondence below explains the intermediate keypoint representation. Keypoint 0 is approximated by the midpoint of RAD and ULN. These are proxy correspondences because camera keypoints and skin markers differ anatomically.

| MediaPipe index | Marker proxy |
|---:|---|
| 0 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 1 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 2 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 3 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 4 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 5 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 6 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 7 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 8 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 9 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 10 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 11 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 12 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 13 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 14 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 15 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 16 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 17 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 18 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 19 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |
| 20 | Varies by take; read `markers/labels` and `markers/canonical_aliases` |

The camera is an external ZED 2i stereo camera, 1280 x 720 pixels per eye. The comparison uses a rigid palm-to-palm alignment fit on each take’s calibration frames; it does not use a camera extrinsic. No depth stream was recorded.
