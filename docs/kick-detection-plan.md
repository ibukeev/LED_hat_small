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

## Pixelblaze Calibration Step

The first direct Pixelblaze port exposed a gap between the offline simulator and real Pixelblaze behavior. The next step is to calibrate against real on-device data rather than continue blind threshold tuning.

### Goal

Capture real Pixelblaze Sensor Expansion Board values during playback of known test excerpts and replay them in Python so detector tuning can be done against actual Pixelblaze-like input streams.

### Dedicated Logger Pattern

Use:

- `firmware/patterns/techno/main-beat-debug.pe`

This debug pattern exports:

- `frequencyData[32]`
- `energyAverage`
- detector intermediates such as:
  - `dbgLowRaw`
  - `dbgBodyRaw`
  - `dbgHighRaw`
  - `dbgLowNorm`
  - `dbgBodyNorm`
  - `dbgHighNorm`
  - `dbgLowRise`
  - `dbgRatio`
  - `dbgRawRatio`
  - `dbgSignalActive`
  - `dbgHighDominant`
  - `dbgLowQualified`
  - `dbgRawBassSupport`
  - `dbgCandidate`
  - `dbgAccepted`

### Workflow

1. Load `main-beat-debug.pe` onto Pixelblaze
2. Play a known excerpt already used in the Python evaluation corpus
3. Capture exported vars over time from Pixelblaze
4. Save the captured stream to a machine-readable file
5. Replay that stream in Python
6. Compare:
   - simulated Python features
   - real Pixelblaze features
   - detector decisions
7. Adjust the Python-side Pixelblaze approximation before further on-device tuning

### Current Calibration Workflow

The current calibration path is:

1. Freeze the offline Python reference detector
   - current reference:
     - `onset_plus_ratio_peak_picked_low_qualified`
2. Run a dedicated Pixelblaze debug pattern that exports:
   - raw sensor inputs
   - normalized detector features
   - candidate / accepted trigger flags
   - detector thresholds and internal state
3. Capture those exported vars over time into CSV / JSONL using:
   - `tools/kick_detector/capture_pixelblaze_vars.py`
4. Replay the current Pixelblaze detector logic offline against the captured export stream using:
   - `tools/kick_detector/replay_pixelblaze_capture.py`
5. Compare:
   - frozen Python excerpt baseline
   - real Pixelblaze exported values
   - replayed Pixelblaze detector decisions
   - logged Pixelblaze detector decisions
6. Use that comparison to recalibrate the Pixelblaze-side feature scaling and detector gating before further live tuning

Important implementation note:

- Pixelblaze detector logic is currently quantized to a fixed `50 ms` detector tick for calibration
- `dbgAccepted` is latched for one full detector tick
- this makes exported captures and offline replay meaningfully comparable

### Current Working Method

At this stage, detector experimentation should happen in this order:

1. Keep a stable Pixelblaze debug pattern for data collection
2. Capture one known excerpt from hardware
3. Trim / align the capture in replay
4. Compare:
   - ideal frozen Python baseline
   - logged Pixelblaze behavior
   - replayed detector behavior
5. Try detector changes in replay first
6. Only port a replay change back to Pixelblaze after it shows a clear improvement

This is now preferred over editing the live Pixelblaze pattern for every detector idea.

### Current Pixelblaze Detector State

The current Pixelblaze debug/live detector uses:

- detector tick quantized to `50 ms`
- `sub = bins 0..2`
- `core = bins 1..6`
- `body = bins 7..11`
- neutral mids `12..20` ignored
- `contamination = bins 21..25`
- peak picking and refractory retained
- slow baseline averages for:
  - `sub`
  - `core`
  - `support`
- over-average gating for:
  - `sub`
  - `core`
  - `support`

Recently tried and reverted:

- `supportRawRatio`
  - intent: require short-term support growth to reject bassy sustained body sounds
  - outcome: reduced some pre-drop false positives, but collapsed post-drop recall
  - status: reverted from both `main-beat-debug.pe` and `main-beat-flash.pe`

### Current Status Summary

What is working:

- capture and replay workflow is functioning
- active-window trimming / alignment is available in replay
- accepted-event logging is reliable enough for comparison
- revised band grouping improved over the original broad low/body/high split

