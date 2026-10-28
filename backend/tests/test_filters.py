"""Tests for M6 filters: resampling, detrending, band-pass, and agreement with the config file."""

from pathlib import Path

import numpy as np
import pytest
import yaml

from vitalscan.signal_processing import filters
from vitalscan.signal_processing.filters import (
    SignalError,
    bandpass,
    detrend_signal,
    resample_uniform,
)

CONFIG = Path(__file__).resolve().parents[2] / "configs" / "signal.yaml"


def _dominant_hz(x: np.ndarray, fs: float) -> float:
    freqs = np.fft.rfftfreq(x.size, d=1 / fs)
    return float(freqs[np.argmax(np.abs(np.fft.rfft(x)))])


def test_defaults_match_signal_config() -> None:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert filters.DEFAULT_TARGET_FS == config["target_fps"]
    assert list(filters.DEFAULT_BAND_HZ) == config["bandpass_hz"]
    assert filters.DEFAULT_FILTER_ORDER == config["filter_order"]


def test_resample_125_to_30_hz_keeps_length_and_frequency() -> None:
    fs = 125.0
    t = np.arange(0, 10, 1 / fs)
    x = np.sin(2 * np.pi * 1.2 * t)
    y = resample_uniform(x, fs, 30.0)
    assert y.size == 300
    assert _dominant_hz(y, 30.0) == pytest.approx(1.2, abs=0.1)


def test_detrend_removes_linear_drift() -> None:
    x = 5.0 + 2.0 * np.arange(100)
    assert np.allclose(detrend_signal(x), 0.0, atol=1e-9)


def test_bandpass_keeps_pulse_and_removes_drift_and_noise() -> None:
    fs = 30.0
    t = np.arange(0, 30, 1 / fs)
    pulse = np.sin(2 * np.pi * 1.2 * t)
    drift = 3.0 * np.sin(2 * np.pi * 0.05 * t)   # slow lighting change, below the band
    buzz = 0.8 * np.sin(2 * np.pi * 9.0 * t)     # fast noise, above the band
    out = bandpass(pulse + drift + buzz, fs)
    inner = slice(60, -60)                       # ignore filter edge effects
    assert np.corrcoef(out[inner], pulse[inner])[0, 1] > 0.98


@pytest.mark.parametrize(
    "bad",
    [np.ones((10, 2)), np.array([1.0, np.nan] * 200)],
    ids=["two-dimensional", "contains-nan"],
)
def test_bad_signals_raise_clear_error(bad: np.ndarray) -> None:
    with pytest.raises(SignalError):
        bandpass(bad, 30.0)


def test_too_short_signal_raises() -> None:
    with pytest.raises(SignalError, match="at least"):
        bandpass(np.zeros(30), 30.0)   # 1 s is too short to filter at 0.7 Hz
