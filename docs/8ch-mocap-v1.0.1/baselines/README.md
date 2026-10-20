# Shipped baselines

Run `python -B baselines/reproduce.py .` from the release root. It writes predictions and metrics to a temporary directory outside the release tree and checks the resulting JSON against shipped metrics. The headline T1 recipe was fixed on the 430 non-SCORE takes before any SCORE take was read. The selection rule used performance on those non-SCORE takes only: macro AUROC 0.738 versus 0.640 for the earlier a priori configuration. Probe logs are retained in the `reference/t1_probe/`. The earlier configuration was fixed a priori before any SCORE read; no data-driven selection was performed for it. Its freeze was 2026-10-15T04:50:16Z, SHA-256 `22b5a0598d6bbb90e4d52d143798354f989c3676926d0a7ff56e2ec9c48900d4`.

The T1 model uses log RMS, log MAV and log waveform length, zero-crossing and slope-sign-change rates over 400 samples on the official 200-sample-start grid, 100 and 200 ms context formed before filtering, and balanced L-BFGS logistic regression with C=0.1, tolerance 1e-4 and at most 500 iterations. It follows the glitch filter and label rule in `eval/probe_targets.py`. Model settings are in `frozen_config.json` and the generating code is shipped. The earlier configuration used log1p RMS, nearly linear at this amplitude scale, and is superseded. The vendor did not provide physical EMG amplitude units (volts); the features use the shipped normalized ADC counts.

| T1 model | AUROC (95% CI) | AP (95% CI) | Prevalence |
|---|---:|---:|---:|
| Train prevalence | 0.5000 [0.500, 0.500] | 0.0990 [0.070, 0.129] | 0.099 |
| Probe logistic regression | 0.7654 [0.717, 0.816] | 0.2649 [0.191, 0.345] | 0.099 |

| T2 model | Mean marker error, mm | Fingertip error, mm |
|---|---:|---:|
| Mean pose | 27.685 | 43.267 |
| Ridge | 27.737 | 43.268 |
| Small MLP | 28.966 | 44.149 |

T2 is a reference result; compare the regenerated model rows above. Full precision, fold metrics and bootstrap intervals are in the metric JSON files. Exact T1 reproduction uses the pinned scikit-learn and SciPy versions in `requirements.txt`. The old MLP used Adam learning rate 0.001. `eval/TASKS.md` defines the submission contract.
