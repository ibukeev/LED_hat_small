# Techno Pattern Backlog

This document tracks sound-reactive pattern ideas for a techno/underground bunker visual style on the LED hat.

## Context
- Target mood: industrial, dark, high contrast, rhythmic.
- Constraint: hat has only 7 pixels in height, so patterns must remain legible at low vertical resolution.
- Runtime target: Pixelblaze pattern editor with exposed controls for live tuning.

## Candidate Patterns

### 1) Bunker Strobe Grid
- Concept: virtual block grid with quantized on/off hits.
- Audio mapping:
  - Low (kick): full block hits.
  - Mid (snare/clap): block selection rotation.
  - High (hat): edge crackle/flicker.
- Key controls (minimal v0.1):
  - `Level`
  - `Reactivity`
  - `Color`
- Signature moment: periodic blackout then full-white slam.
- Status: Active (v0.1 minimal in testing)

### 2) Tunnel Scanner
- Concept: single scanning beam with trails and spark artifacts.
- Audio mapping:
  - Low: widen/brighten beam.
  - Mid: add trailing echoes.
  - High: spark noise around beam.
- Key controls (current):
  - `Level`
  - `Reactivity`
- Signature moment: beam freeze on peak, then double-speed release.
- Status: Active (v0.3 in testing)

### 3) Riot Pulse
- Concept: aggressive center-out and edge-in shockwaves.
- Audio mapping:
  - Low: outward wave.
  - Mid: inward snap.
  - High: static grain overlay.
- Key controls:
  - `PulseWidth`
  - `Decay`
  - `KickGain`
  - `SnareGain`
  - `GrainAmount`
- Signature moment: periodic stacked double-hit.
- Status: Candidate

### 4) Machine Fault
- Concept: stable dim baseline with glitch/fault bursts.
- Audio mapping:
  - Low: brownout dip/rebound.
  - Mid: segment desync events.
  - High: micro-flicker noise.
- Key controls:
  - `BaseLevel`
  - `FaultChance`
  - `FaultDuration`
  - `RecoverySpeed`
  - `Noise`
- Signature moment: rare fault cascade then clean re-sync.
- Status: Candidate

### 5) Blackout Lightning
- Concept: almost-black output with brief lightning/strobe strikes on kick.
- Audio mapping:
  - Low: kick onset triggers bolt spawn + flash.
  - Energy: controls strike intensity and width.
  - Mid/high: intentionally minimized in v0.1 for clarity.
- Key controls (minimal v0.1):
  - `Level`
  - `Reactivity`
  - `Color`
- Signature moment: short white clip flash followed by fading random bolt lines.
- Status: Active (v0.1 minimal in testing)

## Quick Evaluation Matrix (Draft)

| Pattern | Aggression | Readability @ 7px height | Risk of Looking Messy |
|---|---|---|---|
| Bunker Strobe Grid | High | High | Medium |
| Tunnel Scanner | Medium-High | Very High | Low |
| Riot Pulse | Very High | Medium | Medium-High |
| Machine Fault | High | Medium-High | High |

## Initial Recommendation
- Best first implementation candidate: **Tunnel Scanner**
- Why:
  - Most readable on a 7px-tall surface.
  - Strong bunker vibe without over-cluttering.
  - Low implementation risk and easy live control tuning.

## Next Step
- Pick one pattern and build a minimal v1 with:
  - core audio mapping,
  - 5-8 controls in Pixelblaze UI,
  - safe defaults (no crash-prone parameter ranges).

## Tunnel Scanner Iteration Notes

### Implementation Path
- Pattern file created at: `firmware/patterns/techno/tunnel-scanner.pe`.
- Kept compatibility entry points:
  - `beforeRender(delta)`
  - `render(index)`
  - `render2D(index, x, y)`
  - `render3D(index, x, y, z)`
- Removed synthetic/no-audio fallback after testing to isolate true reactivity.

### What Changed (Recent)
- Switched from light-sensor delta reactivity to Sensor Expansion Board audio variables:
  - `frequencyData[32]`
  - `energyAverage`
  - `maxFrequency`
  - `maxFrequencyMagnitude`
- Added absolute energy gating tuned to measured values:
  - idle: `energyAverage ~0.0005`
  - music: `energyAverage ~0.01`
  - pattern defaults: `energyFloor=0.0012`, `energyCeil=0.012`
- Reduced UI to minimal controls:
  - `Level` for brightness
  - `Reactivity` macro for sensitivity/behavior
- Added bass onset detector (`kick`) for punchier kick flashes:
  - rising-edge detection from low band
  - short decay flash envelope
  - scanner speed spike on kick
- Lowered onset threshold to trigger more easily with small speaker:
  - `onset > 0.07` -> `onset > 0.045`

### Current Defaults (v0.3)
- `intensity=0.8`
- `darknessFloor=0.0`
- `sweepSpeed=0.65`
- `beamWidth=0.14`
- `trailDecay=0.42`
- `kickBoost=2.1`
- `sparkAmount=0.34`
- `audioGain=1.8`
- `energyFloor=0.0012`
- `energyCeil=0.012`
- `paletteMode=1` (acid green)

### What We Learned
- The pattern can look non-reactive if using `light` sensor instead of true audio vars.
- Absolute gating performs better than normalized-only gating for this hardware/speaker setup.
- Minimal controls improve test clarity during iteration.

### Next Iteration Focus
- Increase perceived kick separation without raising noise floor.
- Option A: stronger kick flash contrast.
- Option B: temporary hold/freeze of beam position on kick to make hits more legible.

## Bunker Strobe Grid Iteration Notes

### Implementation
- Pattern file: `firmware/patterns/techno/bunker-strobe-grid.pe`
- Goal: very minimal baseline for fast tuning.
- Uses Sensor Expansion Board audio vars:
  - `frequencyData[32]`
  - `energyAverage`

### Current Behavior (v0.1)
- 8 virtual block columns around hat.
- Low band controls block activation density.
- Mid band adds alternating checker/step structure.
- High band adds sparse shimmer/random spark enables.
- Absolute `energyAverage` gate controls overall punch.

### Controls (minimal)
- `Level` (overall brightness)
- `Reactivity` (sensitivity and gate window)
- `Color` (hue)

### Why Minimal First
- Isolate audio behavior before adding style complexity.
- Keep only controls needed to answer: "does this react clearly to music?"
