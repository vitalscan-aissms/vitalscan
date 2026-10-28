# `utils`

**Owner:** Sidd  
**Status:** synthetic signals done (`synthetic.py`); logging and config loading not started

**Purpose:** Shared helpers: synthetic test signals, and later logging setup, config loading and common errors.

**Inputs / Outputs:** see each function.

| Function | Does |
| --- | --- |
| `synthetic.synthetic_ppg(hr_bpm, seconds, fs, ...)` | fake finger PPG with a known heart rate and pulse shape (two Gaussian waves per beat), optional beat jitter, drift and noise |

**Dependencies:** NumPy.

**Example usage:**

```python
from vitalscan.utils.synthetic import synthetic_ppg

ppg = synthetic_ppg(hr_bpm=72, seconds=10, fs=125, noise=0.05)   # (1250,) array
```

Use it in tests: because the true heart rate and shape are known, a test can check the exact answer.
