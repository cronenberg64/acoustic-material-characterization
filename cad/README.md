# CAD

Current design only. Earlier versions (v4 carriage, v5 tower) are in git history.
What to print, with settings and status: **[PRINT.md](PRINT.md)**.

| Folder | Contents |
|---|---|
| `rig/structure/` | `base_board` (with clamp tab, clamp/mic holes, lower pad), `tier_1_foundation` (tunnel + solenoid chamber), `tier_2_spring_chamber` (retainer plate + spring bay) |
| `rig/electronics/` | `tier_3_deck` (open deck for the breakout + MOSFET), `tier_4_lid` (+ 1:1 SVG drilling template for a wooden lid) |
| `rig/solenoid_fit/` | TPU fillers (set the solenoid position X = 0 / 22 / 44), shim tiles (set the tap gap) |
| `rig/clamp/` | Grip-modulation clamp: frame, carriage, hanger (load cell = moving jaw) |
| `rig/mic/` | Microphone post and arm |
| `rig/assembly/` | `full_assembly.step` (tower parts in place) |
| `stand/` | Thread-suspension stand for free-free reference measurements: base, 2 posts (printed lying down), beam |
| `specimens/` | `sample_100x20x8`, `bend_jig` |
| `strikers/` | Striker caps 14 / 16 / 18 mm (16 mm is the standard) |
| `docs/` | `solenoid_specs.md`, design sketch, `fit_report.md` (assembly simulation), `renders/parts/` (one PNG per STL), `renders/full_rig.png` |
| `src/` | `generate_tower.py` + `generate_clamp_mic_stand.py` (make the STLs), `render_parts.py` (per-part PNGs), `simulate_assembly.py` (assembly + fit check) |

Filename suffix `_xN` = how many to print.
Tiles: bottom tiles + top tiles always total 7 (3.5 mm each). 2 bottom + 5 top = nominal 15.44 mm gap; each tile moved from top to bottom lifts the solenoid and makes the gap 3.5 mm bigger (0 bottom = 8.44 mm, 3 bottom = 18.94 mm, plunger fully extends before reaching the bar).

Do not fire the solenoid until `tier_2_spring_chamber` is screwed onto `tier_1_foundation`.

Regenerate everything: `uv run python cad/src/generate_tower.py`, then `render_parts.py` and `simulate_assembly.py` to re-check.
