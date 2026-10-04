# Action Block Routing & Verification Report

The fixed 32 × 32 mm, two-layer, 1.6 mm Action Block board is routed with 37 track segments and zero added vias. All component footprint positions, rotations, pad positions, net assignments, and Edge.Cuts geometry were verified and preserved.

| Net | Width | Layer | Segments | Endpoints |
| :--- | :--- | :--- | :---: | :--- |
| `/RX_IN` | 0.30 mm | `B.Cu` | 4 | `IN` Pin 3 $(83.5, 73.77) \to$ `MCU` Pin 8 $(88.76, 67.62)$ |
| `/TX_OUT` | 0.30 mm | `B.Cu` | 6 | `MCU` Pin 9 $(88.76, 65.08) \to$ `OUT` Pin 3 $(109.5, 73.77)$ |
| `/LED_DIN` | 0.30 mm | `F.Cu` | 3 | `RGB` Pin 3 $(84.0, 65.04) \to$ `MCU` Pin 6 $(88.76, 72.70)$ |
| `/SWIO` | 0.30 mm | `F.Cu` | 3 | `MCU` Pin 16 $(104.0, 75.24) \to$ `PROG` Pin 3 $(109.5, 86.50)$ |
| `/RETURN_BUS` | 0.40 mm | `B.Cu` | 7 | `IN` Pin 4 $(83.5, 76.31) \to$ `OUT` Pin 4 $(109.5, 76.31)$ |
| `+3V3` | 0.60 mm | `F.Cu`, `B.Cu` | 14 | Interconnects all 7 power pads (`IN`, `OUT`, `RGB`, `MCU` 10 & 21, `C104`, `PROG`) |

GND zones cover $(80.50, 56.50)\text{ mm}$ through $(112.50, 88.50)\text{ mm}$ on both copper layers. They were filled with `pcbnew.ZONE_FILLER`, using 0.25 mm clearance, 0.30 mm thermal gaps, 0.40 mm thermal spokes, and automatic removal of isolated islands. The standard 0.50 mm copper-to-edge rule remains in force. All seven GND pads connect with thermal reliefs on both layers.

## Return Bus Routing

A straight line across the board would short MCU through-hole pads 4 and 15 at $Y = 77.78\text{ mm}$. Furthermore, the 2.54 mm pitch and 1.80 mm pad diameter leave only 0.74 mm between adjacent pins, which cannot accommodate a 0.40 mm trace with 0.20 mm clearance on each side.

`/RETURN_BUS` therefore detours below the MCU across $Y = 87.25\text{ mm}$ with 45-degree corners. This leaves $1.05\text{ mm}$ clearance to the bottom board edge while preserving complete signal integrity.

## DRC Verification

Command:
```sh
kicad-cli pcb drc --all-track-errors --severity-all -o hardware/action_block/reports/routing_drc.rpt hardware/action_block/action_block.kicad_pcb
```

Final result:
* **Unconnected items: 0**
* **DRC errors: 0**
* **Copper clearance violations: 0**
* **Silkscreen warnings: 39** (31 text height $0.70\text{ mm}$ vs $0.80\text{ mm}$ default, 6 silkscreen outline overlaps, 2 edge-clipped outline graphics).

## Deliverables

- `action_block.kicad_pcb`: saved routes and filled zones.
- `reports/routing_drc.rpt`: full final DRC report.
- `pcb_preview/action_block_routed.svg`: composite copper, silkscreen, and outline vector preview.
- `pcb_preview/action_block_top.png`: 3D top render.
- `pcb_preview/action_block_bottom.png`: 3D bottom render.
- `robosen_action_block_gerbers.zip`: production Gerber package.
- `route_pcb.py`: routing source script, runnable with KiCad Python.
