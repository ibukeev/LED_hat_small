# Kick Detector Analyzer

Offline Phase 1 analyzer for comparing simple kick-detection approaches against the example track corpus before porting one detector to Pixelblaze.

## Scope

This tool:

- loads `mp3` or `wav` audio
- resamples to the agreed Phase 1 baseline
- approximates Pixelblaze `frequencyData[32]` using 32 log-spaced bands from about `37.5 Hz` to `10 kHz`
- computes a simple `energyAverage`-like frame trace
- compares four detector variants:
  - `low_band_threshold`
  - `low_band_rising_edge`
  - `bass_vs_high_ratio`
  - `onset_plus_ratio`
- emits per-track:
  - `PNG` visualization
  - frame-level `CSV`
  - terminal summary

## Dependencies

Install into a local virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install librosa matplotlib numpy
```

## Usage

Analyze the example corpus:

```bash
python tools/kick_detector/analyze.py Data/example_tracks
```

Analyze a single file:

```bash
python tools/kick_detector/analyze.py "Data/example_tracks/Kick Drum _ BPM 100 [9hXSNhds1JA].mp3"
```

Write output somewhere else:

```bash
python tools/kick_detector/analyze.py Data/example_tracks --output-dir /tmp/kick-detector-output
```

## Outputs

By default artifacts are written to:

- `tools/kick_detector/output/<track_slug>.png`
- `tools/kick_detector/output/<track_slug>.csv`
- `tools/kick_detector/output/summary.csv`

The plots are intended for visual comparison with:

- `Data/example_tracks/example_visualizer/`

Those reference assets are not required for the analyzer to run.
