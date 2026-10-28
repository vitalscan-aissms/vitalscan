# M6 `signal_processing`

**Owner:** Sidd  
**Status:** filters done (`filters.py`); timestamp resampling, FFT, peaks and SNR not started

**Purpose:** Resampling, detrending, 0.7-4 Hz band-pass, FFT, peak detection, SNR.
`filters.py` is shared by the live pipeline and BP training (`ml_models.features.camera_match`),
so both clean their pulse with the same code.

**Inputs:** raw pulse + sampling rate (later: + real frame timestamps)

**Outputs:** clean pulse (later: peaks, spectrum, SNR)

| Function | Does |
| --- | --- |
| `resample_uniform(x, fs, target_fs=30)` | anti-aliased resampling of an evenly sampled signal (e.g. PulseDB 125 Hz → 30 Hz) |
| `detrend_signal(x)` | removes the straight-line drift |
| `bandpass(x, fs, band_hz=(0.7, 4.0), order=3)` | zero-phase Butterworth band-pass (`sosfiltfilt`), 42–240 bpm |

Defaults equal `configs/signal.yaml`; `test_defaults_match_signal_config` fails if they drift apart.
Bad input (not 1-D, NaN/inf, too short to filter) raises `SignalError` with a clear message.

**Dependencies:** NumPy, SciPy.

**Example usage:**

```python
from vitalscan.signal_processing.filters import bandpass, detrend_signal

clean = bandpass(detrend_signal(raw_pulse), fs=30)
```

**Tests:** `backend/tests/test_filters.py`.
