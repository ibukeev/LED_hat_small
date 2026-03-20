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
- Key controls:
  - `Intensity`
  - `BlockCount`
  - `StrobeLength`
  - `Crackle`
  - `AccentColor`
- Signature moment: periodic blackout then full-white slam.
- Status: Candidate

### 2) Tunnel Scanner
- Concept: single scanning beam with trails and spark artifacts.
- Audio mapping:
  - Low: widen/brighten beam.
  - Mid: add trailing echoes.
  - High: spark noise around beam.
- Key controls:
  - `SweepSpeed`
  - `BeamWidth`
  - `TrailDecay`
  - `Jitter`
  - `AccentColor`
- Signature moment: beam freeze on peak, then double-speed release.
- Status: Candidate

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
