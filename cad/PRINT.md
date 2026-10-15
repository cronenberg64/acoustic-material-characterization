# Print tracker

Every printable part, its settings and where it stands. Update the **Status** column as parts come off the printer.

Defaults for every part: 0.20 mm layers (keep the normal initial layer height), 0.4 mm nozzle, **no supports**, print in the orientation the STL is saved in. Times are rough estimates; trust the slicer.

Status: **Printing** · **Ready** (current design, OK to print) · **Blocked** (waiting on a measurement) · **Done** (current design printed) · **Old** (printed from an earlier design, needs a reprint)

## Printability rules (every STL here is checked against these)

- No supports anywhere, normal or tree.
- No unsupported span wider than about 10 mm: wider openings get 45° corbels or chamfered tops instead of flat bridges.
- No face hanging in the air above the bed (every part starts flat on the bed).
- Tall, slender pieces are printed lying down and assembled afterwards.
- At least 1.5 mm of plastic around every hole and counterbore.

Exception: the ballast pockets under `base_board.stl` bridge 16 mm. They are hidden under the board, so a little sag there doesn't matter.

## Tower (`rig/`)

| File | Qty | Material | Walls | Infill (gyroid) | Top/bottom | Extra | Time | Status |
|---|---|---|---|---|---|---|---|---|
| `structure/base_board.stl` | 1 | PLA | 5 | 30% | 6 | Outer brim 8–10 mm, bed +5 °C | 8–11 h | Printing (started 2026-10-14) |
| `structure/tier_1_foundation.stl` | 1 | PLA | 5 | 30% | 5 | Brim 5 mm | 12–15 h | Blocked: coil-bulge measurement |
| `structure/tier_2_spring_chamber.stl` | 1 | PLA | 4 | 25% | 5 | | 4–5 h | Blocked: coil-bulge measurement |
| `electronics/tier_3_deck.stl` | 1 | PLA | 3 | 15% | 4 | | 3–4 h | Old (no lid screw bosses), Ready |
| `electronics/tier_4_lid.stl` | 1 | Wood (friend) | – | – | – | 100 × 120 mm panel, 4 × Ø3.4 holes; 1:1 drilling template: `electronics/tier_4_lid_template.svg` (print at 100 %, check the 100 mm scale bar) | – | Old (hook lid broke), Ready for woodwork |
| `solenoid_fit/filler_22_x2_TPU.stl` | 2 | TPU 95A | 4 | 15% | 4 | Hollow tube; ≤30 mm/s, direct feed, dry filament | ~1 h each | Old (solid, too tight), Ready |
| `solenoid_fit/filler_44_x1_TPU.stl` | 1 | TPU 95A | 4 | 15% | 4 | Same as above | ~1.5 h | Old, Ready |
| `solenoid_fit/tile_bottom_x7.stl` | 7 | PLA | 4 | 100% | – | | minutes | 4 printed, 3 more to print |
| `solenoid_fit/tile_top_x7.stl` | 7 | PLA | 4 | 100% | – | | minutes | 4 printed, 3 more to print |

Blocked parts need three numbers before printing: plunger axis to each side of the widest point of the blue coil tape, the widest point in the other direction (≈30.8 mm expected), and cap tip to bar top at rest with 0 tiles (8.44 mm expected).

`base_board.stl` (the one printing) still has two 3 mm grooves where the old tier 1 spigots sat. Tier 1 no longer has spigots, so the grooves are simply unused.

## Clamp (`rig/clamp/`)

| File | Qty | Material | Walls | Infill (gyroid) | Top/bottom | Time | Status |
|---|---|---|---|---|---|---|---|
| `clamp_frame.stl` | 1 | PLA | 5 | 40% | 5 | 2.5–3.5 h | Old (first print sagged under the top beam), Ready |
| `clamp_carriage.stl` | 1 | PLA | 5 | 50% | 5 | ~1 h | Blocked: load cell hole spacing / inset |
| `clamp_hanger.stl` | 1 | PLA | 5 | 50% | 5 | ~0.5 h | Blocked: load cell hole spacing / inset |

## Microphone post (`rig/mic/`)

| File | Qty | Material | Walls | Infill (gyroid) | Top/bottom | Time | Status |
|---|---|---|---|---|---|---|---|
| `mic_post.stl` | 1 | PLA | 4 | 30% | 5 | 0.5–1 h | Sent to friend (2026-10-13) |
| `mic_arm_holder.stl` | 1 | PLA | 4 | 40% | 5 | 0.5 h | Sent to friend (2026-10-13) |

## Suspension stand (`stand/`)

| File | Qty | Material | Walls | Infill (gyroid) | Top/bottom | Time | Status |
|---|---|---|---|---|---|---|---|
| `stand_base.stl` | 1 | PLA | 4 | 30% | 5 | 3–4 h | Ready |
| `stand_post_x2.stl` | 2 | PLA | 4 | 30% | 5 | ~1.5 h each (saved lying flat; print it that way) | Ready |
| `stand_beam.stl` | 1 | PLA | 4 | 100% | 5 | 0.5–1 h | Sent to friend (2026-10-13), still current |

## Specimens and strikers

| File | Qty | Material | Status |
|---|---|---|---|
| `specimens/sample_100x20x8.stl` | per test plan | PLA / TPU / PETG at set infills | See `to-do.md` (PLA 100%, TPU 60% done) |
| `specimens/bend_jig.stl` | 1 | PLA | Done |
| `strikers/striker_cap_16mm.stl` | 1 | PLA | Done (standard cap) |
| `strikers/striker_cap_14mm.stl`, `striker_cap_18mm.stl` | optional | PLA | Not needed unless the gap changes |

## Superseded files sent to the friend

Skip these if not printed yet; the current versions are in the tables above:
- `base_board_v2.stl`: old channel and corner recesses.
- The hook version of `tier_4_lid.stl`.
- `stand_base_posts.stl`: replaced by `stand_base` + `stand_post_x2`.
- The first `clamp_frame.stl`: its beam was a 22.6 mm flat bridge.

## Hardware

| Part | Screws / nuts | In kit? |
|---|---|---|
| Tier 1 → board | 6 × M3×12 + 6 M3 nuts (pockets under the board) | Yes |
| Tier 2 → tier 1 (retainer) | 4 × M3×8 + 4 M3 nuts (pockets in tier 1 top) | Yes |
| Lid → deck | 4 × M3×8 + 4 M3 nuts (pockets in deck corner bosses) | Yes |
| Mic post → board | 2 × M3×12 + 2 M3 nuts (slide in the channels under the board); arm: 1 × M3×12 + nut | Yes |
| Stand posts → base | 2 × M3×16 from below + 2 M3 nuts (slots near the post bottoms) | Yes |
| Stand beam → posts | 2 × M3×16 + 2 M3 nuts; thread clamps: M3 screws + washers | Yes |
| Clamp frame → board | 4 × M4×10 + 4 M4 nuts | **No, buy** |
| Load cell → carriage / hanger | 2 × M4×10, 2 × M4×20 + 2 M4 nuts | **No, buy** |
| Clamp pusher | 1 × M4×25 + 1 M4 nut | **No, buy** |
