**Final pre-order engineering audit — 2026-10-05, KiCad 10.0.6**

> [!NOTE]
> **Post-Audit Disposition & Order Confirmation (2026-10-05):**  
> Following this dual-agent audit, the reported courtyard DRC warnings on the Master Block were reviewed and confirmed to be benign 3D physical overlaps between top-side components (Tactile Buttons, E-Paper Display) and bottom-side carrier sockets (ESP32-S3 DevKit, 18650 Battery Holder), which is the intended double-sided sandwich daughterboard carrier architecture. Zero electrical shorts or copper clearance violations exist on either board. Both the **Master Block PCB** and **Action Block PCB** have been approved and **ORDERED AT JLCPCB**.

**Audit Production verdict:** Action Block passes the requested bare-board geometry, routing, copper-clearance and fabrication-package checks, with silkscreen/documentation qualifications below. Master Block has complete electrical routing and a current fabrication package, with double-sided carrier courtyard envelopes investigated.

This is an audit of the actual files, not an endorsement of previous reports. No source PCB, schematic, project, footprint or production ZIP was modified. Evidence, independent scripts and fresh comparison exports are in [preorder_audit_evidence](preorder_audit_evidence/). The comparison exports are audit artifacts, not replacement release packages.

| Result | Action Block | Master Block |
|---|---|---|
| Edge.Cuts nominal dimensions | PASS: 32.00 × 32.00 mm | PASS: 115.50 × 62.00 mm |
| Unconnected items, stored and refilled | **0** | **0** |
| Board DRC errors / warnings | **0 / 39** | **61 / 58** |
| Electrical copper shorts / clearance violations | None reported | None reported |
| Additional schematic-parity warnings | 15, investigated below | 4 PCB-only mounting footprints |
| Fresh schematic ERC | 0 violations | 0 violations |
| Requested power trace widths | All +3V3 segments 0.60 mm | All five requested power nets 0.80 mm |
| ZIP integrity and freshness | 10 files; all match fresh exports after timestamp normalization | 10 files; all match fresh exports after timestamp normalization |
| Bare-board fabrication disposition | PASS with noted legend qualifications | Electrically fabricable, but HOLD production release for mechanical/RF findings |

**Method, reproducibility and rule limits**

KiCad CLI was run with the requested DRC options, adding explicit output paths and JSON format for reliable counting:

```sh
kicad-cli pcb drc --all-track-errors --severity-all --format json \
  -o hardware/preorder_audit_evidence/action_stored.json \
  hardware/action_block/action_block.kicad_pcb
kicad-cli pcb drc --format json \
  -o hardware/preorder_audit_evidence/master_stored.json \
  hardware/master_block/robosen_master_block.kicad_pcb
```

Both were also checked with `--all-track-errors --severity-all --schematic-parity --refill-zones`, without `--save-board`. The stored/refilled board-violation lists are identical and both runs have zero unconnected items. Counts come from report contents: a successful CLI process exit alone does not mean DRC passed. Both schematics received fresh ERC checks. CLI emitted a Fontconfig diagnostic during schematic operations; reports and netlist exports completed. Action netlist export additionally warned of annotation errors; this should be cleaned up, even though the exported electrical netlist matches the PCB exactly.

Independent `pcbnew` measurements used the supplied KiCad Python interpreter. Both boards are two-layer, nominal 1.60 mm thick. Action has six footprints, 37 track segments and no vias; Master has 21 footprints, 476 segments and 21 vias. Polygon clearance measurements use 0.001 mm shape approximation and approximately 0.001 mm search resolution; they are not physical manufacturing-tolerance measurements.

Both projects use Default-netclass clearance 0.20 mm, zone clearance 0.25 mm, minimum track width 0.20 mm, copper-to-edge clearance 0.50 mm, hole-to-copper clearance 0.25 mm and two minimum resolved thermal spokes. Global minimum clearance is 0.0 mm; the netclass/zone rules therefore matter. No DRC exclusions are configured. `--severity-all` does not turn on ignored checks: missing courtyards, track endpoints centered on vias, tuning-profile geometry, footprint filters and footprint-type/pad-type matching are ignored in both projects. The existing Power class has no explicit assignments/patterns; the measured 0.60/0.80 mm widths are not protected by corresponding minimum-width rules.