What is not solved yet:

- the Monolink pre-drop false-trigger cluster is reduced but not eliminated
- stricter short-term growth gates can suppress false triggers, but currently also suppress too many valid post-drop kicks

Current recommendation:

- stop iterating detector ideas directly on the live pattern
- use captured Pixelblaze exports as the main experiment input
- evaluate new candidate rules in replay first
- only promote clear wins back to Pixelblaze

### Hardware Calibration Reference Set

The current hardware-side reference set for replay-first detector evaluation is:

1. `Monolink - Return To Oz - 04m35s-05m05s`
   - role:
     - hard transition / pre-drop false-trigger case
   - what it tests:
     - stay quiet during break / riser
     - react to the main beat after the drop
     - avoid double / extra triggers after the drop

2. `Becoming Insane - 03m45s-04m15s`
   - role:
     - transition into a real bassy beat
   - what it tests:
     - avoid triggering through noisy / textured lead-in
     - begin triggering when the real beat arrives

3. `Kick Drum BPM 100 - 30s`
   - role:
     - clean kick sanity baseline
   - what it tests:
     - do not make the detector so strict that obvious isolated kicks are missed

Current important observation:

- on the current live/debug detector, `Kick Drum BPM 100 - 30s` produced:
  - `logged_accepted_count = 0`
  - `replay_accepted_count = 0`
- this means the current Pixelblaze gate is too strict for the easy baseline
- this sample should be treated as a mandatory regression guard for future replay-side detector experiments

Current evaluation rule for replay-side detector variants:

- improve the hard Monolink false-trigger case
- preserve or improve Becoming Insane beat-entry behavior
- recover the clean Kick Drum baseline
- only detector variants that satisfy all three should be considered for promotion back into Pixelblaze

### Why This Step Is Needed

- the offline simulator and real Pixelblaze `frequencyData` behavior are not numerically equivalent
- real-time rolling normalization on Pixelblaze drifts differently during breaks, risers, and drops
- direct detector porting without this calibration led to:
  - false triggers during breaks and pre-drop sections
  - overreaction after drops
  - behavior that diverged from the Python evaluation

### Success Criteria

- captured Pixelblaze logs can be replayed offline in Python
- the replayed data explains the observed divergence between the simulator and on-device behavior
- the offline model is updated so further tuning is driven by real Pixelblaze-like inputs instead of guesswork

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

## Current Status

- Python detector exploration is complete enough to freeze a reference detector for Pixelblaze porting
- current frozen Python reference:
  - `onset_plus_ratio_peak_picked_low_qualified`
- next phase:
  - capture real Pixelblaze sensor and detector data from the hat
  - replay that data in Python to calibrate the offline model against actual Pixelblaze behavior
  - then simplify the calibrated reference detector into a Pixelblaze-portable form

## Evaluation Notes

### Howling - 00m15s to 00m45s

- `0s` to about `15s` in the excerpt:
  - main kicks are clear and isolated
  - all four Phase 1 detectors behave well
- about `18s` to `30s` in the excerpt:
  - additional rhythmic and transient content appears between the main kicks
  - current detectors begin firing between the main beat pulses

Current requirement clarified from this test:

- the target is not generic percussive detection
- the detector should prefer the main beat only and suppress intermediate rhythmic events where possible

### Howling - 02m30s to 03m00s

- this is a denser, harder real-music test with competing rhythmic material across many bands
- `low_band_threshold` and `low_band_rising_edge` are clearly too chatty here
- the meaningful comparison is between:
  - `bass_vs_high_ratio`
  - `onset_plus_ratio`

Observed tradeoff:

- `bass_vs_high_ratio`
  - better recall
  - still fires on some intermediate events between the strongest beat pulses
- `onset_plus_ratio`
  - better precision
  - is closer to main-beat-only behavior in this window
  - may miss some valid kicks because it is stricter

Current takeaway from this test:

- if the target is main-beat-only response, `onset_plus_ratio` is the stronger Phase 1 candidate in this window
- the likely next step is not to use it unchanged, but to start from it and tune for fewer missed valid kicks

