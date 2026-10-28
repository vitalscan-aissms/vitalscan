"""Pulse-shape features for the experimental BP model (M8), shared by training and the server.

Purpose:
    Turn a clean pulse wave into one row of numbers describing the shape of its heartbeats
    (how fast each beat rises, how wide it is, how its area is split). The BP model learns
    blood pressure from these numbers plus age, sex and BMI.
Inputs:
    A clean 1-D pulse (systolic peaks pointing up) and its sampling rate. For training on PulseDB,
    first pass the finger PPG through ``camera_match`` so it looks like what our webcam produces.
Outputs:
    ``dict[str, float]`` with every name in ``FEATURE_NAMES``.
Example:
    >>> from vitalscan.utils.synthetic import synthetic_ppg
    >>> pulse = camera_match(synthetic_ppg(hr_bpm=72, seconds=10, fs=125), fs=125)
    >>> round(extract_features(pulse, fs=30)["hr_bpm"])
    72

Why camera matching matters (research question RQ3): PulseDB is a clean 125 Hz finger signal,
ours is a noisy 30 Hz band-passed face signal. Fine details such as the dicrotic notch vanish at
30 Hz. Training on features the camera can never see would give a model that fails on faces, so
training data goes through the same resample + detrend + band-pass chain as live scans.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
from scipy.signal import find_peaks

from vitalscan.signal_processing.filters import (
    DEFAULT_TARGET_FS,
    bandpass,
    detrend_signal,
    resample_uniform,
)

logger = logging.getLogger(__name__)

ANALYSIS_FS = 120.0          # band-limited (< 4 Hz) pulse is upsampled for finer beat timing
MIN_BEAT_S, MAX_BEAT_S = 0.25, 1.5   # 40-240 bpm
MAX_DURATION_DEVIATION = 0.30        # beat length may differ from the median by at most 30 %
MIN_GOOD_BEATS = 3
EDGE_S = 1.0                         # band-pass filtering distorts the first and last second
WIDTH_LEVELS = (0.25, 0.50, 0.75)

BEAT_FEATURES = (
    "duration_s",
    "rise_time_s",
    "fall_time_s",
    "rise_ratio",
    "width_25_s",
    "width_50_s",
    "width_75_s",
    "area_ratio_dia_sys",
    "max_upslope_per_s",
    "vpg_peak_time_s",
    "apg_b_a",
)
RECORDING_FEATURES = ("hr_bpm", "ibi_sdnn_ms", "ibi_rmssd_ms", "n_beats", "beat_quality")
FEATURE_NAMES = BEAT_FEATURES + RECORDING_FEATURES


class FeatureExtractionError(ValueError):
    """Raised when a pulse has too few clean beats to describe its shape."""


@dataclass(frozen=True)
class Beat:
    """Sample indices of one heartbeat: start (foot), systolic peak, and end (next foot)."""

    foot: int
    peak: int
    end: int


def camera_match(ppg: np.ndarray, fs: float) -> np.ndarray:
    """Make a contact (finger) PPG look like our camera pulse: 30 Hz, detrended, band-passed.

    Inputs: ``ppg`` (N,) evenly sampled at ``fs`` Hz (125 Hz for PulseDB).
    Outputs: (about N * 30 / fs,) pulse at ``DEFAULT_TARGET_FS`` Hz.
    """
    at_camera_rate = resample_uniform(ppg, fs, DEFAULT_TARGET_FS)
    return bandpass(detrend_signal(at_camera_rate), DEFAULT_TARGET_FS)


def dominant_period_s(pulse: np.ndarray, fs: float) -> float:
    """Beat period (seconds) from the strongest frequency in the 40-240 bpm band."""
    spectrum = np.abs(np.fft.rfft(pulse - pulse.mean()))
    freqs = np.fft.rfftfreq(pulse.size, d=1 / fs)
    in_band = (freqs >= 1 / MAX_BEAT_S) & (freqs <= 1 / MIN_BEAT_S)
    return 1.0 / float(freqs[in_band][np.argmax(spectrum[in_band])])


def find_beats(pulse: np.ndarray, fs: float) -> list[Beat]:
    """Locate every complete beat (foot -> peak -> next foot) in a clean pulse.

    Inputs: ``pulse`` (N,) with systolic peaks pointing up, sampled at ``fs`` Hz.
    Outputs: list of ``Beat``. Beats touching the first or last ``EDGE_S`` seconds are
    skipped: there the filter has not settled and beat boundaries are misplaced.

    Peaks must be at least 60 % of the spectral beat period apart. Without this, the
    diastolic (reflected) wave is often counted as an extra heartbeat.
    """
    robust_range = float(np.percentile(pulse, 95) - np.percentile(pulse, 5))
    if robust_range <= 1e-12:
        raise FeatureExtractionError("Pulse is flat; no heartbeats to measure")
    min_gap_s = max(MIN_BEAT_S, 0.6 * dominant_period_s(pulse, fs))
    peaks, _ = find_peaks(pulse, distance=max(1, int(min_gap_s * fs)),
                          prominence=0.2 * robust_range)
    # The foot of a beat is the lowest point between it and the previous peak.
    feet = [int(a + np.argmin(pulse[a:b])) for a, b in zip(peaks[:-1], peaks[1:], strict=True)]
    beats = [Beat(feet[i - 1], int(peaks[i]), feet[i]) for i in range(1, len(peaks) - 1)]
    edge = int(EDGE_S * fs)
    return [b for b in beats if b.foot >= edge and b.end <= pulse.size - 1 - edge]


def select_good_beats(pulse: np.ndarray, beats: list[Beat], fs: float) -> list[Beat]:
    """Keep beats with a plausible length (40-240 bpm, near the median) and a real upstroke."""
    plausible = [
        b for b in beats
        if MIN_BEAT_S <= (b.end - b.foot) / fs <= MAX_BEAT_S and pulse[b.peak] > pulse[b.foot]
    ]
    if not plausible:
        return []
    median_len = float(np.median([b.end - b.foot for b in plausible]))
    return [b for b in plausible
            if abs((b.end - b.foot) - median_len) <= MAX_DURATION_DEVIATION * median_len]


def _crossing_time(y: np.ndarray, level: float, start: int, step: int) -> float:
    """Walk from ``start`` in direction ``step`` until ``y`` drops below ``level``.

    Returns the interpolated (fractional) sample index of the crossing, or NaN if never reached.
    """
    i = start
    while 0 <= i + step < y.size:
        nxt = i + step
        if y[nxt] < level:
            frac = (y[i] - level) / (y[i] - y[nxt])
            return i + step * frac
        i = nxt
    return float("nan")


def beat_features(pulse: np.ndarray, beat: Beat, fs: float) -> dict[str, float]:
    """Shape features of one beat, normalised so foot-to-foot baseline = 0 and peak = 1.

    Inputs: ``pulse`` (N,), one ``Beat`` inside it, sampling rate ``fs``.
    Outputs: dict with every name in ``BEAT_FEATURES`` (times in seconds).
    """
    seg = pulse[beat.foot:beat.end + 1]
    baseline = np.linspace(seg[0], seg[-1], seg.size)
    peak = beat.peak - beat.foot
    y = (seg - baseline) / (seg[peak] - baseline[peak])

    widths = {f"width_{int(lv * 100)}_s":
              (_crossing_time(y, lv, peak, +1) - _crossing_time(y, lv, peak, -1)) / fs
              for lv in WIDTH_LEVELS}
    vpg = np.gradient(y) * fs                  # velocity: first derivative
    apg = np.gradient(vpg) * fs                # acceleration: second derivative
    a_idx = int(np.argmax(apg[:peak + 1]))
    a, b = apg[a_idx], float(np.min(apg[a_idx:peak + 1]))
    systolic_area = float(np.trapezoid(y[:peak + 1]))
    duration = (beat.end - beat.foot) / fs
    return {
        "duration_s": duration,
        "rise_time_s": peak / fs,
        "fall_time_s": (beat.end - beat.peak) / fs,
        "rise_ratio": peak / fs / duration,
        **widths,
        "area_ratio_dia_sys": float(np.trapezoid(y[peak:])) / systolic_area,
        "max_upslope_per_s": float(np.max(vpg[:peak + 1])),
        "vpg_peak_time_s": float(np.argmax(vpg[:peak + 1])) / fs,
        "apg_b_a": b / a if a > 0 else float("nan"),
    }


def extract_features(pulse: np.ndarray, fs: float = DEFAULT_TARGET_FS) -> dict[str, float]:
    """Summarise a recording as one feature row: the median of each beat feature plus rhythm.

    Inputs: clean ``pulse`` (N,) at ``fs`` Hz, e.g. M6 output or ``camera_match`` of a PPG.
    Outputs: dict with every name in ``FEATURE_NAMES``.
    Raises: ``FeatureExtractionError`` if fewer than ``MIN_GOOD_BEATS`` clean beats are found.
    """
    fine = resample_uniform(pulse, fs, ANALYSIS_FS)
    beats = find_beats(fine, ANALYSIS_FS)
    good = select_good_beats(fine, beats, ANALYSIS_FS)
    if len(good) < MIN_GOOD_BEATS:
        raise FeatureExtractionError(
            f"Only {len(good)} clean beats found (need {MIN_GOOD_BEATS}); signal too short or noisy"
        )
    rows = [beat_features(fine, b, ANALYSIS_FS) for b in good]
    features = {name: float(np.nanmedian([r[name] for r in rows])) for name in BEAT_FEATURES}

    ibi_ms = np.array([r["duration_s"] for r in rows]) * 1000.0
    features["hr_bpm"] = 60.0 / features["duration_s"]
    features["ibi_sdnn_ms"] = float(np.std(ibi_ms, ddof=1))
    features["ibi_rmssd_ms"] = float(np.sqrt(np.mean(np.diff(ibi_ms) ** 2)))
    features["n_beats"] = float(len(good))
    features["beat_quality"] = len(good) / len(beats)
    logger.debug("Extracted features from %d/%d beats", len(good), len(beats))
    return features
