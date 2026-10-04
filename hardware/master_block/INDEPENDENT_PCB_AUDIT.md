# Independent routed-PCB audit

**Board:** `robosen_master_block.kicad_pcb`  
**Audit date:** 2026-10-04  
**Verdict: routing is complete, but hold release for normal fabrication/assembly until the mechanical and RF findings below are resolved.** There are no detected electrical routing violations under the current project rules. That does not establish that the assembled product fits or that its antenna performs adequately.

The audited board has 21 footprints, 476 straight track segments, 21 vias, two copper layers, a 115.5 × 62 mm rectangular outline, and nominal 1.6 mm thickness. No source PCB, schematic, or project settings were changed.

| Check | Independent result |
|---|---|
| Required CAD connectivity | Complete: zero unconnected items, both before and after refilling |
| Dangling tracks / vias | None reported |
| Shorts / electrical copper clearances | None reported under configured rules |
| Five requested power nets | Every segment is 0.80 mm wide; no discrete vias on these nets |
| Battery negative versus system ground | Separate copper; approximately 0.25 mm minimum separation on both layers |
| H1–H4 traces, vias, component pads | Clear of the requested 2.85 / 3.25 / 3.50 mm radii |
| H1–H4 ground pours | Copper extends beneath hardware envelopes; not an all-copper mechanical clearance pass |
| Defined antenna rectangle | No carrier-board tracks, vias, pads, or filled copper inside it |
| Assembled antenna environment | Fails placement rule: display overlaps antenna rectangle; broader RF clearance is inadequate |
| Fresh DRC | 61 errors + 58 warnings; four additional schematic-parity warnings |

## 1. Evidence and method

The board was loaded independently with KiCad 10 `pcbnew`. KiCad CLI DRC was run against the current board and project with all severities, excluded violations, all track errors, and schematic parity enabled. It was run once with stored fills and once with `--refill-zones`, without `--save-board`. Both reports have identical violation, unconnected-item, and parity lists.

```powershell
$env:KICAD_DOCUMENTS_HOME = "$PWD\hardware\kicad"
& 'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe' pcb drc `
  --format json --severity-all --all-track-errors --schematic-parity `
  --refill-zones -o hardware/master_block/reports/independent_audit_drc.json `
  hardware/master_block/robosen_master_block.kicad_pcb
