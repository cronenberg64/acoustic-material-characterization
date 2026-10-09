# CAD

| Folder | Contents |
|---|---|
| `rig/structure/` | `base_board`, `tier_a_foundation`, `tier_b_spring_bay` (PLA) |
| `rig/electronics/` | `tier_c_deck` (PLA), `tier_d_lid` (PETG) |
| `rig/solenoid_fit/` | `tile_bottom_x4`, `tile_top_x4` (PLA); `filler_22_x2_TPU`, `filler_44_x1_TPU` (TPU) |
| `rig/assembly/` | `tower_v5_assembly.step` |
| `specimens/` | `sample_100x20x8`, `bend_jig` |
| `strikers/` | `striker_cap_14/16/18mm`, `striker_caps` |
| `docs/` | solenoid specs, design sketch, renders |
| `src/` | `generate_tower_v5.py` regenerates everything in `rig/` |

Filename suffix `_xN` = how many to print. Tiles: any split of 4 tiles between bottom and top sets the tap gap (2 + 2 = nominal 15.44 mm).

Print order: `base_board`, `tier_a_foundation`, tiles + fillers, `tier_b_spring_bay`, `tier_c_deck`, `tier_d_lid`.
Do not fire the solenoid until `tier_b_spring_bay` is bolted on.

Regenerate: `uv run python cad/src/generate_tower_v5.py`
