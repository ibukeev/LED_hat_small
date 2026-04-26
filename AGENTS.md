# AGENTS.md

Project-specific memory and conventions for `LED_hat_small`.

## Purpose
- Keep stable decisions and known-good conventions in one place.
- Prefer updating this file when we learn something durable about hardware, mapping, pattern behavior, or workflow.

## Pixelblaze Pattern Workflow
- Source patterns in this repo are `.pe` files.
- Pixelblaze "Open File" expects `.epe` exports; for `.pe`, use copy/paste into Pattern Editor.
- For compatibility, patterns should implement:
  - `beforeRender(delta)`
  - `render(index)` (required fallback)
  - optional `render2D(index, x, y)` and `render3D(index, x, y, z)`
- Avoid per-frame/per-pixel array allocations inside render paths to reduce crash risk.

## Pattern Organization
- Use themed folders under `firmware/patterns/`:
  - `techno/`
  - `burning-man/`
  - `general/`
- Current files:
  - `firmware/patterns/techno/tunnel-scanner.pe`
  - `firmware/patterns/techno/main-beat-flash.pe`
  - `firmware/patterns/techno/main-beat-debug.pe`
  - `firmware/patterns/general/aurora.pe`
  - `firmware/patterns/general/waves.pe`
  - `firmware/patterns/general/ukrainian-flag.pe`

## Sensor Expansion Board Memory
- This project uses Pixelblaze Sensor Expansion Board support.
- Audio-reactive variables available in patterns include:
  - `frequencyData` (32 bands)
  - `energyAverage`
  - `maxFrequency`
  - `maxFrequencyMagnitude`
- Other sensor variables used here:
  - `accelerometer`
  - `light`
- Detection convention:
  - `energyAverage >= 0` indicates audio data present.
  - `light == -1` means sensor board not detected for light sensor patterns.

## Known Geometry Notes
- Hat height is 7 pixels.
- For clean 1D splits, sample pixel centers with:
  - `x = (index + 0.5) / pixelCount`
- Ukrainian flag requirement:
  - Center boundary should resolve to blue for recognizability on odd pixel counts.

## Tunnel Scanner Conventions
- File: `firmware/patterns/techno/tunnel-scanner.pe`
- Current intent:
  - True audio reactivity from Sensor Expansion Board (no synthetic fallback beat engine).
  - Minimal UI controls for live use.
  - `Energy` slider acts as macro sensitivity control.

## Audio-Reactive Control Conventions
- When separating audio-reactive controls, prefer distinct meanings:
  - `Input Gain`: scales incoming audio influence before event detection.
  - `Trigger Sensitivity`: controls how easily hits or events are allowed to trigger.
- Avoid one slider driving both gain and trigger threshold when that makes UI behavior feel inverted.
- For high-gain live use, prefer soft compression/shaping over hard clipping in detector paths so kick onsets remain visible.
- `firmware/patterns/techno/blackout-lightning.pe` follows this split-control approach.

## Kick Detector Baseline
- The frozen offline Python reference detector is:
  - `onset_plus_ratio_peak_picked_low_qualified`
- Current calibration excerpt baseline:
  - `Monolink - Return To Oz - 04m35s-05m05s`
  - expected Python result:
    - no flashes before about `23.15s`
    - `15` flashes from about `23.15s` to `29.93s`
    - spacing about `0.485s` (`~124 BPM`)
- Porting intent for Pixelblaze:
  - derive low/body/high energy from `frequencyData`
  - compute low-band onset from normalized low energy rise
  - require bass dominance plus low/body qualification
  - perform short local peak picking before accepting a trigger
  - validate with a minimal whole-hat flash pattern before adding more visual complexity
- Initial live port target:
  - `firmware/patterns/techno/main-beat-flash.pe`
- Current calibration workflow:
  - `firmware/patterns/techno/main-beat-debug.pe` exports raw inputs, detector features, thresholds, and trigger flags
  - `tools/kick_detector/capture_pixelblaze_vars.py` records exported vars to CSV / JSONL
  - `tools/kick_detector/replay_pixelblaze_capture.py` replays the Pixelblaze detector offline against captured export data
  - detector logic is quantized to a fixed `50 ms` tick during calibration so capture and replay align
  - `dbgAccepted` is latched for one detector tick so logged accepted events match visible flashes more closely
- Current live/debug detector grouping on Pixelblaze:
  - `sub = bins 0..2`
  - `core = bins 1..6`
  - `body = bins 7..11`
  - neutral mids `12..20` ignored
  - `contamination = bins 21..25`
- Current workflow rule:
  - detector ideas should be tested in replay against captured Pixelblaze exports first
  - only detector changes that clearly improve replay/logged behavior should be promoted back into Pixelblaze patterns
- Current instrumentation note:
  - Pixelblaze debug exports now include:
    - `dbgTickId`
    - `dbgDetectorTimeS`
  - websocket/exported-vars capture is useful for coarse detector calibration, but it drops a noticeable fraction of detector ticks
  - treat replay from captured exports as approximate, not exact per-tick ground truth
- Recently tried and reverted:
  - `supportRawRatio` short-term growth gate
  - it reduced some false triggers but hurt post-drop recall too much
- Current hardware calibration reference set:
  - `Monolink - Return To Oz - 04m35s-05m05s`
    - hard false-trigger / pre-drop case
  - `Becoming Insane - 03m45s-04m15s`
    - transition into real beat case
  - `Kick Drum BPM 100 - 30s`
    - clean kick sanity baseline
- Important current guardrail:
  - the current live/debug detector fully misses `Kick Drum BPM 100 - 30s`
  - future replay-side detector experiments must recover this easy baseline before being promoted back to Pixelblaze
- Current export-path conclusion:
  - no clearly better documented transport than exported vars over the Pixelblaze websocket/UI path has been found
  - Firestorm appears to wrap the same underlying websocket API rather than providing a distinct high-fidelity logging channel

## Documentation Update Rule
- If pattern folder layout, sensor variable usage, or control philosophy changes, update:
  - `AGENTS.md` (this file)
  - `firmware/README.md` (user-facing paths and pattern list)
