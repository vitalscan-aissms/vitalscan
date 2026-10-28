"""Tests for M8 pulse-shape features, using synthetic pulses whose true values are known."""

import math

import numpy as np
import pytest

from vitalscan.ml_models.features import (
    FEATURE_NAMES,
    FeatureExtractionError,
    camera_match,
    extract_features,
)
from vitalscan.utils.synthetic import synthetic_ppg

PULSEDB_FS = 125.0


def _features(**kwargs: float) -> dict[str, float]:
    """Features of a 10 s synthetic finger PPG after camera matching, like PulseDB training data."""
    ppg = synthetic_ppg(seconds=10, fs=PULSEDB_FS, **kwargs)
    return extract_features(camera_match(ppg, PULSEDB_FS), fs=30.0)


def test_camera_match_gives_30_hz_signal() -> None:
    ppg = synthetic_ppg(seconds=10, fs=PULSEDB_FS)
    assert camera_match(ppg, PULSEDB_FS).size == 300


@pytest.mark.parametrize("hr", [45, 60, 72, 100, 150])
def test_heart_rate_is_recovered(hr: float) -> None:
    assert _features(hr_bpm=hr)["hr_bpm"] == pytest.approx(hr, abs=1.0)


def test_diastolic_wave_is_not_counted_as_extra_beat() -> None:
    # A narrow systolic wave leaves a separate diastolic peak after filtering.
    assert _features(hr_bpm=72, systolic_width_s=0.05)["hr_bpm"] == pytest.approx(72, abs=1.0)


def test_slower_upstroke_gives_longer_rise_time() -> None:
    rise = [_features(systolic_width_s=w)["rise_time_s"] for w in (0.05, 0.08, 0.12)]
    assert rise[0] < rise[1] < rise[2]


def test_beat_interval_variability_is_measured() -> None:
    steady = _features(hr_bpm=72)["ibi_sdnn_ms"]
    varying = _features(hr_bpm=72, hrv_jitter_s=0.05)["ibi_sdnn_ms"]
    assert steady < 10.0
    assert varying > 25.0


def test_noise_and_drift_do_not_change_heart_rate() -> None:
    noisy = _features(hr_bpm=72, noise=0.05, drift=0.5)
    assert noisy["hr_bpm"] == pytest.approx(72, abs=1.0)
    assert noisy["beat_quality"] > 0.8


def test_every_feature_is_present_and_finite() -> None:
    features = _features(hr_bpm=72)
    assert set(features) == set(FEATURE_NAMES)
    assert all(math.isfinite(v) for v in features.values())


def test_short_camera_segment_still_works() -> None:
    # The Mendeley iPPG + BP dataset stores 250-sample segments (about 8.3 s at 30 Hz).
    ppg = synthetic_ppg(hr_bpm=72, seconds=250 / 30, fs=PULSEDB_FS)
    assert extract_features(camera_match(ppg, PULSEDB_FS), fs=30.0)["n_beats"] >= 3


def test_flat_signal_raises_clear_error() -> None:
    with pytest.raises(FeatureExtractionError, match="flat"):
        extract_features(np.zeros(300), fs=30.0)


def test_too_few_beats_raises_clear_error() -> None:
    ppg = synthetic_ppg(hr_bpm=45, seconds=4.5, fs=PULSEDB_FS)
    with pytest.raises(FeatureExtractionError, match="clean beats"):
        extract_features(camera_match(ppg, PULSEDB_FS), fs=30.0)