```

Measurements use actual board coordinates and copper edges. Track distances subtract half the actual track width; via distances subtract half the actual copper diameter, not the drill radius. Pads were polygonized with 0.001 mm geometric tolerance. Antenna tests intersect full copper shapes and filled polygons, rather than just testing endpoints or bounding boxes. Ground-isolation clearance was bracketed to approximately 0.001 mm using polygon collision tests. Stored and independently refilled zone areas and mounting-hole clearances match.

The source SHA-256 before and after inspection was:

`b44805e0233c39378f1b44351a8d4233defd64b724479f33255d2bd5abe69faf`

Supporting artifacts:

- [Fresh DRC with refill](reports/independent_audit_drc.json) and [stored-fill DRC](reports/independent_audit_drc_stored.json).
- [Detailed geometry, coordinates, power nets, pads, and zone measurements](reports/independent_audit_geometry.json).
- [Front copper view](reports/independent_audit_F_Cu.svg) and [back copper view](reports/independent_audit_B_Cu.svg). Both use top-view PCB coordinates; the back view is deliberately not mirrored. Orange circles show the screw radius, red circles the largest boss radius, and blue dashed rectangles the battery/display bodies.
- [Reproducible geometry inspection script](../../scripts/independent_pcb_audit.py).

These are CAD findings. The actual module variants, pin lengths, solder heights, enclosure, hardware tolerances, finished copper weight, and operating current were not supplied or physically measured. Schematic parity verifies CAD consistency, not the correctness of custom symbols or their mapping to purchased hardware.

## 2. Connectivity and netlist

**All connections required by the current CAD netlist are routed.** Both DRC runs report zero unconnected items, and neither reports `track_dangling`, `via_dangling`, `shorting_items`, `tracks_crossing`, or copper-clearance errors. Intentional single-pad `unconnected-(...)` nets on unused module pins are not missing routes.

The four schematic-parity warnings are `extra_footprint` for H1, H2, H3, and H4. They are mechanical holes present only on the PCB. No electrical schematic/PCB discrepancy was reported. Document these as intentional PCB-only hardware or represent them consistently in the schematic.

The existing `scripts/verify_routing.py` was not treated as proof of connectivity: its final net check counts pads and prints success without testing their physical connection. The independent conclusion above comes from the fresh KiCad connectivity/DRC results.

## 3. Power routing and ground planes

| Net | Segments | Width, all segments | Copper layer | Total segment length | Discrete vias |
|---|---:|---:|---|---:|---:|
| +3V3 | 83 | 0.80 mm | F.Cu | 157.86 mm | 0 |
| /VBAT_SW | 23 | 0.80 mm | F.Cu | 52.32 mm | 0 |
| /VBAT_PROT | 15 | 0.80 mm | F.Cu | 25.91 mm | 0 |
| /VBAT_RAW | 8 | 0.80 mm | B.Cu | 26.97 mm | 0 |
| /VBAT_GND | 12 | 0.80 mm | F.Cu | 53.86 mm | 0 |

Lengths are sums over each routed network, including branches; they are not all source-to-load path lengths. Through-hole pads provide layer access even where the table shows no discrete vias. There are no narrower track-segment neckdowns on these five nets; pad entries and plane thermal spokes are separate geometries.

This is a reasonable starting geometry for a low-power carrier, but it is not a verified current rating. Copper thickness, peak load, allowed voltage drop, ambient temperature, and module/connector ratings remain unspecified. For scale, assuming 35 µm copper at room temperature and copper resistivity 1.724 × 10⁻⁸ Ω·m, a 0.8 mm track is approximately 0.616 Ω/m. The dedicated battery-negative route is approximately 33 mΩ and battery-positive route approximately 17 mΩ: together about 50 mV drop at 1 A, before the charger protection MOSFETs, switch, other traces, contacts, and return-plane losses. This estimate is not a thermal qualification.

Measure 3.3 V at U1 and the dock loads during radio bursts and worst-case downstream loading, including low battery voltage. Inspect bulk decoupling on the actual DevKit/regulator modules and add carrier decoupling if those measurements require it. C1 in this carrier is the battery-sense filter, not rail bulk capacitance.

### Battery protection boundary

`/VBAT_GND` connects only **BT1 pad 2** and **U2 pad 3 (B−)**. System `GND` uses **U2 pad 4 (OUT−)**. Both large zones are assigned to `GND`; neither is assigned to battery negative. Independent polygon tests find no overlap between battery-negative copper and system-ground copper, with approximately **0.249–0.250 mm** minimum clearance on each layer (the interval reflects polygon/numerical tolerance around nominal 0.25 mm).

**The carrier layout preserves the intended B−/OUT− separation.** Verify the purchased charging module actually includes the intended protection MOSFET circuit; the TP4056 charger designation alone does not establish that feature. In the assembled circuit these nodes can conduct through enabled protection MOSFETs, so a simple continuity reading with the module installed does not prove a bypass. Check bare-carrier separation and then test the actual protection function with appropriate controlled equipment. External wiring, conductive hardware, or a solder bridge must not directly bond B− to system ground.

### Plane construction

| Layer | Assigned net | Filled area | Filled polygons | Foreign-net clearance | Thermal gap / spoke |
|---|---|---:|---:|---:|---:|
| F.Cu | GND | 4,978.38 mm² | 5 | 0.25 mm | 0.30 / 0.40 mm |
| B.Cu | GND | 5,610.03 mm² | 7 | 0.25 mm | 0.30 / 0.40 mm |

Island removal is set to **always**. DRC reports no isolated copper or starved thermals. Multiple polygon pieces are not, by themselves, floating islands: through-hole ground pads can connect pieces between layers. There are 20 physical system-ground pads, no explicit GND tracks, and no dedicated GND stitching vias.

Thus DC grounding passes, but this is not an uninterrupted reference plane everywhere. Routing slots and thermal spokes can constrain high-frequency return paths. Consider ground stitching near signal layer changes and around module/power regions, while respecting antenna and mechanical keepouts. Validate actual signal edge rates and power transients before treating the planes as electrically optimal.

### Design-rule limits

The Default class requests 0.20 mm clearance. The project minimum track width is 0.20 mm, copper-to-edge clearance 0.50 mm, and hole-to-copper clearance 0.25 mm. A `Power` class exists, but there are no explicit netclass assignments or patterns in the project JSON. Its preferred 0.60 mm track width is not evidence that these power nets are protected by an enforced minimum-width constraint. Their measured width is independently 0.80 mm.

Add explicit net assignments and minimum-width rules where required for future edits. The project-wide minimum copper clearance is zero; the effective Default-class and zone clearances are therefore important. Confirm the final fabrication rules against the chosen manufacturer's process.

## 4. M3 screw and printed-boss clearances

The four holes are 3.2 mm NPTH. The requested hardware radii are 2.85 mm for the screw head and 3.25–3.50 mm for the printed boss. Measurements below are **hole-center to nearest copper edge**, not clearance from the drill edge.

| Hole / center (mm) | Nearest track edge | Net / layer | Nearest via edge | Nearest component-pad edge | Track margin beyond R3.50 |
|---|---:|---|---:|---:|---:|
| H1 (96.25, 92.00) | 3.677 mm | /CFG_RX, B.Cu | 15.360 mm | 5.610 mm | +0.177 mm |
| H2 (192.25, 92.00) | 3.677 mm | /K2_DT, B.Cu | 5.005 mm | 5.348 mm | +0.177 mm |
| H3 (91.50, 120.50) | 12.691 mm | /BTN_STOP, F.Cu | 38.159 mm | 11.715 mm | +9.191 mm |
| H4 (197.00, 120.50) | 5.290 mm | /CHAIN_RX, F.Cu | 32.622 mm | 4.515 mm | +1.790 mm |

**Every routed trace and via clears all three nominal envelopes.** Component pads also clear them. The smallest trace margin to the R2.85 screw is 0.827 mm; to R3.25 it is 0.427 mm. H1/H2 have just 0.177 mm beyond a 7.0 mm diameter boss, so printing error, screw/hole play, boss eccentricity, and assembly tolerance need a specified budget. A larger washer must be assessed using its actual radius.

The ground pours give a different result:

| Hole | Nearest F.Cu GND edge radius | Nearest B.Cu GND edge radius | All copper outside R2.85 / R3.50? |
|---|---:|---:|---|
| H1 | 1.851 mm | 1.851 mm | No |
| H2 | 4.795 mm | 1.851 mm | No |
| H3 | 1.851 mm | 1.851 mm | No |
| H4 | 1.851 mm | 1.851 mm | No |

Except for the larger front opening around H2, these pours clear the 1.6 mm drill radius by approximately 0.2505 mm. They consequently extend about **1.00 mm into the screw-head radial envelope** and **1.65 mm into the largest boss envelope**.

This is not an existing signal short. Masked ground under a nonconductive printed boss can be acceptable in a deliberately approved stack-up. It does mean the statement “all copper clears the hardware” is false. Solder mask is not a durable bearing surface or a guaranteed isolation barrier under a metal screw head. Clamping and abrasion could ground conductive hardware or damage the finish.

For a robust revision, define copper, track, via, and pad keepouts around all mounting holes using the largest actual bearing/washer/boss radius plus the tolerance allowance, on the affected layers. A 3.50 mm nominal circle alone leaves no manufacturing/assembly allowance. Refill and repeat connectivity checks afterward. If retaining the present pour geometry, explicitly approve the hardware material, insulating washers/spacers, bearing surface, and clamping arrangement.

## 5. ESP32-S3 antenna

U1 is on B.Cu. Its actual footprint rule area is:

**X = 175.11–181.11 mm; Y = 70.18–87.68 mm; size 6.00 × 17.50 mm.**

It forbids tracks, vias, pads, copper pours, and footprints on F.Cu and B.Cu. Independent full-shape intersections find **zero track, via, or copper-pad intrusions**, and **0.000 mm² filled-zone overlap** on both layers, both stored and refilled.

**The carrier copper obeys that rectangle. The assembled antenna environment does not pass.** DRC reports `items_not_allowed` for DISP1 in U1's keepout. The display body outline is X = 108–179 mm, Y = 63–93 mm. It overlaps the antenna rectangle by **3.89 mm × 17.50 mm = 68.075 mm²**, approximately 65% of the rectangle. Its courtyard extends another 0.5 mm. Although display and DevKit are mounted on opposite sides, the display PCB, conductive layers, and other materials can still load or shield the antenna. Their actual internal geometry and vertical separation are not represented by the carrier copper check.

The antenna rectangle is also well inside the carrier: its right edge is 20.89 mm from the carrier's right edge, and carrier material/copper remain around the small local keepout. This is not a broad antenna-clearance implementation.

Espressif recommends placing the antenna outside the baseboard where possible; for an internal placement its guidance calls for board cutouts/adequate clearance, consideration of housing effects, and final throughput/range testing. Its current guidance recommends at least 15 mm clearance around the antenna within the housing. A local rectangle matching only the antenna outline cannot establish compliance. [Espressif ESP32-S3 PCB layout guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html#general-principles-of-pcb-layout-for-modules-positioning-a-module-on-a-base-board).

Move/orient U1 so the antenna can reach a suitable carrier edge, relocate the display from the antenna region, or evaluate an appropriate external-antenna module and antenna placement. Define the chosen module's actual clearance envelope and test the complete enclosure/display/battery assembly for RF performance.

## 6. DRC breakdown and assembly impact

The fresh board DRC contains **119 violations: 61 errors and 58 warnings**. Schematic parity adds **four warnings**, yielding **123 reported findings overall: 61 errors and 62 warnings**. No exclusions are configured. `--severity-all` includes excluded findings but does not enable checks configured as ignored.

| Category | Severity | Count | Engineering meaning |
|---|---|---:|---|
| `pth_inside_courtyard` | Error | 57 | Opposite-side through-hole tails/solder occupy another component's assembly envelope: 13 at BT1, 44 at DISP1 |
| `npth_inside_courtyard` | Error | 2 | DISP1 mounting holes conflict with U1's projected envelope; fasteners need a 3D clearance check |
| `items_not_allowed` | Error | 1 | DISP1 overlaps the antenna placement keepout |
| `malformed_courtyard` | Error | 1 | U1 courtyard self-intersects; reliable placement checking requires footprint repair |
| `text_height` | Warning | 34 | Text is below the configured 0.8 mm minimum; readability/printing yield concern |
| `silk_over_copper` | Warning | 18 | Legend conflicts with pad/mask-opening regions; fabrication may clip identifying text/graphics |
| `silk_overlap` | Warning | 4 | Overlapping legend can obscure assembly identification |
| `silk_edge_clearance` | Warning | 2 | J1 and U2 graphics extend into/beyond board-edge clipping regions |
| `extra_footprint` | Parity warning | 4 | Intentional-looking PCB-only H1–H4; no electrical mismatch reported |

The checks configured as ignored are missing courtyards, track endpoint centering on vias, tuning-profile geometries, footprint filters, and footprint component-type/pad-type mismatch. Electrical short, clearance, dangling-item, hole, mask-bridge, and thermal checks are enabled. No violations were reported for electrical clearances, copper edge clearance, annular width, hole spacing, track width, solder-mask bridges, or starved thermals under those settings.

### Through-hole pins underneath BT1

BT1 is on the back, centered at (143.5, 105.8). Its body outline spans **X = 104.75–182.25 mm, Y = 95.55–116.05 mm**. Its larger B.Courtyard spans X = 100–187 mm, Y = 94.8–116.8 mm.

| Front-side component | Pads flagged against BT1 | Pad centers (mm) | Interpretation |
|---|---|---|---|
| U2 | 1, 2, 3, 4 | X = 123.2, 126.4, 133.8, 137.0; Y = 99.8 | Four pin tails directly beneath holder body |
| U3 | 5, 6, 7, 8 | X = 145.06, 147.60, 157.50, 160.04; Y = 97.52 | Four pin tails directly beneath holder body |
| SW3 | Both physical pads numbered 1 | (178, 103.5), (178, 108.5) | Two switch legs beneath holder body |
| SW5 | Both physical pads numbered 2 | (108.5, 103.5), (108.5, 108.5) | Two switch legs beneath holder body |
| C1 | 1 | (186.96, 97.5) | Within enlarged courtyard, but outside the drawn holder body |

Twelve of these thirteen pad centers are directly beneath the drawn plastic holder body. The C1 finding is a separate edge/service-envelope concern, not evidence that its pin sits underneath that rectangular body.

These are real assembly risks, even though they are not bare-board copper shorts. Solder fillets and cut leads can stop the holder seating, concentrate clamping pressure, damage plastic, or contact unmodeled conductive holder parts. The PCB alone cannot determine whether the actual holder has underside cavities that avoid them.

Resolve with measured underside geometry and a documented vertical stack-up. Required spacing must exceed the maximum lead/solder projection plus assembly and deflection allowances; no arbitrary spacer height can be certified from this file. Suitable remedies include relocating the offending pins/components, using verified recessed holder geometry, or providing rigid insulating spacers and an appropriate barrier. Flush trimming alone does not remove solder-fillet height. Solder and inspect covered joints before fitting the holder; preserve rework access. Do not blanket-waive all thirteen findings without this evidence.

### U1, display, and remaining errors

All **44 U1 through-hole pads** are flagged against DISP1. U1 is on the back and DISP1 on the front, so U1's socket-pin tails and solder appear beneath the display. Check display standoff height and underside component clearance over both complete header rows, including unused pins. Opposite-side mounting does not eliminate pin-tail interference.

The two DISP1 NPTH findings are at **(176.5, 65.5)** and **(176.5, 90.5)** against U1. Check actual screws, nuts, and spacers; a drill-only DRC cannot prove fastener fit.

U1's courtyard consists of overlapping body and antenna rectangles, creating the reported self-intersection. Replace them with a valid closed courtyard contour and rerun DRC. The malformed courtyard limits confidence in placement checks around U1; fixing it may reveal additional findings.

The clipped U2 silkscreen represents an off-board module/connector outline and may be intentional for USB access, but confirm its enclosure opening and mechanical support. Clean up the J1 clipping, text below the process limit, pad-overlaid silk, and four silk overlaps before generating fabrication files. These are generally documentation/assembly-quality issues, not evidence of open circuits.

## 7. Release recommendation

**Do not release this revision as a mechanically and RF-validated production board.** Its routing completeness and battery-ground separation are good; the unresolved stack-up, antenna placement, and hardware-bearing copper geometry prevent an unconditional fabrication/assembly approval.

1. Resolve BT1 and DISP1 pin-tail clearances with measured parts and an explicit stack-up; repair U1's courtyard and check display fasteners.
2. Resolve display/antenna overlap and define the actual RF clearance region. Validate range/throughput with the intended enclosure and populated assembly.
3. Add mounting hardware keepouts including tolerance, or document a verified insulating/bearing arrangement. Preserve additional margin at H1/H2.
4. Specify finished copper weight and load budget; enforce power-net constraints and verify voltage drop/transients at maximum load and low battery.
5. Clean up fabrication legends, refill zones, rerun full DRC and schematic parity, and inspect final Gerber/drill outputs. Only waive individual mechanical findings supported by measured assembly evidence.

A controlled fit-test prototype could be useful after the mechanical risks are understood, but the present evidence does not support labeling the design “DRC clean,” “all copper clear of mounting hardware,” or “RF keepout fully validated.”
