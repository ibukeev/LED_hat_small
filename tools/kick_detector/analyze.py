#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import librosa
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


SAMPLE_RATE = 22050
FRAME_LENGTH = 2048
HOP_LENGTH = 512
N_BANDS = 32
FREQ_MIN = 37.5
FREQ_MAX = 10000.0
SUPPORTED_SUFFIXES = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}


@dataclass(frozen=True)
class DetectorParams:
    low_threshold: float = 0.18
    rising_threshold: float = 0.18
    rearm_threshold: float = 0.11
    ratio_low_threshold: float = 0.12
    bass_high_ratio: float = 2.2
    onset_low_threshold: float = 0.10
    onset_threshold: float = 0.035
    min_interval_s: float = 0.18
    peak_pick_window_s: float = 0.20
    peak_pick_low_threshold: float = 0.16
    peak_pick_low_body_threshold: float = 0.26


@dataclass
class TrackAnalysis:
    path: Path
    slug: str
    y: np.ndarray
    sr: int
    times: np.ndarray
    bands: np.ndarray
    energy_average: np.ndarray
    low_band: np.ndarray
    body_band: np.ndarray
    high_band: np.ndarray
    onset_strength: np.ndarray
    triggers: dict[str, np.ndarray]


def slugify(path: Path) -> str:
    safe = []
    for ch in path.stem.lower():
        if ch.isalnum():
            safe.append(ch)
        else:
            safe.append("-")
    slug = "".join(safe).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "track"


def collect_audio_files(path: Path) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise ValueError(f"Unsupported input file: {path}")
        return [path]
    if not path.is_dir():
        raise ValueError(f"Input does not exist: {path}")
    files = sorted(
        file
        for file in path.iterdir()
        if file.is_file() and file.suffix.lower() in SUPPORTED_SUFFIXES
    )
    if not files:
        raise ValueError(f"No supported audio files found in: {path}")
    return files


def build_band_edges() -> np.ndarray:
    return np.logspace(np.log10(FREQ_MIN), np.log10(FREQ_MAX), N_BANDS + 1)


def normalize_trace(trace: np.ndarray, percentile: float = 99.0) -> np.ndarray:
    scale = float(np.percentile(trace, percentile))
    if not math.isfinite(scale) or scale <= 1e-9:
        scale = float(np.max(trace))
    if not math.isfinite(scale) or scale <= 1e-9:
        scale = 1.0
    return np.clip(trace / scale, 0.0, 1.0)


def extract_features(audio_path: Path) -> TrackAnalysis:
    y, sr = librosa.load(audio_path.as_posix(), sr=SAMPLE_RATE, mono=True)
    stft = librosa.stft(y, n_fft=FRAME_LENGTH, hop_length=HOP_LENGTH, center=True)
    power = np.abs(stft) ** 2
    freqs = librosa.fft_frequencies(sr=sr, n_fft=FRAME_LENGTH)
    times = librosa.frames_to_time(np.arange(power.shape[1]), sr=sr, hop_length=HOP_LENGTH)
    edges = build_band_edges()

    bands = np.zeros((N_BANDS, power.shape[1]), dtype=np.float64)
    for i in range(N_BANDS):
        lo = edges[i]
        hi = edges[i + 1]
        if i == N_BANDS - 1:
            mask = (freqs >= lo) & (freqs <= hi)
        else:
            mask = (freqs >= lo) & (freqs < hi)
        if not np.any(mask):
            center = math.sqrt(lo * hi)
            nearest = int(np.argmin(np.abs(freqs - center)))
            mask = np.zeros_like(freqs, dtype=bool)
            mask[nearest] = True
        bands[i] = power[mask].mean(axis=0)

    for i in range(N_BANDS):
        bands[i] = normalize_trace(bands[i])

    energy = librosa.feature.rms(y=y, frame_length=FRAME_LENGTH, hop_length=HOP_LENGTH, center=True)[0]
    energy = normalize_trace(energy)

    low_band = np.mean(bands[0:5], axis=0)
    body_band = np.mean(bands[5:10], axis=0)
    high_band = np.mean(bands[14:24], axis=0)
    onset_strength = np.maximum(0.0, low_band - np.concatenate(([low_band[0]], low_band[:-1])))

    return TrackAnalysis(
        path=audio_path,
        slug=slugify(audio_path),
        y=y,
        sr=sr,
        times=times,
        bands=bands,
        energy_average=energy,
        low_band=low_band,
        body_band=body_band,
        high_band=high_band,
        onset_strength=onset_strength,
        triggers={},
    )


def apply_refractory(candidate: np.ndarray, times: np.ndarray, min_interval_s: float) -> np.ndarray:
    accepted = np.zeros_like(candidate, dtype=bool)
    last_time = -1e9
    for idx, active in enumerate(candidate):
        if not active:
            continue
        t = float(times[idx])
        if (t - last_time) >= min_interval_s:
            accepted[idx] = True
            last_time = t
    return accepted