### Howling - 04m00s to 04m30s

- this excerpt is primarily a transition and interlude test
- about `0s` to `3.5s`:
  - regular kick section
  - all detectors behave reasonably
- about `3.5s` to `11s`:
  - low-activity / interlude region
  - detectors mostly stop firing, which is the desired behavior
- after about `11s`:
  - beat returns
  - looser detectors begin firing more densely again
  - `onset_plus_ratio` remains the sparsest and closest to main-beat-only behavior

Current takeaway from this test:

- silence and interlude handling are acceptable in the current Phase 1 pipeline
- the main unresolved problem is still main-beat-only selectivity once denser rhythmic content returns

### Monolink - 00m00s to 00m30s

- this is a clean baseline window with a regular repeating kick structure from the start
- the low-frequency kick columns are clear in the heatmap
- feature traces are stable and periodic
- all four detectors align closely and behave acceptably

Current takeaway from this test:

- this window is useful as a sanity check and baseline
- it does not meaningfully differentiate detector quality because the section is too easy

### Monolink - 01m00s to 01m30s

- this window adds a softer lead-in before the beat is fully established
- about `0s` to `2s`:
  - lower-energy opening
  - detectors mostly stay quiet until the beat becomes clear
- after about `2s`:
  - regular kick structure is established
  - all four detectors align closely again

Current takeaway from this test:

- startup and beat-entry behavior are acceptable in this section
- like the previous Monolink baseline window, this excerpt is still too easy to strongly differentiate the detector variants

### Monolink - 02m00s to 02m30s

- the main beat is present through most of the excerpt, but appears to stop around `23s`
- after about `23s`:
  - the low-frequency kick columns largely disappear
  - remaining activity appears to be lighter rhythmic material such as hats or higher-frequency texture

Observed implication:

- detectors should largely stop firing once the main bassy beat disappears
- continued triggering in that tail region should be treated as false positive behavior relative to the project goal

Current takeaway from this test:

- `low_band_threshold` and `low_band_rising_edge` are too permissive in the later part of the window
- stronger bass-dominance filtering appears valuable here because it helps suppress non-kick rhythmic activity after the main beat ends

### Monolink - 04m35s to 05m05s

- this excerpt is a strong transition test with:
  - isolated bursty transients near the beginning
  - a long riser / build section
  - a clear main beat return around `23s`

Observed behavior:

- during the long riser, detectors mostly stay quiet, which is desirable
- when the main beat returns, detectors begin firing again, which is also desirable
- `onset_plus_ratio` produces an early trigger on an isolated transient burst near the start of the excerpt

Current takeaway from this test:

- `onset_plus_ratio` is not universally best
- it helps in denser beat sections, but can still be fooled by strong isolated transients that are not the main beat
- the likely final detector will need:
  - some onset-based selectivity
  - plus stronger qualification that favors the main beat over isolated burst events

### Monolink - 04m35s to 05m05s Frozen Python Baseline

For the frozen Python detector:

- `onset_plus_ratio_peak_picked_low_qualified`

Expected behavior on this excerpt is:

- no accepted flashes before about `23.15s`
- `15` accepted flashes from about `23.15s` to `29.93s`
- average spacing is about `0.485s`, which is about `124 BPM`

Accepted hit times:

- `23.150`
- `23.638`
- `24.126`
- `24.613`
- `25.101`
- `25.588`
- `26.122`
- `26.540`
- `27.028`
- `27.516`
- `28.003`
- `28.491`
- `28.955`
- `29.443`
- `29.931`

This excerpt is the current reference check for Pixelblaze calibration:

- break / riser should stay quiet
- main beat return should trigger once per dominant beat
- post-drop double-triggering should not occur

## Phase 2 Detector Directions

Phase 1 clarified that the target is not generic percussive detection. The detector should prefer the main beat only.

### Target Behavior

- react to the main bassy beat
- suppress intermediate rhythmic clutter between main kicks
- stay quiet during interludes and risers
- avoid isolated transient bursts that are not part of the main beat pattern

### What Phase 1 Ruled Out

- `low_band_threshold`
  - too permissive in denser sections
