# Project Progression & Action Checklist
**Project:** Acoustic Material Characterization (GR1 Research)  
**Status:** In Progress — Solenoid Mount Redesign & Physical Fabrication  
**Last Updated:** 2026-10-09  
**Progress:** 28 / 78 tasks completed (35.9%)

---

## Schedule & Milestones
| By | Milestone |
|---|---|
| Oct 20 | Rig assembled, Gate G1 passed, remaining PLA/TPU bars printed |
| Nov 3 | All bars weighed, measured, bend-tested (ground truth). Pilot sample through full pipeline (G2) |
| Nov 24 | Full 2,700-tap data collection done |
| Dec 15 | RQ1–RQ3 analysis and figures done |
| Jan 8 | Full draft to Prof. Liu |
| Jan 22 | Revisions done, submitted or submit-ready |

*Note: ROBOMECH's deadline is expected around early February (pattern-based, unconfirmed) and IROS 2027's is March 1, both near the February trip, so the effective deadline is before departure.*

---

## Phase 1: 3D Printing & Physical Rig Fabrication
- [x] **Base Fixture & Bend Jig (Completed):**
  - [x] `cad/base_plate.stl` (old plate, retired; replaced by `cad/rig/structure/base_board.stl`)
  - [x] `cad/specimens/bend_jig.stl` (Printed & Ready ✓)
  - [x] M3 brass heat-set inserts installed in base plate (All 12 holes flush ✓)
- [ ] **Solenoid Carriage & Mount (Redesign Overhaul in Progress):**
  - [x] Retired legacy 2-piece design (32 mm legs starved screw threads, trapped nuts, blocked rear holes)
  - [x] Retired Carriage v4 (`cad/solenoid_carriage_v4.stl` — toppling solenoid, difficult fastener access)
  - [ ] **New Carriage Redesign**:
    - [ ] Review user's sketches and design overhaul inputs
    - [ ] Incorporate physical resting cradle / ledge so solenoid cannot topple during assembly
    - [ ] Solve solenoid clamping / fastening (accessible screws/clamp, zero coil puncture risk)
    - [ ] Maintain open line-of-sight counterbores for base plate M3×12 mm screws into brass inserts
    - [ ] Maintain positive air gap (~15.4 mm rest gap, 17.4 mm stroke)
    - [ ] Generate parametric CadQuery script, STL, STEP, and test suite
    - [ ] 3D print the new carriage
- [x] **Striker Caps & Solenoid Hardware Prep:**
  - [x] Ground-truth digital caliper measurements verified:
    - Total rod: 86.87 mm | Body: 51.09 mm | Body width: 24.15 mm | Depth: 30.79 mm
    - Spring at rest: 29.12 mm | Spring compressed: 11.94 mm | Pin dia: 3.0 mm
    - Stroke: 17.18–17.44 mm | Rest reach (16mm cap): 26.11 mm | Energized reach: 43.55 mm
  - [x] 16 mm Striker cap printed and fitted onto plunger pin ✓
  - [x] Hardware gathered strictly from Kinzomoor 500-pc kit (`[6, 8, 12, 16, 20] mm` SHCS + M3 flat washers + M3 nuts)
  - [ ] Check 2020 extrusion slot width (5 mm vs 6 mm) for T-nuts
  - [ ] Decide strike tip: steel ball glued into the cap vs printed dome
- [ ] **Specimen Beams Print Status:**
  - [x] PLA 100% bar printed (`cad/specimens/sample_100x20x8.stl` ✓)
  - [x] TPU 60% bar printed ✓
  - [ ] Print remaining PLA bars (80%, 60% ×3 as PLA-60 / -R1 / -R2, 40%, 20%)
  - [ ] Print TPU-100
  - [ ] Procure PETG filament spool (covers intermediate stiffness between PLA and TPU)
  - [ ] Print PETG specimen batch (after filament arrives: 20%, 40%, 60%, 80%, 100%)

---

