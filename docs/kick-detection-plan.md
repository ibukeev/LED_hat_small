# Kick Detection Plan

This document tracks the plan for developing kick detection offline in Python first, then porting the chosen logic into Pixelblaze patterns.

## Goal

Build and tune a kick detector outside Pixelblaze so detector behavior can be debugged against real audio files before translating the logic into Pixelblaze expression language.

## Inputs

- Primary input format: `mp3`
- Secondary input format: `wav`
- Test set should include:
  - clap / hand-hit recordings
  - flatter drum-machine kick examples
  - techno / psytrance tracks

## Python Tooling

- `librosa`
  - audio loading
  - STFT / spectral features
  - onset-related helpers if needed
- `numpy`
  - frame math
  - detector logic
- `matplotlib.pyplot`
  - waveform / spectrogram / detector debug plots

## Simulated Pixelblaze-Like Features

The Python prototype should compute frame-by-frame features that approximate Sensor Expansion Board inputs:

- `frequencyData[32]`
- `energyAverage`
- optional helper traces:
  - low-band energy
  - body-band energy
  - high-band energy
  - onset strength

The goal is not perfect hardware emulation. The goal is to produce a simple feature stream that can later be approximated in Pixelblaze.

## Prototype Scope

Start with a minimal offline analyzer:

- load an audio file
- convert to mono
- resample if needed
- compute short analysis frames
- generate 32-band spectral features
- run several candidate kick detectors on the same feature stream
- output trigger timestamps plus plots for inspection

## Detector Variants To Compare

Phase 1 should compare exactly these four detectors:

1. `low_band_threshold`
2. `low_band_rising_edge`
3. `bass_vs_high_ratio`
4. `onset_plus_ratio`

The first phase is comparison, not premature optimization.

## Evaluation Workflow

For each test file:

1. Run the analyzer
2. Plot waveform and detector features
3. Mark trigger timestamps
4. Inspect:
   - missed kicks
   - false positives
   - startup behavior
   - behavior during silence / interludes

## Porting Strategy

Once one detector clearly performs best:

1. Reduce it to the smallest useful state machine
2. Remove nonessential Python-side complexity
3. Port the logic into Pixelblaze using similar feature semantics
4. Validate on hardware with the same test clips / speaker setup

## Guardrails

- Keep the Python detector simple enough to port
- Avoid depending on analysis features that Pixelblaze cannot reasonably approximate
- Separate detector tuning from visual pattern tuning
- Do not add visual complexity until the detector itself is trustworthy

## Deliverables

- Python analyzer script
- example run instructions
- plots / trigger outputs for a small test corpus
- final documented detector logic to port into Pixelblaze

## Implementation Plan

### Example Track Corpus

Phase 1 will use the current example set in `Data/example_tracks/`:

- `Kick Drum _ BPM 100 [9hXSNhds1JA].mp3`
- `Howling - 'Signs' (Rødhåd Remix).mp3`
- `Monolink - Return To Oz (ARTBAT Remix).mp3`

Reference visualizations are also available in:

- `Data/example_tracks/example_visualizer/`

Planned usage:

- use the isolated kick track as the calibration reference
- use the two musical tracks as realism checks for false positives and missed kicks
- use the external visualizer assets as manual comparison material when evaluating detector plots

The Python analyzer should remain self-contained and must not depend on the external visualizer files to run.

### Proposed Directory Structure

- `tools/kick_detector/analyze.py`
- `tools/kick_detector/README.md`
- `tools/kick_detector/output/`

`output/` should contain generated artifacts only, for example:

- per-track plots
- CSV or JSON summaries
- trigger timestamp exports

### Phase 1 Scope

Phase 1 should stay narrow:

1. accept one input file or a folder of files
2. load audio with `librosa`
3. convert to mono and normalize sample rate
4. compute frame-based spectral analysis
5. reduce spectral data into a Pixelblaze-like `frequencyData[32]`
6. compute an `energyAverage`-like trace
7. run several candidate detectors over the same feature stream
8. save plots and trigger summaries

### Standard Analysis Settings

Initial defaults should be fixed and documented so runs are comparable:

- sample rate: `22050`
- frame length: `2048`
- hop length: `512`
- output bands: `32`

These values can be changed later, but Phase 1 should avoid parameter churn.

Current decision:

- `22050 / 2048 / 512` is the agreed Phase 1 baseline
- this is a practical debugging-friendly approximation, not a claim of exact Pixelblaze internals

### Features To Compute

For each analysis frame:

- `frequencyData[32]`
- `energyAverage`
- low-band energy
- body-band energy
- high-band energy
- optional onset-strength helper trace

### Pixelblaze-Like Band Mapping

For Phase 1, `frequencyData[32]` should be approximated using a Pixelblaze-like log-spaced band layout instead of generic mel bands.

Current decision:

- use `32` log-spaced bands
- approximate Pixelblaze coverage from about `37.5 Hz` to `10 kHz`
- aggregate FFT energy into those bands per frame

Reasoning:

- official Pixelblaze materials describe `frequencyData` as `32` bands covering roughly `37 Hz` to `10 kHz`
- forum discussion references early frequency buckets around `37.5`, `50`, `75`, and `100 Hz`
- this is closer to Pixelblaze behavior than a generic mel mapping

Important note:

- this is still an approximation
- the exact internal Pixelblaze bucket mapping, FFT windowing, and smoothing behavior are not yet confirmed from official documentation

### Detector Variants In Phase 1

Each detector should emit:

- trigger frame indices
- trigger timestamps in seconds
- trigger count per file

Current decision:

- Phase 1 should compare exactly these four detectors:
  1. `low_band_threshold`
  2. `low_band_rising_edge`
  3. `bass_vs_high_ratio`
  4. `onset_plus_ratio`
- the purpose of Phase 1 is to analyze the performance of each approach on the example corpus and select one detector for Pixelblaze porting

### Outputs Per Track

Each track run should produce:

- waveform plot
- spectrogram or 32-band heatmap
- low/body/high energy traces
- detector traces
- trigger markers for each detector

In addition, save a machine-readable summary:

- CSV or JSON with frame-level features and detector outputs

Current decision:

- Phase 1 output format should include:
  - one `PNG` visualization per track
  - one frame-level `CSV` per track
  - a short terminal summary per detector
- an aggregate `summary.csv` is optional and can be added if useful after the first implementation

### Evaluation Method

For each track:

1. inspect whether the isolated kick track triggers reliably
2. inspect whether the musical tracks trigger on obvious kicks
3. note false triggers on hats, claps, synth pulses, or silence
4. compare detector behavior before deciding what to port

### Phase 1 Success Criteria

Phase 1 is complete when:

- the analyzer runs on the full example corpus
- plots are generated for each track
- all detector variants can be compared on the same features
- one or two detector candidates are clearly promising enough to simplify and port

### After Phase 1

Once a detector candidate looks promising:

1. reduce it to a minimal state machine
2. verify it does not depend on features that are too expensive or awkward for Pixelblaze
3. port it into a very simple Pixelblaze pattern first
4. only after detector validation, add visual complexity back in