def detector_low_band_threshold(track: TrackAnalysis, params: DetectorParams) -> np.ndarray:
    candidate = track.low_band > params.low_threshold
    return apply_refractory(candidate, track.times, params.min_interval_s)


def detector_low_band_rising_edge(track: TrackAnalysis, params: DetectorParams) -> np.ndarray:
    out = np.zeros_like(track.low_band, dtype=bool)
    armed = True
    last_time = -1e9
    for idx, low in enumerate(track.low_band):
        if armed and low > params.rising_threshold and (track.times[idx] - last_time) >= params.min_interval_s:
            out[idx] = True
            armed = False
            last_time = float(track.times[idx])
        elif not armed and low < params.rearm_threshold:
            armed = True
    return out


def detector_bass_vs_high_ratio(track: TrackAnalysis, params: DetectorParams) -> np.ndarray:
    ratio = (track.low_band + 1e-6) / (track.high_band + 1e-6)
    candidate = (track.low_band > params.ratio_low_threshold) & (ratio > params.bass_high_ratio)
    return apply_refractory(candidate, track.times, params.min_interval_s)


def detector_onset_plus_ratio(track: TrackAnalysis, params: DetectorParams) -> np.ndarray:
    ratio = (track.low_band + track.body_band + 1e-6) / (track.high_band + 1e-6)
    candidate = (
        (track.low_band > params.onset_low_threshold)
        & (track.onset_strength > params.onset_threshold)
        & (ratio > params.bass_high_ratio)
    )
    return apply_refractory(candidate, track.times, params.min_interval_s)


def detector_onset_plus_ratio_peak_picked(track: TrackAnalysis, params: DetectorParams) -> np.ndarray:
    ratio = (track.low_band + track.body_band + 1e-6) / (track.high_band + 1e-6)
    base_candidate = (
        (track.low_band > params.onset_low_threshold)
        & (track.onset_strength > params.onset_threshold)
        & (ratio > params.bass_high_ratio)
    )

    # Favor the strongest onset-dominant event in a short neighborhood.
    score = track.onset_strength * (track.low_band + 0.5 * track.body_band) * np.log1p(ratio)
    window_frames = max(1, int(round(params.peak_pick_window_s / (HOP_LENGTH / SAMPLE_RATE))))
    peak_candidate = np.zeros_like(base_candidate, dtype=bool)

    for idx, active in enumerate(base_candidate):
        if not active:
            continue
        start = max(0, idx - window_frames)
        end = min(base_candidate.size, idx + window_frames + 1)
        local_scores = score[start:end]
        local_base = base_candidate[start:end]
        if score[idx] >= np.max(local_scores[local_base]):
            peak_candidate[idx] = True

    return apply_refractory(peak_candidate, track.times, params.min_interval_s)


def detector_onset_plus_ratio_peak_picked_low_qualified(
    track: TrackAnalysis, params: DetectorParams
) -> np.ndarray:
    ratio = (track.low_band + track.body_band + 1e-6) / (track.high_band + 1e-6)
    base_candidate = (
        (track.low_band > params.onset_low_threshold)
        & (track.onset_strength > params.onset_threshold)
        & (ratio > params.bass_high_ratio)
    )

    # Stronger bass/body qualification to reject isolated bright transients.
    qualified = base_candidate & (
        (track.low_band > params.peak_pick_low_threshold)
        | ((track.low_band + track.body_band) > params.peak_pick_low_body_threshold)
    )

    score = track.onset_strength * (track.low_band + 0.5 * track.body_band) * np.log1p(ratio)
    window_frames = max(1, int(round(params.peak_pick_window_s / (HOP_LENGTH / SAMPLE_RATE))))
    peak_candidate = np.zeros_like(qualified, dtype=bool)

    for idx, active in enumerate(qualified):
        if not active:
            continue
        start = max(0, idx - window_frames)
        end = min(qualified.size, idx + window_frames + 1)
        local_scores = score[start:end]
        local_qualified = qualified[start:end]
        if score[idx] >= np.max(local_scores[local_qualified]):
            peak_candidate[idx] = True

    return apply_refractory(peak_candidate, track.times, params.min_interval_s)


def run_detectors(track: TrackAnalysis, params: DetectorParams) -> None:
    track.triggers = {
        "low_band_threshold": detector_low_band_threshold(track, params),
        "low_band_rising_edge": detector_low_band_rising_edge(track, params),
        "bass_vs_high_ratio": detector_bass_vs_high_ratio(track, params),
        "onset_plus_ratio": detector_onset_plus_ratio(track, params),
        "onset_plus_ratio_peak_picked": detector_onset_plus_ratio_peak_picked(track, params),
        "onset_plus_ratio_peak_picked_low_qualified": detector_onset_plus_ratio_peak_picked_low_qualified(
            track, params
        ),
    }


def trigger_times(track: TrackAnalysis, detector_name: str) -> np.ndarray:
    return track.times[track.triggers[detector_name]]