**A. Action Block — geometry and connections**

Edge.Cuts is one closed rectangle from **(80.50, 56.50) to (112.50, 88.50) mm**: exactly **32.00 × 32.00 mm**, center (96.50, 72.50). Its drawing stroke is 0.10 mm. Board dimensions are measured on the outline centerline; the ink/stroke bounding box would be 32.10 × 32.10 mm and must not be mistaken for the routed board size. No invalid-outline violation is reported.

IN origin is **(83.50, 68.69)** and OUT origin is **(109.50, 68.69)**, both at 0°. Each four-pad array spans Y = 68.69–76.31 mm on 2.54 mm pitch; its midpoint and pad-center average are exactly **72.50 mm**. “Centered pads” means the array is centered, not that each individual pad lies at Y = 72.50.

| Pad | Y (mm), both docks | IN net, X = 83.50 | OUT net, X = 109.50 |
|---|---:|---|---|
| 1 | 68.69 | +3V3 | +3V3 |
| 2 | 71.23 | GND | GND |
| 3 | 73.77 | /RX_IN | /TX_OUT |
| 4 | 76.31 | /RETURN_BUS | /RETURN_BUS |

All eight dock assignments pass. Pad diameter is 2.00 mm and drill diameter is 1.10 mm.

RGB uses **WS2812B_Module_1x03_P2.54mm**, at (84.00, 62.50), rotated −90°. It has exactly three through-hole pads, 1.80 mm across with 1.00 mm drills. Top/bottom below refer to the PCB top view, with smaller Y toward the top.

| RGB pin | Position (mm) | Net | Result |
|---|---|---|---|
| 1, top | (84.00, 59.96) | GND | PASS |
| 2, middle | (84.00, 62.50) | +3V3 | PASS |
| 3, bottom | (84.00, 65.04) | /LED_DIN | PASS |

The latest header and dock revisions are present in both the PCB and packaged drill/copper outputs.

**A. Action Block — traces and ground fills**

`/RETURN_BUS` is one continuous seven-segment **B.Cu, 0.40 mm** route, approximately 42.549 mm long, joining IN:4 to OUT:4. Its ordered path is:

```text
(83.50,76.31) → (86.00,78.81) → (86.00,85.25)
→ (88.00,87.25) → (104.90,87.25) → (106.50,85.65)
→ (106.50,79.31) → (109.50,76.31)
```

The requested lower detour exists at **Y = 87.25 mm**. The horizontal trace's lower copper edge is Y = 87.45, leaving **1.05 mm** to the bottom board edge. This is below the MCU's lowest pad row at Y = 85.40; it remains within the module's projected body area, which is acceptable for a backside trace absent some separate mechanical constraint. DRC finds no short, crossing, dangling segment or clearance violation on this net.

`/LED_DIN` is a continuous three-segment **F.Cu, 0.30 mm** route, approximately 9.632 mm long:

```text
RGB:3 (84.00,65.04) → (86.50,67.54)
→ (86.50,70.44) → MCU:6 (88.76,72.70)
```

MCU:6 is the TENSTAR module header's PA2 pin, not bare-chip package pin 6. `/RX_IN` ends at MCU:8, `/TX_OUT` at MCU:9 and `/SWIO` at MCU:16.

Every +3V3 trace segment is **0.60 mm** wide: 14 segments totaling approximately 60.174 mm. All **seven power pads** are on the connected network: IN:1, OUT:1, RGB:2, C104:2, PROG:2, MCU:10 and MCU:21. There are no power vias or narrower power segments.

