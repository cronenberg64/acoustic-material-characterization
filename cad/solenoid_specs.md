# Tapper Actuator Hardware Specifications: CHiFJ FJ-Z05

Logged from physical digital caliper measurements on 2026-10-01 (updated with verified kinematics on 2026-10-07).

| Parameter | Caliper Measurement | Nominal / Spec Sheet |
|:---|:---:|:---:|
| **Model** | `CHiFJ FJ-Z05` | JF-Z05 / FJ-Z05 |
| **Operating Voltage** | `12VDC` | 12V DC |
| **Current Draw** | `2.5A` | 2.5A |
| **Rated Force** | `45N` (~4.5 kg) | 45N |
| **Rated Stroke** | `15 mm` | 15 mm |
| **Total Push Rod Length ($L_{\text{rod}}$)** | **86.87 mm** | ~85–90 mm |
| **Body Frame Length ($L_{\text{body}}$)** | **51.09 mm** | 50.0 mm |
| **Body Width (Narrow)** | **24.15 mm** | 25.0 mm |
| **Body Depth (Wide)** | **30.79 mm** | 30.0 mm |
| **Rear Return Spring at Rest ($L_{\text{rear, rest}}$)** | **29.12 mm** | Plunger retracted |
| **Rear Spring Compressed ($L_{\text{rear, comp}}$)** | **11.94 mm** | Plunger fully extended |
| **Push Pin Diameter** | **3.0 mm** (2.95–3.18 mm measured) | 3.0 mm ground steel rod |
| **Mounting Pitch (M3 Tapped Holes)** | **17.9 mm (across) × 34.5 mm (along body)** | 18.0 mm × 35.0 mm nominal |

---

## Derived Kinematic & Stroke Breakdown

* **Front Pin Protrusion at Rest (unpowered):**
  $$L_{\text{pin, rest}} = L_{\text{rod}} - L_{\text{body}} - L_{\text{rear, rest}} = 86.87 - 51.09 - 29.12 = \mathbf{6.66\text{ mm}}$$
* **Actual Mechanical Stroke:**
  $$\Delta z = L_{\text{rear, rest}} - L_{\text{rear, comp}} = 29.12 - 11.94 = \mathbf{17.18\text{ mm}}$$
* **Front Pin Protrusion at Full Extension:**
  $$L_{\text{pin, ext}} = L_{\text{pin, rest}} + \Delta z = 6.66 + 17.18 = \mathbf{23.84\text{ mm}}$$

*(Note: Earlier bench notes mistook the 11.94 mm compressed rear spring length for the front pin protrusion, leading to negative clearance in the legacy carriage design).*

---

## Striker Cap Reach & Air Gap (16 mm Cap)
* Cap Pin Pocket Depth: **7.40 mm**
* Cap Extension past Pin Tip: **16.60 mm**
* **Total Reach at Rest (from solenoid front face):** $6.66 + 16.60 = \mathbf{23.26\text{ mm}}$
* **Total Reach Extended (from solenoid front face):** $23.84 + 16.60 = \mathbf{40.44\text{ mm}}$
* **Unibody Carriage Nominal Air Gap at Rest:** **3.74 mm** above specimen surface ($Z_{\text{bar}} = 5.5\text{ mm}$)
* **Dynamic Headroom on Impact:** **13.44 mm** (prevents internal bottoming out during strike)

---

### Operational Notes
* **Pulse Duration:** Solenoid draws 2.5A at 12V (~30W peak power). Designed for short impulse strikes (5–15 ms pulse from ESP32 via logic-level MOSFET driver).
* **Return Mechanism:** Spring return plunger.