def plot_track(track: TrackAnalysis, output_path: Path) -> None:
    fig, axes = plt.subplots(
        nrows=4,
        ncols=1,
        figsize=(14, 12),
        sharex=False,
        gridspec_kw={"height_ratios": [1.0, 1.3, 1.1, 1.2]},
    )

    axes[0].plot(np.arange(track.y.size) / track.sr, track.y, linewidth=0.7, color="black")
    axes[0].set_title(track.path.name)
    axes[0].set_ylabel("Waveform")

    im = axes[1].imshow(
        track.bands,
        aspect="auto",
        origin="lower",
        extent=[track.times[0], track.times[-1], 0, N_BANDS - 1],
        cmap="magma",
    )
    axes[1].set_ylabel("Band")
    axes[1].set_title("Simulated Pixelblaze frequencyData[32]")
    fig.colorbar(im, ax=axes[1], pad=0.01)

    axes[2].plot(track.times, track.energy_average, label="energyAverage", linewidth=1.0)
    axes[2].plot(track.times, track.low_band, label="low", linewidth=1.0)
    axes[2].plot(track.times, track.body_band, label="body", linewidth=1.0)
    axes[2].plot(track.times, track.high_band, label="high", linewidth=1.0)
    axes[2].plot(track.times, track.onset_strength, label="low onset", linewidth=1.0, alpha=0.9)
    axes[2].set_ylabel("Normalized")
    axes[2].legend(loc="upper right", ncol=5, fontsize=8)

    detector_names = list(track.triggers.keys())
    detector_offsets = np.arange(len(detector_names), dtype=np.float64)
    for idx, name in enumerate(detector_names):
        trig_times = trigger_times(track, name)
        axes[3].eventplot(
            trig_times,
            lineoffsets=detector_offsets[idx],
            linelengths=0.8,
            linewidths=1.5,
            colors=f"C{idx}",
        )
    axes[3].set_yticks(detector_offsets)
    axes[3].set_yticklabels(detector_names)
    axes[3].set_xlabel("Time (s)")
    axes[3].set_title("Detector triggers")

    fig.tight_layout()
    fig.savefig(output_path, dpi=140)
    plt.close(fig)


def write_frame_csv(track: TrackAnalysis, output_path: Path) -> None:
    fieldnames = ["time_s", "energyAverage", "low_band", "body_band", "high_band", "onset_strength"]
    fieldnames.extend(f"band_{i:02d}" for i in range(N_BANDS))
    fieldnames.extend(track.triggers.keys())

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for idx, time_s in enumerate(track.times):
            row = {
                "time_s": f"{float(time_s):.6f}",
                "energyAverage": f"{float(track.energy_average[idx]):.6f}",
                "low_band": f"{float(track.low_band[idx]):.6f}",
                "body_band": f"{float(track.body_band[idx]):.6f}",
                "high_band": f"{float(track.high_band[idx]):.6f}",
                "onset_strength": f"{float(track.onset_strength[idx]):.6f}",
            }
            for band_idx in range(N_BANDS):
                row[f"band_{band_idx:02d}"] = f"{float(track.bands[band_idx, idx]):.6f}"
            for name, values in track.triggers.items():
                row[name] = int(values[idx])
            writer.writerow(row)


def write_summary(rows: list[dict[str, str]], output_path: Path) -> None:
    if not rows:
        return
    fieldnames = ["track", "detector", "trigger_count", "avg_interval_s", "first_triggers_s"]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize_track(track: TrackAnalysis) -> list[dict[str, str]]:
    print(f"\nTrack: {track.path.name}")
    print(f"  Duration: {track.times[-1]:.2f}s")
    rows: list[dict[str, str]] = []
    for name in track.triggers:
        trig = trigger_times(track, name)
        count = int(trig.size)
        avg_interval = float(np.mean(np.diff(trig))) if count >= 2 else 0.0
        first = ", ".join(f"{t:.2f}" for t in trig[:8])
        print(f"  {name}: count={count} avg_interval={avg_interval:.3f}s first=[{first}]")
        rows.append(
            {
                "track": track.path.name,
                "detector": name,
                "trigger_count": str(count),
                "avg_interval_s": f"{avg_interval:.6f}",
                "first_triggers_s": first,
            }
        )
    return rows


def analyze_file(audio_path: Path, output_dir: Path, params: DetectorParams) -> list[dict[str, str]]:
    track = extract_features(audio_path)
    run_detectors(track, params)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_track(track, output_dir / f"{track.slug}.png")
    write_frame_csv(track, output_dir / f"{track.slug}.csv")
    return summarize_track(track)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Offline kick detector comparison tool.")
    parser.add_argument("input", type=Path, help="Audio file or directory of audio files")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("tools/kick_detector/output"),
        help="Directory for generated plots and CSV files",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audio_files = collect_audio_files(args.input)
    params = DetectorParams()
    summary_rows: list[dict[str, str]] = []
    for audio_path in audio_files:
        summary_rows.extend(analyze_file(audio_path, args.output_dir, params))
    write_summary(summary_rows, args.output_dir / "summary.csv")
    print(f"\nWrote output to: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
