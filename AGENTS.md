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
- Porting intent for Pixelblaze:
  - derive low/body/high energy from `frequencyData`
  - compute low-band onset from normalized low energy rise
  - require bass dominance plus low/body qualification
  - perform short local peak picking before accepting a trigger
  - validate with a minimal whole-hat flash pattern before adding more visual complexity
- Initial live port target:
  - `firmware/patterns/techno/main-beat-flash.pe`

## Documentation Update Rule
- If pattern folder layout, sensor variable usage, or control philosophy changes, update:
  - `AGENTS.md` (this file)
  - `firmware/README.md` (user-facing paths and pattern list)