- `low_band_rising_edge`
  - still too permissive once rhythmic clutter appears
- raw `bass_vs_high_ratio`
  - useful when the main beat disappears
  - but can become too strict and miss valid kicks in some sections
- raw `onset_plus_ratio`
  - strongest overall Phase 1 candidate in dense beat sections
  - but can still false-trigger on isolated transient bursts

### Phase 2 Candidates To Try

1. `onset_plus_ratio + local peak picking`

- start from `onset_plus_ratio`
- require the trigger to be the strongest candidate within a short local window
- intended effect:
  - keep the dominant beat hit
  - suppress intermediate smaller events between kicks

2. `onset_plus_ratio + stronger low-band qualification`

- start from `onset_plus_ratio`
- add a stricter minimum on low-band or low-plus-body energy
- intended effect:
  - reduce false triggers on isolated bright transients
  - keep onset information for dense rhythmic sections

3. `bass_vs_high_ratio + onset rescue`

- start from `bass_vs_high_ratio`
- add a secondary onset condition so flatter but valid kicks are not rejected as easily
- intended effect:
  - preserve the useful bass-dominance filter when the main beat disappears
  - recover some missed valid kicks in mixed sections

4. `main-beat spacing filter`

- apply a short competition window or adaptive minimum spacing after candidate detection
- keep only the strongest event in each local beat-sized neighborhood
- intended effect:
  - enforce main-beat preference
  - reduce between-beat clutter without relying entirely on raw thresholds

### Recommended Phase 2 Order

1. try `onset_plus_ratio + local peak picking`
2. if isolated transient false positives remain, add stronger low-band qualification
3. if valid kicks are still missed when bass dominance weakens, test `bass_vs_high_ratio + onset rescue`
4. only then add a main-beat spacing filter if needed

## Phase 2 Trial Notes

### onset_plus_ratio_peak_picked

Implemented as:

- start from `onset_plus_ratio`
- compute a local score based on onset strength, low/body energy, and bass dominance
- keep only the strongest candidate inside a short local neighborhood before applying the refractory interval

Observed behavior on the reviewed excerpts:

- `Howling - 00m15s to 00m45s`
  - trigger count dropped from `79` to `63`
  - this reduced some between-beat clutter
- `Howling - 02m30s to 03m00s`
  - trigger count stayed at `64`
  - timing shifted slightly but the detector remained much sparser than the simpler baselines
- `Howling - 04m00s to 04m30s`
  - minor reduction from `48` to `47`
- `Monolink - 00m00s to 00m30s`
  - no meaningful change on the easy baseline
- `Monolink - 01m00s to 01m30s`
  - no meaningful change on the easy baseline
- `Monolink - 02m00s to 02m30s`
  - no meaningful change on the main-beat-stop test
- `Monolink - 04m35s to 05m05s`
  - reduced beat-return clutter from `18` to `16`
  - but still preserved the early isolated-transient false trigger near the start of the excerpt

Current takeaway:

- local peak picking is directionally useful
- it improves main-beat preference in some denser sections without harming the easy baseline windows
- it is not sufficient by itself because isolated transient false positives can still survive if they dominate their local neighborhood
- the next Phase 2 refinement should be stronger low-band qualification on top of the peak-picked detector

### onset_plus_ratio_peak_picked_low_qualified

Implemented as:

- start from `onset_plus_ratio_peak_picked`
- require stronger low-band or combined low-plus-body energy before a peak-picked candidate is allowed through

Observed behavior on the key review excerpts:

- `Howling - 00m15s to 00m45s`
  - no meaningful change versus `onset_plus_ratio_peak_picked`
  - retained the useful reduction in between-beat clutter
- `Howling - 02m30s to 03m00s`
  - trigger count dropped from `64` to `63`
  - removed one early trigger while preserving the sparse main-beat-oriented pattern
- `Monolink - 04m35s to 05m05s`
  - removed the early isolated-transient false trigger entirely
  - reduced count from `16` to `15`
  - aligned closely with the clean beat-return spacing

Current takeaway:

- this is the strongest detector variant tried so far
- it preserves the useful behavior of peak picking in dense sections
- it improves the isolated-transient failure case seen in the Monolink transition window
- this should be treated as the current leading candidate for the next round of evaluation

