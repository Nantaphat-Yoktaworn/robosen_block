# Action Block routing verification

Routed with KiCad 10.0.6 pcbnew using `route_pcb.py --return-detour`.
All footprint positions, rotations, pad positions, and pad net assignments were verified unchanged against the input board. The board remains 32 × 32 mm, two copper layers, 1.6 mm thick.

| Net | Width | Layers | Segments |
| --- | --- | --- | --- |
| /RX_IN | 0.30 mm | B.Cu | 4 |
| /TX_OUT | 0.30 mm | B.Cu | 6 |
| /LED_DIN | 0.30 mm | F.Cu | 3 |
| /SWIO | 0.30 mm | F.Cu | 3 |
| /RETURN_BUS | 0.40 mm | B.Cu | 7 |
| +3V3 | 0.60 mm | F.Cu, B.Cu | 14 |

RETURN_BUS follows the specified eight-point detour at Y = 87.25 mm. All seven +3V3 pads are interconnected. Total: 37 track segments, zero vias (layer transitions use plated through-hole pads).

GND zones cover (80.50, 56.50) through (112.50, 88.50) on F.Cu and B.Cu. Both were filled with pcbnew.ZONE_FILLER and saved. Thermal connections use 0.30 mm gaps and 0.40 mm spokes; zone clearance is 0.25 mm. All seven GND pads are connected.

## DRC

Command: `kicad-cli pcb drc --all-track-errors --severity-all -o hardware/action_block/reports/routing_drc.rpt hardware/action_block/action_block.kicad_pcb`

- Unconnected items: **0** (previously 17).
- Copper clearance violations: **0**.
- DRC errors: **0**.
- Existing warnings: **39** — 31 text-height, 6 silkscreen overlaps, 2 silkscreen/board-edge clearances. Warning types and affected item UUIDs match the unrouted baseline exactly. These warnings remain; this is not an entirely warning-free DRC.
- No DRC rules or exclusions were changed.

Machine-readable results: `routing_drc.json`; baseline: `routing_drc_before.json`.

## Previews

- `../pcb_preview/action_block_routed.svg`: KiCad composite F.Cu, B.Cu, F.Silkscreen, Edge.Cuts export.
- `../pcb_preview/action_block_top.png`: KiCad raytraced orthographic top view, 1600 × 1600 pixels. Custom footprints have no component 3D models; the render shows the PCB, pads, copper, and silkscreen.
