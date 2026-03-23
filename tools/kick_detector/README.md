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
- compares one Phase 2 variant:
  - `onset_plus_ratio_peak_picked`
- compares an additional Phase 2 refinement:
  - `onset_plus_ratio_peak_picked_low_qualified`
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

For Pixelblaze capture logging:

```bash
. .venv/bin/activate
pip install pixelblaze-client
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

## Capturing Real Pixelblaze Vars

Use the dedicated debug pattern:

- `firmware/patterns/techno/main-beat-debug.pe`

Then capture exported vars over time:

```bash
. .venv/bin/activate
python tools/kick_detector/capture_pixelblaze_vars.py 192.168.1.50 --duration 35 --interval 0.05 --output-prefix tools/kick_detector/output/monolink-drop-capture
```

This writes:

- `*.jsonl`
- `*.csv`

The capture includes:

- timestamps
- `energyAverage`
- flattened `frequencyData_00` ... `frequencyData_31`
- all exported `dbg...` detector intermediates

## Replaying a Pixelblaze Capture

You can replay the current Pixelblaze detector logic against a captured CSV:

```bash
python tools/kick_detector/replay_pixelblaze_capture.py tools/kick_detector/output/monolink-drop-capture.csv --output-prefix tools/kick_detector/output/monolink-drop-replay
```

This prints a summary of:

- how often replayed `candidate` matches logged `dbgCandidate`
- how often replayed `accepted` matches logged `dbgAccepted`
- total replayed vs logged candidate/accepted counts

And optionally writes:

- replay row CSV
- replay summary JSON

## Outputs

By default artifacts are written to:

- `tools/kick_detector/output/<track_slug>.png`
- `tools/kick_detector/output/<track_slug>.csv`
- `tools/kick_detector/output/summary.csv`

The plots are intended for visual comparison with:

- `Data/example_tracks/example_visualizer/`

Those reference assets are not required for the analyzer to run.