## Additional Track Notes

### Becoming Insane - 05m15s to 05m45s

- about `0s` to `6s` in the excerpt:
  - main bassy kick is present
- after about `6s`:
  - the main bass kick stops
  - a faster, less-bassy psy-style kick remains
  - this later activity should not be considered the target trigger behavior for this project

Current takeaway from this test:

- sparse detector behavior after `6s` is desirable in this excerpt
- suppression of the later faster, less-bassy activity should be treated as a success rather than a miss
- `onset_plus_ratio_peak_picked_low_qualified` performs well on this requirement

### Becoming Insane - 03m45s to 04m15s

- about `0s` to `16s` in the excerpt:
  - mostly noisy or textured material without a stable bass-kick train
  - only occasional isolated stronger events appear
- about `16.5s` to `28s`:
  - a clear regular main bass beat arrives
  - low-band kick columns become strong and periodic

Current takeaway from this test:

- low detector activity before the regular bass beat arrives is desirable
- triggering should primarily start once the later regular main beat section begins
- `onset_plus_ratio_peak_picked_low_qualified` matches this behavior well

### Becoming Insane - 05m55s to 06m25s

- about `0s` to `5.5s` in the excerpt:
  - dense upper and mid-frequency texture is present
  - the clean main bass-kick train is not yet fully established
- after about `6s`:
  - a strong regular main bass beat appears and continues
  - low-band kick columns become clearly periodic

Current takeaway from this test:

- peak picking provides the main improvement here by cutting raw onset-based clutter substantially
- stronger low qualification does not materially change this window, which is acceptable because the later beat is already strongly bass-supported
- `onset_plus_ratio_peak_picked_low_qualified` behaves well in the established main-beat section

### Pria - 04m00s to 04m30s

- about `10s` to `17s` in the excerpt:
  - beat is present, but the section is lighter and less cleanly bass-dominant
  - there is substantial mid and high-frequency clutter between beat pulses
- after about `17s`:
  - the main bass beat becomes stronger and more clearly established

Current takeaway from this test:

- raw detectors are too chatty in the presence of between-beat clutter
- peak picking provides the main improvement by bringing trigger spacing much closer to the dominant beat
- stronger low qualification does not materially change this window, but it does not hurt the result

### Pria - 00m25s to 00m55s

- this is a stable beat-driven section with a strong repeating low-band pulse throughout
- substantial rhythmic clutter remains present between the main beat pulses

Current takeaway from this test:

- raw detectors are far too dense for a main-beat-only goal
- peak picking provides the key improvement by reducing trigger density toward the dominant pulse train
- stronger low qualification is neutral here, which is acceptable

### Moderat - Bad Kingdom - 00m30s to 01m00s

- this excerpt contains a repeating low-end pulse, but the target beat is weaker and flatter than the heavier techno and psy examples
- the mix contains substantial mid and high-frequency structure around the beat

Current takeaway from this test:

- this is a useful weak/flatter-beat case
- simple low-band and ratio-based detectors are too dense
- the peak-picked onset family still produces a plausible sparse pulse train
- stronger low qualification is neutral in this excerpt, which is acceptable

### The Chemical Brothers - Galvanize - 02m15s to 02m45s

- about `0s` to `15s` in the excerpt:
  - broken, sparse, or irregular rhythmic structure
  - only occasional isolated low events are present
- after about `15s`:
  - a more regular low-end pulse emerges
  - substantial upper and mid-frequency rhythmic content is still present

Current takeaway from this test:

- this is a useful off-grid / irregular-structure case
- the leading detector stays relatively restrained in the early broken section
- it becomes more active once a stronger recurring beat-like structure appears
- this is acceptable behavior for the project goal

### Moderat - A New Error - 02m45s to 03m15s

- about `0s` to `8s` in the excerpt:
  - dense beat-driven material with a repeating low-end pulse and substantial surrounding structure
- about `8s` to `12.5s`:
  - clear breakdown / low-activity gap
  - low-band activity drops out strongly
- after about `12.5s`:
  - beat returns and stays strong
  - upper and mid-frequency clutter remains present around the beat

