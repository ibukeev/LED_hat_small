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

## Documentation Update Rule
- If pattern folder layout, sensor variable usage, or control philosophy changes, update:
  - `AGENTS.md` (this file)
  - `firmware/README.md` (user-facing paths and pattern list)
