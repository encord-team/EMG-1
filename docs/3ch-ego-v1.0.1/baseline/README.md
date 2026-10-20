# Historical clip-level probe

This folder contains a weak clip-dominant ridge probe refit on the v1.0.1 primary train partition (3,488 clips; the 2,689 train clips with historical probe features enter the fit). Its target is one dominant vendor category per clip, not a time-aligned window label. It is not the reference benchmark for v1.0.1. Use `baselines/` and `EVALUATION.md` for the window-level protocol, primary and station-held-out results, per-class support and station-day intervals. `python -B baseline/reproduce.py .` re-fits this historical model from the shipped feature JSON.
