# Project Progression & Action Checklist
**Project:** Acoustic Material Characterization (GR1 Research)  
**Status:** In Progress — Physical Fabrication & Setup  
**Last Updated:** 2026-10-02  

---

## Phase 1: 3D Printing & Physical Rig Fabrication
- [x] **Base Fixture & Bend Jig (Completed):**
  - [x] `cad/base_plate.stl` (Printed & Ready ✓)
  - [x] `cad/bend_jig.stl` (Printed & Ready ✓)
- [x] **Solenoid Carriage & Mount (Completed):**
  - [x] `cad/solenoid_carriage_pivot_carriage.stl` (Printed ✓)
  - [x] `cad/solenoid_carriage_pivot_plate.stl` (Printed ✓)
  - [x] Striker cap printed and fitted onto plunger pin ✓
- [ ] **Next Print Plate (Specimen Beams):**
  - [ ] `cad/sample_100x20x8.stl` (Start PLA 100% infill beam now)
- [ ] **Hardware Gathering & Solenoid Prep:**
  - [x] Measure solenoid plunger protrusion & pin diameter (Extended: 11.94 mm, Dia: 3.0 mm) ✓
  - [x] Generated slip-on striker caps (14 mm, 16 mm, 18 mm) ✓
  - [ ] Pick up M3 brass heat-set inserts (out for delivery at apartment)
  - [ ] Gather 4x M3 screws (8–10 mm) for mounting solenoid onto pivot plate
  - [ ] Gather 2x M3 screws (14–16 mm) + 2 washers + 2 nuts for arc slot clamp
  - [ ] Gather 4x M3 screws (10–14 mm) for carriage feet mounting to base plate
  - [ ] Check 2020 extrusion slot width (5 mm vs 6 mm) for T-nuts
  - [ ] Procure PETG filament spool (covers intermediate stiffness between PLA and TPU)

---

## Phase 2: Electronics & Firmware Bench Validation
- [x] **Solenoid Driver Circuit (Verified ✓):**
  - [x] Wire 12V DC power supply into Freenove breakout board barrel jack
  - [x] Route regulated power & GND to IRF520 MOSFET module
  - [x] Wire solenoid to MOSFET load terminals
  - [x] Connect ESP32 D4 (GPIO 4) to MOSFET SIG and common GND
- [x] **ESP32 Firmware (Flashed & Tested ✓):**
  - [x] PlatformIO setup in `.venv` via `uv pip install platformio`
  - [x] Patch firmware for non-blocking HX711 checks
  - [x] Flash firmware: `uv run pio run -d firmware/esp32_tapper -t upload --upload-port /dev/cu.usbserial-10`
  - [x] Verify bench pulses: TAP 1 (5000 µs), TAP 2 (10000 µs), TAP 3 (15000 µs) fired with 100% success ✓

---

## Phase 3: Specimen Fabrication & Ground-Truth Measurement
- [ ] **Fabricate Test Beams (100 x 20 x 8 mm):**
  - [ ] PLA specimens (100%, 70%, 50%, 30%, 15% infill)
  - [ ] PETG specimens (100%, 70%, 50%, 30%, 15% infill)
  - [ ] TPU specimens (flexible material regime)
- [ ] **Density & Dimension Verification:**
  - [ ] Measure exact L, b, h with digital caliper (±0.05 mm)
  - [ ] Weigh each beam on digital scale (±0.01 g) to calculate true density rho
- [ ] **3-Point Bend Static Test (Mechanical Ground Truth):**
  - [ ] Place beam on `bend_jig` fulcrums (span L_s = 80 mm)
  - [ ] Apply step loads with load cell / weights and measure deflection delta
  - [ ] Run `src/ame/analysis/ground_truth.py` to extract Young's modulus E

---

## Phase 4: Acoustic Data Acquisition (DAQ) & Calibration
- [ ] **Rig Assembly:**
  - [ ] Bolt base plate to 2020 aluminum extrusion rails
  - [ ] Mount solenoid carriage on base plate at position 1 (X = 0 mm)
  - [ ] Place specimen on nodal support ridges (X = ±27.6 mm)
  - [ ] Attach acoustic sensor (piezo / contact microphone / Analog Discovery 3)
- [ ] **Strike Angle & Position Calibration:**
  - [ ] Test normal impact (0 deg) at 3 span positions (X = 0, 22, 44 mm)
  - [ ] Test shear impact (-15 deg and +15 deg) using indexed detents
  - [ ] Verify acoustic waveform SNR and strike repeatability via `src/ame/daq/acquire.py`

---

## Phase 5: Machine Learning & Scientific Evaluation
- [ ] Extract modal frequencies (f1, f2, f3) and acoustic damping (zeta)
- [ ] Train regression models (KNN, Random Forest, Ridge) via `src/ame/models/run_all.py`
- [ ] Cross-validate predicted stiffness (E) and density (rho) against ground truth
- [ ] Produce comparative figures and tables for final GR1 publication report
