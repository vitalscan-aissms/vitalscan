"""Resampling, detrending and band-pass filtering shared by the live pipeline and training.

Purpose:
    One implementation of the M6 filter chain, so a pulse from the camera (live scans) and a
    finger PPG from PulseDB (training) are cleaned by exactly the same code.
Inputs:
    1-D pulse signals as NumPy arrays plus their sampling rate in Hz.
Outputs:
    Filtered 1-D signals as float64 NumPy arrays.
Example:
    >>> import numpy as np
    >>> fs = 125.0
    >>> t = np.arange(0, 10, 1 / fs)
    >>> raw = np.sin(2 * np.pi * 1.2 * t) + 0.5 * t          # 72 bpm pulse + slow drift
    >>> clean = bandpass(detrend_signal(raw), fs)
    >>> clean.shape
    (1250,)

Default values match configs/signal.yaml (a test checks this, so they cannot drift apart).
"""

from __future__ import annotations

import logging
from fractions import Fraction

import numpy as np
from scipy import signal as sps

logger = logging.getLogger(__name__)

DEFAULT_TARGET_FS = 30.0
DEFAULT_BAND_HZ = (0.7, 4.0)
DEFAULT_FILTER_ORDER = 3


class SignalError(ValueError):
    """Raised when a signal is too short, not 1-D, or contains NaN/inf values."""


def _check_signal(x: np.ndarray, fs: float, min_seconds: float = 0.0) -> np.ndarray:
    """Validate a 1-D finite signal and return it as float64."""
    arr = np.asarray(x, dtype=np.float64)
    if arr.ndim != 1:
        raise SignalError(f"Expected a 1-D signal, got shape {arr.shape}")
    if fs <= 0:
        raise SignalError(f"Sampling rate must be positive, got {fs}")
    if not np.all(np.isfinite(arr)):
        raise SignalError("Signal contains NaN or infinite values; clean or interpolate them first")
    if arr.size / fs < min_seconds:
        raise SignalError(f"Signal is {arr.size / fs:.2f} s long; need at least {min_seconds} s")
    return arr


def resample_uniform(x: np.ndarray, fs: float, target_fs: float = DEFAULT_TARGET_FS) -> np.ndarray:
    """Resample an evenly sampled signal to ``target_fs`` with an anti-aliasing filter.

    Inputs: ``x`` (N,) signal sampled at ``fs`` Hz; ``target_fs`` the wanted rate in Hz.
    Outputs: signal of length about ``N * target_fs / fs``.
    Example: a 10 s PulseDB PPG at 125 Hz (1250 samples) becomes 300 samples at 30 Hz.

    Use this for signals that are already evenly spaced (PulseDB). Browser video has uneven
    frame times and must be interpolated from its real timestamps instead.
    """
    arr = _check_signal(x, fs)
    if np.isclose(fs, target_fs):
        return arr.copy()
    ratio = Fraction(target_fs / fs).limit_denominator(1000)
    out = sps.resample_poly(arr, ratio.numerator, ratio.denominator)
    logger.debug(
        "Resampled %d samples at %.1f Hz to %d at %.1f Hz", arr.size, fs, out.size, target_fs
    )
    return np.asarray(out, dtype=np.float64)


def detrend_signal(x: np.ndarray) -> np.ndarray:
    """Remove the straight-line trend (slow lighting or sensor drift) from a signal.

    Inputs: ``x`` (N,) signal. Outputs: (N,) signal with its best-fit line subtracted.
    """
    arr = _check_signal(x, fs=1.0)
    return np.asarray(sps.detrend(arr, type="linear"), dtype=np.float64)


def bandpass(
    x: np.ndarray,
    fs: float,
    band_hz: tuple[float, float] = DEFAULT_BAND_HZ,
    order: int = DEFAULT_FILTER_ORDER,
) -> np.ndarray:
    """Zero-phase Butterworth band-pass filter (keeps 42-240 bpm by default).

    Inputs: ``x`` (N,) signal at ``fs`` Hz; ``band_hz`` (low, high) cut-offs; filter ``order``.
    Outputs: (N,) filtered signal. ``sosfiltfilt`` runs the filter forwards and backwards,
    so peaks are not shifted in time (important for pulse-timing features).
    """
    low, high = band_hz
    if not 0 < low < high < fs / 2:
        raise SignalError(f"Band {band_hz} Hz must satisfy 0 < low < high < fs/2 = {fs / 2} Hz")
    # sosfiltfilt needs a few cycles of the lowest frequency to settle at the edges.
    arr = _check_signal(x, fs, min_seconds=3.0 / low)
    sos = sps.butter(order, [low, high], btype="bandpass", fs=fs, output="sos")
    return np.asarray(sps.sosfiltfilt(sos, arr), dtype=np.float64)
