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

#### Core Features (V1)
- Display animated LED patterns on the hat’s outer surface (covering hat as an LED matrix)
- Switch between a small set of predefined patterns using **mechanical control** as a primary control  
  (any BT/WiFi connectivity can be a secondary one)
- Global brightness limiting for power and heat safety
- Battery-powered operation with safe shutdown behavior

#### User Interaction (V1)
- Primary control (assuming PixelBlaze V3 Pico limitations)
  - Button press → next pattern
- No phone app required in V1
- No complex setup or configuration required

#### Pattern Management (V1)
- Patterns are preloaded at build time
- No dynamic upload or editing in V1
- Pattern set is curated and limited (quality > quantity)

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