All **seven ground pads** are connected: IN:2, OUT:2, RGB:1, C104:1, PROG:1, MCU:11 and MCU:22. Each inherits the zone thermal setting; direct pad/fill polygon intersections confirm copper contact on **both layers for all seven pads**. Both zones use 0.30 mm thermal gap and 0.40 mm spoke width. DRC reports no starved thermal or isolated copper. Ground has no explicit tracks or stitching vias; the plated ground pads connect the layers.

| GND fill | Filled area (mm²) | Polygon regions | Stored/refilled |
|---|---:|---:|---|
| F.Cu | 728.539 | 2 | Same measured area/count |
| B.Cu | 730.471 | 1 | Same measured area/count |

Island removal is **always**. Ground connectivity passes, but the statement “continuous dual-layer planes” needs qualification: front copper has two regions connected through the overall plated-pad/back-plane network. It is not one uninterrupted front sheet, and DC connectivity alone does not establish optimal high-frequency return paths.

**A. Action Block — DRC and remaining qualifications**

The requested board DRC has **0 unconnected items, 0 errors, 0 electrical copper-clearance violations, and 39 warnings**:

| Category | Count | Disposition |
|---|---:|---|
| Text below configured 0.8 mm minimum height | 31 | Improve readability or explicitly accept final CAM legend |
| Silkscreen overlaps | 6 | RGB GND/VCC/IN and PROG GND/3V3/SWIO labels overlap their outlines |
| Silkscreen edge clearance | 2 | IN circle and MCU outline are clipped at board edge |

Thus it is electrically DRC-clean under the configured rules, **not warning-free**. No copper-edge, annular-width, drill-spacing, solder-mask-bridge or thermal violations were reported.

Parity adds 14 `net_conflict` warnings saying no corresponding schematic pin was found for MCU pads **1–5, 7, 12–15, 17–20**, plus one C104 Description-field mismatch. These 14 pins have explicit schematic no-connect markers. Independent comparison of the freshly exported netlist against every PCB pad confirms **all 21 nets match exactly, including all 14 intentional one-pin no-connect nets**. These warnings are not evidence of fourteen missing functional routes. Preserve this evidence or resolve the parity/annotation reporting issue; do not hide genuine future discrepancies with a blanket exclusion.

The Action README is stale: it describes a 30 mm board and SOP-8 CH32V003J4M6 rather than this 32 mm TENSTAR-module carrier. Update it before assembly procurement. The MCU's modeled connector reaches Y = 55.70, **0.80 mm beyond the top board edge**; its courtyard spans Y = 55.20–88.70. Check that intended connector access and the enclosure accommodate this overhang. The copper outline itself passes.