Current takeaway from this test:

- this is a strong breakdown and beat-reentry case
- raw detectors are too dense in the active sections
- the leading detector stays mostly quiet during the breakdown and re-acquires cleanly after the beat returns
- this is another positive result for `onset_plus_ratio_peak_picked_low_qualified`

### Astrix - Deep Jungle Walk - 02m00s to 02m30s

- about `0s` to `7s` in the excerpt:
  - transitional or sparse opening with noisy upper-frequency content and isolated events
  - no stable target bass-kick train is established yet
- after about `7s`:
  - a strong, fast, regular bass-driven pulse appears
  - low-band activity becomes clearly periodic

Current takeaway from this test:

- this is a useful fast-psy coverage case
- raw detectors over-trigger heavily once the rolling section starts
- peak picking provides the critical improvement by reducing the raw onset clutter to a cleaner regular pulse train
- stronger low qualification is neutral here, which is acceptable

### Astrix - Deep Jungle Walk - 07m00s to 07m30s

- about `0s` to `6.5s` in the excerpt:
  - noisy intro with strong upper-frequency content
  - no stable low-band target pulse yet
- about `6.5s` to `18.5s`:
  - strong fast rolling bass-driven pulse is clearly established
- about `18.5s` to `20s`:
  - short break where the low-band pulse drops out
- after about `20s`:
  - the rolling pulse returns strongly

Current takeaway from this test:

- this is a valuable combined fast-psy, break, and beat-reentry case
- the leading detector stays relatively restrained in the intro
- it tracks the established rolling pulse well
- it goes quiet through the short break and re-acquires cleanly when the beat returns

## Test Matrix

The matrix below tracks what detector behaviors are already covered by the current curated excerpt set and where more examples would still be useful.

| Test Goal | What Good Behavior Looks Like | Current Coverage | Current Example(s) | Notes / Gaps |
| --- | --- | --- | --- | --- |
| Clean main kick baseline | Fires reliably on obvious bassy kick | Strong | `Kick Drum _ BPM 100 - 30s`, `Monolink 00m00s-00m30s`, `Monolink 01m00s-01m30s` | Baseline is well covered |
| Beat entry after softer opening | Stays mostly quiet, then locks onto beat when it arrives | Strong | `Monolink 01m00s-01m30s`, `Becoming Insane 03m45s-04m15s` | Covered |
| Dense beat plus between-beat clutter | Favors dominant beat and suppresses intermediate rhythmic events | Strong | `Howling 00m15s-00m45s`, `Howling 02m30s-03m00s`, `Pria 04m00s-04m30s`, `Pria 00m25s-00m55s` | One of the best-covered categories |
| Main beat disappears but lighter rhythmic content continues | Stops triggering once the target bassy beat is gone | Strong | `Monolink 02m00s-02m30s`, `Becoming Insane 05m15s-05m45s` | Covered and very important for project goal |
| Long riser / build with no true kick train | Stays quiet through build, resumes on beat return | Strong | `Monolink 04m35s-05m05s`, `Howling 04m00s-04m30s` | Covered |
| Isolated transient bursts that are not the main beat | Rejects isolated non-beat transient events | Medium | `Monolink 04m35s-05m05s`, `Becoming Insane 03m45s-04m15s` | Covered enough to expose one key false-trigger case, but more examples would help |
| Strong regular beat in dense psy / fast material | Keeps main pulse without exploding into over-triggering | Medium | `Becoming Insane 05m55s-06m25s`, `Pria 00m25s-00m55s` | More fast psy / hi-tech examples would still help |
| Weak or flatter kick with less bass emphasis | Still catches valid target beat if it is meant to count | Weak | Partial coverage only from some `Howling` and `Pria` sections | Needs more deliberate examples |
| Off-grid percussion / non-4-on-the-floor rhythmic material | Avoids following non-target rhythmic structure | Weak | No strong dedicated example yet | Good gap to fill |
| Sparse cinematic or industrial hits | Avoids triggering on isolated booms / impacts that are not beat-driving kicks | Weak | Only partially covered by transition windows | Good gap to fill |

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
