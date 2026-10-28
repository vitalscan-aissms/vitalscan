# M8 `ml_models`

**Owner:** Member 2  
**Status:** pulse-shape features done (`features.py`); ONNX inference not started

**Purpose:** Everything the server needs for the experimental BP estimate:
1. `features.py` — turns a clean pulse into one row of pulse-shape features. **Training on Colab/Kaggle imports this same file**, so the model sees identical features in training and in production.
2. *(later)* load the BP ONNX model and predict SBP/DBP with an error band. Training scripts live in `training/`.

**Inputs:** a clean 1-D pulse (systolic peaks pointing up) and its sampling rate.
For PulseDB finger PPG, call `camera_match(ppg, fs=125)` first.

**Outputs:** `dict[str, float]` with every name in `FEATURE_NAMES`:

| Feature | Meaning |
| --- | --- |
| `duration_s` | beat length, foot to next foot |
| `rise_time_s`, `fall_time_s`, `rise_ratio` | foot → peak, peak → next foot, rise ÷ duration |
| `width_25_s`, `width_50_s`, `width_75_s` | how long the beat stays above 25/50/75 % of its height |
| `area_ratio_dia_sys` | area after the peak ÷ area before it |
| `max_upslope_per_s`, `vpg_peak_time_s` | steepest rise (first derivative, VPG) and when it happens |
| `apg_b_a` | b/a ratio of the second derivative (APG), linked to arterial stiffness |
| `hr_bpm`, `ibi_sdnn_ms`, `ibi_rmssd_ms` | heart rate and beat-interval variability (short windows: experimental) |
| `n_beats`, `beat_quality` | clean beats used, and the share of beats that passed the checks |

Beat features are the **median** over all clean beats. Age, sex and BMI are added by the training script, not here.

**Design choices (defend these in the viva):**
- **Camera matching (RQ3).** PulseDB is a clean 125 Hz finger signal; ours is a 30 Hz band-passed face signal. `camera_match` resamples to 30 Hz and applies the same detrend + 0.7–4 Hz band-pass as M6, so the model never learns details (like the dicrotic notch) that a webcam cannot see.
- **Upsampling to 120 Hz before measuring.** The pulse has no content above 4 Hz, so resampling 30 → 120 Hz loses nothing and gives 8 ms timing resolution instead of 33 ms.
- **Spectral beat spacing.** Peaks must be ≥ 60 % of the FFT beat period apart; otherwise the diastolic wave is counted as an extra heartbeat (a test covers this).
- **Edge trimming.** Beats in the first/last second are skipped because the band-pass filter distorts the edges.
- **Beat checks.** Beats must be 0.25–1.5 s (40–240 bpm) and within 30 % of the median length.

**Dependencies:** NumPy, SciPy, `vitalscan.signal_processing.filters`.

**Example usage:**

```python
from vitalscan.ml_models.features import camera_match, extract_features

pulse = camera_match(ppg_125hz, fs=125)          # PulseDB segment -> camera-like 30 Hz pulse
row = extract_features(pulse, fs=30)             # {"hr_bpm": 72.0, "rise_time_s": 0.26, ...}
```

`extract_features` raises `FeatureExtractionError` if fewer than 3 clean beats are found; training scripts should catch it, count it, and skip that segment.

**Tests:** `backend/tests/test_bp_features.py` (synthetic pulses with known heart rate and shape).