RGB module procurement must specify the actual module and voltage grade, not just “WS2812.” The current [Worldsemi family table](https://www.world-semi.com/web/index.php?classid=302&id=299&lanstr=en&topclassid=16) lists WS2812B at 3.3–5.5 V, but that does not identify the chip revision on the purchased module. Verify its pin order, supply range, input thresholds and operation at the lowest voltage after regulator tolerance and chain drop. This is a component qualification item, not a detected wrong PCB connection.

**B. Master Block — dimensions, routing and battery isolation**

Edge.Cuts is one closed 0.10 mm-stroke rectangle from **(86.50, 62.00) to (202.00, 124.00) mm**, giving exactly **115.50 × 62.00 mm** on its centerline. No invalid-outline finding is reported.

All requested power segments measure **0.80 mm**:

| Net | Segments | Routed length (mm) | Connected pads |
|---|---:|---:|---|
| +3V3 | 83 | 157.856 | 11 |
| /VBAT_RAW | 8 | 26.966 | BT1:1, U2:2 |
| /VBAT_PROT | 15 | 25.906 | U2:1, SW4:1 |
| /VBAT_SW | 23 | 52.321 | SW4:2, U3:3, U3:4, R3:1 |
| /VBAT_GND | 12 | 53.856 | BT1:2, U2:3 |

`/VBAT_GND` has exactly those two endpoints and is a distinct net from GND. Independent polygon checks including tracks, pads, vias and ground fills find **zero overlap with system GND on either layer**. Minimum separation is approximately **0.25 mm** on each layer (computed bracket 0.249023–0.250000 mm). Isolation passes the configured rules; the README's stronger “strictly >0.25 mm” claim is not substantiated. This establishes carrier copper separation, not isolation inside an installed charger/protection module or attached cables.

Master's GND fills cover 4,978.379 mm² on F.Cu in five regions and 5,610.027 mm² on B.Cu in seven regions, unchanged in measured area/count after refill. Twenty physical GND pads form the connected network. Both layers use the same 0.30/0.40 mm thermal settings as Action. No unconnected items, electrical shorts, copper-clearance violations, isolated-copper or starved-thermal findings are reported.

Measured width alone does not certify a current rating: finished copper, allowable heating, ground thermal bottlenecks, regulator capability, pogo ratings and maximum chain load still define the operating limit.

**B. Master Block — production blockers**

| Board DRC category | Severity | Count |
|---|---|---:|
| PTH inside another component's courtyard | Error | 57 |
| NPTH inside courtyard | Error | 2 |
| DISP1 in U1 keepout | Error | 1 |
| U1 self-intersecting courtyard | Error | 1 |
| Text height | Warning | 34 |
| Silkscreen over copper/pad openings | Warning | 18 |
| Silkscreen overlap | Warning | 4 |
| Silkscreen clipped at board edge | Warning | 2 |
| **Total board DRC** | **61 errors + 58 warnings** | **119** |

Four additional parity warnings identify PCB-only H1–H4; no functional connection mismatch is reported. The full refilled/parity run therefore contains **123 findings**, separate from the zero unconnected-item count.

The 57 PTH conflicts comprise **44 U1 header pads beneath DISP1** and **13 pads within BT1's courtyard**. Twelve of the latter are beneath the drawn battery-holder body: U2:1–4, U3:5–8, both physical SW3:1 pads and both physical SW5:2 pads. C1:1 is the thirteenth courtyard conflict but is outside the body rectangle. Opposite-side footprints do not remove the need to accommodate through-hole tails and solder fillets. Confirm measured standoff heights, holder underside recesses, insulation and worst-case lead projection. The README's suggested foam and flush trimming are not a verified tolerance stack-up.

The two NPTH conflicts are DISP1 mounting holes at **(176.50, 65.50)** and **(176.50, 90.50)** within U1's projected courtyard. Check the complete screws/spacers/nuts and module envelopes. Repair U1's self-intersecting courtyard before relying on placement-check coverage.

The antenna rule area is **X = 175.11–181.11, Y = 70.18–87.68 mm**. Independent full-shape measurements find **0.000 mm² carrier-copper intrusion on either layer**. Nevertheless, DISP1 violates the footprint keepout. Its drawn body X = 108–179, Y = 63–93 overlaps that antenna rectangle by **3.89 × 17.50 = 68.075 mm²**. This is an assembled RF/placement issue despite the clean carrier copper. [Espressif's module layout guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html) recommends placing the antenna outside the baseboard where possible and maintaining adequate clearance, including at least 15 mm around it within the housing. Resolve placement or substantiate the chosen antenna/assembly with appropriate RF testing; the local rectangle alone is insufficient.

These fresh findings reproduce the substantive assembly/RF problems in the existing independent audit. They cannot be reclassified as harmless simply because electrical connectivity is complete. Clean up the 58 legend warnings as part of the release revision.

**C. Fabrication ZIP integrity and currency**

Both archives pass ZIP CRC checks, have no duplicate member names and contain exactly these ten flat files, using their respective prefixes `action_block` and `robosen_master_block`:

| Suffix | Purpose | Action | Master |
|---|---|---|---|
| -F_Cu.gtl | Top copper | Present/current | Present/current |
| -B_Cu.gbl | Bottom copper | Present/current | Present/current |
| -F_Mask.gts | Top solder mask | Present/current | Present/current |
| -B_Mask.gbs | Bottom solder mask | Present/current | Present/current |
| -F_Silkscreen.gto | Top legend | Present/current | Present/current |
| -B_Silkscreen.gbo | Bottom legend | Present/current | Present/current |
| -Edge_Cuts.gm1 | Routed outline | Present/current | Present/current |
| -PTH.drl | Plated drills | Present/current | Present/current |
| -NPTH.drl | Nonplated drills | Present/current | Present/current |
| -job.gbrjob | Gerber job metadata | Present/current | Present/current |

Precisely, these are **seven Gerbers, two Excellon drill files and one job file**, not ten Gerber/drill artwork files. Master README lists a drill report as the tenth file; the actual archive contains the job file instead. A drill report is not the drill program and its absence does not mean holes are missing.

Fresh exports used `pcb export gerbers -l F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts` and `pcb export drill --excellon-separate-th`. All twenty archive members match their fresh counterparts after removing only creation-date metadata/comments. No geometric, aperture, coordinate, net-attribute, drill-tool or job-setting differences remain. The new RGB drill hits at (84, −59.96), (84, −62.50), (84, −65.04), and both docks' revised drill coordinates are explicitly present. Excellon Y signs follow export coordinates; they do not indicate an erroneously mirrored board.

Action contains **38 PTH hits** with 0.85/1.00/1.10 mm tools. Its NPTH program intentionally has **zero hits**, consistent with the board having no NPTH holes. Its back legend is also intentionally empty artwork. Master contains **127 plated hits**, including 21 vias, with 0.30/0.85/1.00/1.10/1.20/1.30 mm tools, and **14 NPTH hits** with 2.20/3.20 mm tools. Outline and drill origin/units match fresh exports.

This confirms package completeness and consistency; it does not constitute a fabricator's CAM acceptance, a physical fit test, or evidence that the assembled electronics operate correctly.

**Release actions and final disposition**

1. **Action:** Copper and the two requested revisions pass. Its present package is suitable for bare-board fabrication with the documented legend qualifications. Improve the conflicting/clipped labels, correct stale documentation and annotation warnings, and confirm module/enclosure compatibility before calling the assembled product production-qualified. The investigated no-connect parity warnings do not represent missing routes.
2. **Master:** Hold production order. Repair the courtyard, resolve/document all pin-tail and fastener clearances with actual dimensions, and resolve the display/antenna conflict. Then rerun full refilled DRC/parity and regenerate the release ZIP after any change.
3. **Joint order:** **Not approved as an unconditional production release.** Both packages are current and both layouts have zero unconnected items, but that does not overcome Master's 61 unresolved assembly/placement errors.

**Audit identity**

| Input | SHA-256 |
|---|---|
| Action PCB | `bf540996d46648c4fcbf37c8f79539da147fc131260e56a972ba8c4b9a1a320d` |
| Master PCB | `44cd5299f6834351aad9d08645dcbc903c97fa4cf2c73a6ffe21a0e4d53c7928` |
| Action production ZIP | `a7797fa7b5b42915fe014b7d6b90f4adbe9b091aee8f23857b6d91a95dba3e2e` |
| Master production ZIP | `080c174462b0789689491e709395a5da4f25a29b3d2153bf8d12985a1836ee07` |

Raw measurements: [Action geometry](preorder_audit_evidence/action_geometry.json), [Master geometry](preorder_audit_evidence/master_geometry.json), [Action ground contacts](preorder_audit_evidence/action_ground_contacts.json), [Action netlist comparison](preorder_audit_evidence/action_netlist_comparison.json), [archive comparison](preorder_audit_evidence/archive_integrity.json). DRC evidence: [Action stored](preorder_audit_evidence/action_stored.json), [Action refilled/parity](preorder_audit_evidence/action_refilled_parity.json), [Master stored](preorder_audit_evidence/master_stored.json), [Master refilled/parity](preorder_audit_evidence/master_refilled_parity.json).