## Phase 2: Electronics & Firmware Bench Validation
- [x] **Solenoid Driver Circuit (Verified ✓):**
  - [x] Wire 12V DC power supply into Freenove breakout board barrel jack
  - [x] Route regulated power & GND to IRF520 MOSFET module
  - [x] Wire solenoid to MOSFET load terminals
  - [x] Connect ESP32 D4 (GPIO 4) to MOSFET SIG and common GND
  *(Note: "Verified ✓" confirms the solenoid fires, not that force is repeatable; repeatability is measured in the 50-tap test)*
- [x] **ESP32 Firmware (Flashed & Tested ✓):**
  - [x] PlatformIO setup in `.venv`
  - [x] Patch firmware for non-blocking HX711 checks
  - [x] Flash firmware: `uv run pio run -d firmware/esp32_tapper -t upload --upload-port /dev/cu.usbserial-10`
  - [x] Verify bench pulses: TAP 1 (5000 µs), TAP 2 (10000 µs), TAP 3 (15000 µs) fired with 100% success ✓
- [ ] **Wiring & Repeatability Checks:**
  - [ ] Wiring check: solenoid current path bypasses breadboard and ESP32 board, ≥22 AWG
  - [ ] Tap repeatability test: 50 taps at fixed pulse width, check peak amplitude stability and MOSFET temp (Gate G1)
  - [ ] CONDITIONAL (if amplitude spread >~10%): Swap for D4184 logic-level MOSFET module or add buffer capacitor

---

## Phase 3: Specimen Fabrication & Ground-Truth Measurement
- [ ] **Measure Specimen Beams (100 x 20 x 8 mm):**
  - [ ] Measure exact L, b, h with digital caliper (±0.05 mm)
  - [ ] Weigh each beam on digital scale (±0.01 g) to calculate true density rho
- [ ] **3-Point Bend Static Test (Mechanical Ground Truth):**
  - [ ] Place beam on `bend_jig` fulcrums (span L_s = 80 mm)
  - [ ] Apply step loads with weights / load cell and measure deflection delta
  - [ ] Run `src/ame/analysis/ground_truth.py` to extract Young's modulus E

---

## Phase 4: Acoustic Data Acquisition (DAQ) & Calibration
- [ ] **Gates & Pre-Checks:**
  - [ ] Hand-tap pre-check: record the PLA 100% bar on nodal ridges, confirm distinct modal peaks
  - [ ] **Gate G1**: 50 taps, 1 sample, 1 condition, modal peaks stable within a few %
  - [ ] **Gate G2**: pilot sample, full 9-condition grid × 20 reps, through DAQ → features → harness end-to-end
- [ ] **Rig Assembly & Setup:**
  - [ ] Bolt base plate to 2020 aluminum extrusion rails
  - [ ] Mount newly redesigned solenoid carriage on base plate at position 1 (X = 0 mm)
  - [ ] Place specimen on nodal support ridges (X = ±27.6 mm)
  - [ ] Attach acoustic sensor (piezo / contact mic / Analog Discovery 3)
- [ ] **Strike Angle & Position Calibration:**
  - [ ] Test normal impact (0 deg) at 3 span positions (X = 0, 22, 44 mm)
  - [ ] Verify acoustic waveform SNR and strike repeatability via `src/ame/daq/acquire.py`

---

## Phase 5: Machine Learning & Scientific Evaluation
- [ ] Extract modal frequencies (f1, f2, f3) and acoustic damping (zeta)
- [ ] Train regression models (KNN, Random Forest, Ridge) via `src/ame/models/run_all.py`
- [ ] Cross-validate predicted stiffness (E) and density (rho) against ground truth
- [ ] Produce comparative figures and tables for final GR1 publication report

---

## Phase 6: Writing & Submission
- [ ] Full draft to Prof. Liu (target Jan 8)
- [ ] Revisions after review (target Jan 22)
- [ ] Choose venue by fit and confirm its deadline on the official site
- [ ] Submit before the February trip
- [ ] Repo README + scripts that regenerate every figure from raw data

---

## Deferred / Parked
- [ ] ±15° angle tests (RQ2 grid is 3 forces × 3 positions; revisit if time allows)
- [ ] Angle index pin for the pivot mount (the detent holes don't actually lock the angle)
