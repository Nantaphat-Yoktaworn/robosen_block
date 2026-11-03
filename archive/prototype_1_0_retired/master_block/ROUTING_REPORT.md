# PCB routing and copper fill

Board: `robosen_master_block.kicad_pcb`  
Verified: 2026-10-04, KiCad 10.0

## Completed

- Routed all 24 signal and power nets: 460 track segments and 21 through vias.
- Power traces: 0.8 mm on `+3V3`, `/VBAT_SW`, `/VBAT_PROT`, `/VBAT_RAW`, and `/VBAT_GND`.
- Signal traces: 0.25 mm. Signal vias: 0.6 mm diameter / 0.3 mm drill; power vias: 1.0 mm / 0.5 mm.
- Added filled GND zones on F.Cu and B.Cu, with polygon corners at (85, 60) and (203.5, 125.5) mm. KiCad clips the fill to the board outline and honors the existing antenna copper keepout.
- Zone clearance: 0.25 mm; thermal gap: 0.3 mm; thermal spoke width: 0.4 mm. Unconnected copper islands are removed.
- Kept `/VBAT_GND` separate from system GND, preserving the charger protection topology.
- Preserved all footprint positions, orientations, sides, UUIDs, and locking states, including H1-H4. The outline and original keepout were retained.

## DRC result

**Zero unconnected items; no remaining unrouted nets.** Intentionally unconnected pins retain their original net assignments.

| Finding | Before | After |
| --- | ---: | ---: |
| Unconnected items | 60 | 0 |
| Other errors | 61 | 61 |
| Warnings | 58 | 58 |

All 119 remaining findings match the baseline by type, severity, description, and affected item UUIDs. No new DRC violations were introduced. No track clearance, short-circuit, thermal connection, via, or copper-edge violations were reported.

Existing errors still require review before fabrication:

- 57 plated-through-hole courtyard conflicts.
- 2 non-plated display mounting-hole conflicts with U1's courtyard.
- U1 has a self-intersecting courtyard.
- DISP1's footprint conflicts with U1's footprint keepout.

The 58 existing warnings comprise 34 text-height, 18 silkscreen-over-copper, 4 silkscreen-overlap, and 2 silkscreen-edge-clearance findings. These placement/library/silkscreen issues were not suppressed or altered by routing. The board is fully connected but does **not** have a clean overall DRC.

Machine-readable reports:

- [Before routing](reports/routing_drc_before.json)
- [After routing](reports/routing_drc_after.json)

## Reproduction

`scripts/route_master_pcb.py` implements a two-layer A* grid router with pad, hole, trace, via, board-edge, and antenna keepout obstacles. It reserves escape space at the ESP32 header before routing and fills both planes using `pcbnew.ZONE_FILLER`. It is specific to this placement and assumes the current through-hole pads and rectangular keepout. It refuses to reroute a board that already contains tracks; an unrouted copy is required to reproduce the routing.

Run the final DRC from the repository root in PowerShell:

```powershell
$env:KICAD_DOCUMENTS_HOME = "$PWD\hardware\kicad"
& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb drc --format json -o hardware/master_block/reports/routing_drc_after.json hardware/master_block/robosen_master_block.kicad_pcb
```

The documents-home override allows CLI initialization in this restricted workspace. The CLI reported denied access to its user registry key but completed the DRC and wrote the report. Validation uses the report contents, not the CLI exit code alone.
