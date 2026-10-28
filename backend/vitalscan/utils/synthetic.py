"""Synthetic pulse waves with a known heart rate and shape, for testing signal code.

Purpose:
    Real recordings never tell you the exact true answer. A synthetic pulse does, so every
    feature or vital-sign function can be tested against a known value before real data exists.
Inputs:
    Heart rate, duration, sampling rate, and shape parameters of the pulse.
Outputs:
    A 1-D NumPy array: the pulse wave sampled at ``fs`` Hz.
Example:
    >>> ppg = synthetic_ppg(hr_bpm=72, seconds=10, fs=125)
    >>> ppg.shape
    (1250,)

Each beat is the sum of two Gaussian bumps: the systolic wave (blood pushed out by the heart)
and a smaller, later diastolic wave (the pressure wave reflected back from the lower body).
This two-Gaussian model is a common simple stand-in for a finger PPG beat.
"""

from __future__ import annotations

import numpy as np


def synthetic_ppg(
    hr_bpm: float = 72.0,
    seconds: float = 10.0,
    fs: float = 125.0,
    systolic_width_s: float = 0.08,
    diastolic_delay_s: float = 0.25,
    diastolic_ratio: float = 0.45,
    hrv_jitter_s: float = 0.0,
    drift: float = 0.0,
    noise: float = 0.0,
    seed: int = 0,
) -> np.ndarray:
    """Make a fake PPG with a known heart rate and pulse shape.

    Inputs:
        hr_bpm: heart rate in beats per minute.
        seconds, fs: length in seconds and sampling rate in Hz.
        systolic_width_s: standard deviation of the systolic bump; wider = slower rise.
        diastolic_delay_s: time from the systolic to the diastolic bump.
        diastolic_ratio: diastolic height / systolic height.
        hrv_jitter_s: random change of each beat interval (standard deviation, seconds).
        drift: amplitude of a slow 0.05 Hz baseline wander.
        noise: standard deviation of added white noise.
        seed: random seed, so results are reproducible.
    Outputs:
        (round(seconds * fs),) float64 array.
    """
    rng = np.random.default_rng(seed)
    n = int(round(seconds * fs))
    t = np.arange(n) / fs
    period = 60.0 / hr_bpm

    # Beat onsets, starting before t=0 so the first beat in the window is complete.
    onsets = [-period]
    while onsets[-1] < seconds + period:
        onsets.append(onsets[-1] + period + rng.normal(0.0, hrv_jitter_s))

    systolic_centre = 3.0 * systolic_width_s     # bump starts near zero at the beat onset
    ppg = np.zeros(n)
    for onset in onsets:
        ppg += np.exp(-0.5 * ((t - onset - systolic_centre) / systolic_width_s) ** 2)
        diastolic_centre = systolic_centre + diastolic_delay_s
        diastolic_width = 1.5 * systolic_width_s
        diastolic = np.exp(-0.5 * ((t - onset - diastolic_centre) / diastolic_width) ** 2)
        ppg += diastolic_ratio * diastolic

    ppg += drift * np.sin(2 * np.pi * 0.05 * t)
    ppg += rng.normal(0.0, noise, n) if noise > 0 else 0.0
    return ppg
