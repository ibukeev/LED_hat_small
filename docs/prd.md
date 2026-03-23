# PRD — LED Hat Small

Live verision of the PRD is available [here](https://docs.google.com/document/d/1FLzrYwGxkrkdUYWeL5eMNLWcGb3R6WqpmVtx5oFr57E/edit?usp=sharing)

## Product Overview

### Product Description

LED Hat Small is a lightweight, wearable LED hat designed for festivals, night events, and playful self-expression. It prioritizes aesthetics, comfort, safety, and reliability over technical complexity. The product should "just work" with minimal setup and simple controls.

### Target Audience

- **Primary user**: My girlfriend (non-technical, values comfort and aesthetics)
- **Secondary user**: Builder/maintainer (Ilya)

---

## Goals & Success Criteria

### Primary Goals (Must-have)

1. **Looks great**
  - At night: visually striking LED patterns in low-light environments
  - During the day: it should still look good when light patterns are off
2. **Comfortable and safe to wear for several hours**
  - Light enough so that the neck is not getting tired
  - Ideally no wires connecting to external power source (to avoid wire damage)
3. **Reliable operation**
  - No resets, flicker, overheating, or water/dust damage
4. **Extremely simple user interaction**
  - No learning curve

### Success Criteria

- **Battery life**: 3–5 hours minimum of continuous use at capped brightness
- **Comfort**: wearable for 3+ hours without discomfort or excessive heat
- **Reliability**: no crashes, brownouts, or visible glitches during normal use
- **User reaction**: positive aesthetic feedback from wearer

---

## Functional Requirements

### Iteration V1

#### V1 Project Plan

| Feature Group | Work Item | Acceptance Criteria | Priority | Status |
|---|---|---|---|---|
| Core Hardware | Build bench-top LED hat matrix | LED matrix is fully attached in its final geometry, driven by Pixelblaze, powered from an external supply, and usable for pattern testing even if not yet wearable. | P0 | Done |
| Core Hardware | Make the hat wearable | Package wiring inside the hat, mount a USB power bank, and convert the build from external bench power to self-contained wearable power. | P0 | Done |
| Core Hardware | Add Sensor Expansion Board | Sensor Expansion Board is integrated and provides audio, accelerometer, and light-sensor inputs to Pixelblaze patterns. | P0 | Done |
| Core Firmware | Configure Pixelblaze LED mapping | Pixelblaze uses the correct LED count and mapping so patterns render on the intended physical hat geometry. | P0 | Done |
| Core Firmware | Set brightness operating baseline | Global brightness limit is set to a safe baseline (`35%` cap), and a practical default live brightness level is chosen for normal use. | P0 | In Progress |
| Controls & UX | Add external pattern-switch button | A user-accessible external button is mounted and wired so patterns can be switched conveniently while wearing the hat. | P0 | Not Started |
| Controls & UX | Add power on/off switch | Hat includes a convenient physical power switch so normal use does not require plugging and unplugging the battery connection. | P2 | Not Started |
| Controls & UX | Gesture control | Shake, tilt, or nod gestures are added only if they work reliably and remain easy to understand. | P2 | Not Started |
| Power & Safety | Adaptive brightness and battery behavior | Hat adjusts behavior based on battery state and/or environment without making UX more complex. | P2 | Not Started |
| Patterns | First non-audio-reactive pattern | Static Ukrainian flag pattern renders correctly on the hat and is stable enough to serve as the first baseline pattern. | P0 | In Progress |
| Patterns | Curated V1 list of non-audio / accelerometer-reactive patterns | A curated set of reliable non-audio and accelerometer-reactive patterns is selected and works acceptably on the hat. | P0 | In Progress |
| Patterns | Curated list of audio-reactive patterns | A curated set of audio-reactive patterns is selected and works well enough for real-world use on the hat. | P1 | In Progress |
| Patterns | Advanced reactive pattern set | Additional audio-reactive pattern families are added after detector behavior becomes trustworthy. | P2 | Not Started |
| Audio Reactivity | Python kick detection prototype | Offline Python tooling accepts test audio files and produces detector outputs that can be inspected and tuned. A reference detector is selected and frozen for porting. | P1 | Done |
| Audio Reactivity | Port chosen detector to Pixelblaze | The frozen Python reference detector is simplified and ported into one Pixelblaze audio-reactive pattern, then validated on hardware against the target kick behavior. | P1 | In Progress |
| Audio Reactivity | Motion-reactive pattern experiments | Accelerometer-based behavior is tested in at least one pattern and evaluated for real user value. | P1 | Not Started |
| Expansion | Cross-device sync | Hat can synchronize patterns or timing with future wearable LED devices. | P2 | Not Started |

---

## Post-V1 Iterations

### Axis 1: Interaction & Control (UX evolution)

- **Secondary mechanical input**
  - Brightness knob (potentiometer via Pixelblaze expansion)
  - Or second hidden button (brightness up/down)
- **Gesture-based control**
  - Shake / tilt to switch patterns (accelerometer-driven)
  - Nod forward → dim / nod back → brighten
- **Contextual button behavior**
  - Short press: next pattern
  - Long press: toggle “low power mode”
  - Double press: favorite pattern

**Guardrail:** still **no menus**, no learning curve.

### Axis 2: Pattern Intelligence & Reactivity

This is where Pixelblaze really shines. These keep UX simple while making behavior feel “alive”.

- **Motion-reactive patterns**
  - Walking vs standing
  - Dancing vs idle
- **Environmental responsiveness**
  - Ambient light sensor → auto brightness
  - Sound-reactive patterns (if mic added later)
- **“Mood sets”**
  - Calm mode (slow, dim)
  - Party mode (faster, brighter)
  - Still selected with same button, not a UI

### Axis 3: Power & Reliability Enhancements

These are invisible features — perfect for Post-V1. None of this adds user complexity.

- **Battery level signaling via LEDs**
  - Subtle color overlay or pulse
- **Adaptive brightness**
  - Gradual dimming as battery drops
- **Thermal safety behaviors**
  - Auto-dim if internal temp rises
- **Sleep / idle mode**
  - Detect no motion → dim or pause patterns

### Axis 4: Physical / Industrial Design

Purely hardware iteration.

- Modular electronics insert (hat-agnostic)
- Improved diffusion layer (softer light)

### Axis 6: Interconnectivity with other wearables

- When Cat-bike or other LED devices are ready, create interconnectivity between devices so they are lit in-sync  
(will require WiFi hub, etc.)

---

## Non-Goals (Explicitly Out of Scope)

These are intentionally excluded to prevent scope creep:

- No display to live-control the state
- Any web-based UI is limited to what is provided by the controller (e.g., Pixelblaze UI)

---

## Non-Functional Requirements

### Performance

- Smooth animations (no visible stutter)
- Predictable startup behavior
- Pattern switching latency < 500 ms

### Usability

- Zero-instruction use
- Intuitive single-button interaction
- No need to understand electronics or software

### Safety

- LED brightness capped to safe current levels
- No noticeable surface heating
- Battery protection against over-discharge
- All wiring insulated and strain-relieved

---

## Design Requirements

### Physical Design

- Lightweight and balanced on head
- Secure mounting of electronics
- Sweat- and light rain-resistant
- Clean, minimal appearance (electronics hidden)

### Aesthetic Direction

- Expressive but not distracting (not too bright)
- Patterns should feel intentional, not noisy
- Favor smooth color transitions over harsh flashing
- Patterns should leverage Pixelblaze V3 Pico accelerometer functionality

---

## Constraints

### Technical Constraints

- Limited battery capacity (head-mounted)
- Thermal constraints near skin
- **147 LEDs** distributed as a round matrix on top of the hat

### Physical Constraints

- Must not significantly alter hat comfort
- Must not increase head temperature noticeably

### Time & Scope

- Single-person build
- Iterative prototyping acceptable
- V1 optimized for reliability, not feature richness

---

## Key Risks & Mitigation

### Risk: Battery drain or brownouts

- **Mitigation**: conservative brightness cap, power budget modeling

### Risk: Excessive heat

- **Mitigation**: LED density limits, brightness limiting, real-world testing

### Risk: UX complexity

- **Mitigation**: one-button control only, explicit non-goals
