# 📘 Prototype #1-1: Master Block PCB Respin Engineering Specification

> **Project:** Tangible Modular Physical Block Coding System for Robosen K1 Humanoid Robot  
> **Iteration:** Prototype #1-1 (ESP32-S3 Socket Footprint Row Spacing Respin)  
> **Document Purpose:** Engineering Change Order (ECO) documentation, root-cause failure analysis of Prototype #1 physical arrival, footprint correction parameters, autorouting & DRC verification, BOM, and production release package.  
> **Author:** Nantaphat Yoktaworn  
> **Date:** October 14, 2026  
> **Status:** **PRODUCTION FILES VERIFIED & PACKAGED FOR JLCPCB RE-ORDER**  
> **Repository:** `https://github.com/Nantaphat-Yoktaworn/robosen_block.git`

---

## 1. Executive Summary & Hardware Evolution

| Metric / Feature | **Prototype #0 (Breadboard)** | **Prototype #1 (Initial PCB Release)** | **Prototype #1-1 (Footprint Respin)** |
| :--- | :--- | :--- | :--- |
| **Physical Construction** | 5× MB-102 solderless breadboards & Dupont jumpers | Custom 2-layer FR-4 carrier PCBs ($1.6\text{ mm}$, 1 oz Cu) | Custom 2-layer FR-4 carrier PCBs ($1.6\text{ mm}$, 1 oz Cu) |
| **Action Blocks Carrier** | Breadboard wire-up | $32 \times 32\text{ mm}$ carrier PCB (JLCPCB arrived) | Unchanged ($32 \times 32\text{ mm}$, verified 100% correct) |
| **Master Controller Carrier** | Breadboard wire-up | $115.5 \times 62.0\text{ mm}$ carrier PCB (JLCPCB arrived) | $115.5 \times 62.0\text{ mm}$ carrier PCB (**Respun**) |
| **ESP32-S3 Socket Spacing** | Manual breadboard span | **$22.86\text{ mm}$ ($0.9\text{ in} / 900\text{ mil}$)** ❌ *Defect* | **$25.40\text{ mm}$ ($1.0\text{ in} / 1000\text{ mil}$)** ✅ *Fixed* |
| **Socket Compatibility** | Loose jumper fit | Deviation prevented physical module insertion | Exact fit for official ESP32-S3-DevKitC-1 |
| **Trace Routing State** | N/A (Jumper wires) | 100% routed (460 tracks, 21 vias) | 100% rerouted (469 tracks, 20 vias, 0 unconnected) |
| **DRC Clearance Verification**| N/A | 0 unconnected, 0 copper clearance errors | 0 unconnected, 0 copper clearance errors |
| **JLCPCB Order Status** | Tested August–Sept 2026 | Fabricated & Arrived October 14, 2026 | **Gerbers Packaged & Ready for Re-Order** |

---

## 2. Root Cause Analysis: Prototype #1 Physical Arrival Defect

### 2.1 The Discrepancy
Upon delivery and physical inspection of the Prototype #1 batch from JLCPCB on October 14, 2026:
1. **Action Blocks (`hardware/action_block/`)**: Passed all mechanical and dimensional checks. The 2×11 socket for the CH32V003F4P6, centered 4-pin pogo docks ($Y = 72.50\text{ mm}$), WS2812 header, and SWIO programming pads matched physical parts precisely.
2. **Master Block (`hardware/master_block/`)**: The through-hole female socket headers for `U1` (ESP32-S3-DevKitC-1) were spaced **$22.86\text{ mm}$ ($0.900\text{ in}$)** apart.
3. **The Physical Conflict**: The official Espressif **ESP32-S3-DevKitC-1-N16R8** development board has a pin row separation of **$25.40\text{ mm}$ ($1.000\text{ in} / 1000\text{ mil}$)**. As a result, the physical module could not bridge into the dual 1×22 header sockets (the footprint was exactly 1 grid pitch / 100 mil / $2.54\text{ mm}$ too narrow).

```text
PROTOTYPE #1 (DEFECTIVE):
   Pin 1..22 (X = -11.43 mm) <-------- 22.86 mm (0.90") --------> Pin 23..44 (X = +11.43 mm)
   [ESP32-S3 Module Pins (25.40 mm wide) COULD NOT SEAT!]

PROTOTYPE #1-1 (CORRECTED):
   Pin 1..22 (X = -12.70 mm) <---------- 25.40 mm (1.00") ----------> Pin 23..44 (X = +12.70 mm)
   [Exact drop-in socket alignment for official Espressif DevKitC-1]
```

### 2.2 Preserved Integrity
As instructed, all original Prototype #1 files remain completely preserved in [`hardware/master_block/`](hardware/master_block/) and [`PROTOTYPE_01_SPEC.md`](PROTOTYPE_01_SPEC.md). All corrections, rerouted boards, audit evidence, and new Gerbers are isolated under [`hardware/prototype_1_1/`](hardware/prototype_1_1/).

---

## 3. Engineering Changes in Prototype #1-1

### 3.1 Footprint Modifications (`robosen_master.pretty/ESP32-S3-DevKitC-1-Socket.kicad_mod`)
1. **Pin Rows**:
   - Pins 1–22 (Row 1): Local $X$ coordinate shifted from $-11.43\text{ mm}$ to **$-12.70\text{ mm}$** (Board $Y = 91.63\text{ mm}$).
   - Pins 23–44 (Row 2): Local $X$ coordinate shifted from $+11.43\text{ mm}$ to **$+12.70\text{ mm}$** (Board $Y = 66.23\text{ mm}$).
   - Total row-to-row spacing: **$25.40\text{ mm}$ ($1000\text{ mil}$)**.
2. **Silkscreen & Courtyard Outlines**:
   - Silkscreen rectangle expanded from $X = \pm 13.5\text{ mm}$ to **$X = \pm 14.2\text{ mm}$** (total $28.4\text{ mm}$ width) to clear outer pad solder fillets.
   - Courtyard rectangle expanded from $X = \pm 14.0\text{ mm}$ to **$X = \pm 14.7\text{ mm}$** (total $29.4\text{ mm}$ width).
   - Silkscreen pin labels ("1", "22", "23", "44") moved from $X = \pm 14.0\text{ mm}$ to **$X = \pm 15.2\text{ mm}$** to eliminate silkscreen-over-copper collisions.
3. **Overhang & Keepout**:
   - Kept antenna copper keepout zone ($17.5 \times 6.0\text{ mm}$) at board edge centered on $X = 0$.

### 3.2 Automated PCB Retracing & autorouting
Using KiCad 10 Python SWIG bindings:
1. Stripped all previous copper tracks, vias, and copper pours from `robosen_master_block.kicad_pcb`.
2. Updated embedded `U1` footprint definition and pad positions.
3. Executed automated two-layer A* grid router:
   - Reserved interior escape channels for the ESP32 socket.
   - Routed all 24 signal and power nets with zero failed nets.
   - Repoured filled `GND` ground planes on `F.Cu` and `B.Cu` with $0.25\text{ mm}$ clearance and thermal relief spokes.
   - Verified DW01A battery protection `/VBAT_GND` ground loop isolation.

---

## 4. Design Rules Check (DRC) & Verification Results

### 4.1 DRC Summary
Ran `kicad-cli pcb drc` on `hardware/prototype_1_1/master_block/robosen_master_block.kicad_pcb`:
* **Unconnected Items:** **0 (Zero)**
* **Track Clearance Violations:** **0 (Zero)**
* **Short Circuits:** **0 (Zero)**
* **Via Violations:** **0 (Zero)**
* **Total Remaining Findings:** 116 (courtyard conflicts between socket pins and cosmetic silkscreen text height notices).

### 4.2 Mechanical M3 Mounting Hole Clearances
Verified with `scripts/verify_prototype_1_1.py` against standard $6.4\text{ mm}$ standoff / screw boss diameter ($R \ge 3.20\text{ mm}$):
* **`H1` at $(96.25, 92.00)$**: Closest copper = **$3.68\text{ mm}$** (`/CFG_RX` trace on `B.Cu`) $\rightarrow$ **PASS**
* **`H2` at $(192.25, 92.00)$**: Closest copper = **$3.68\text{ mm}$** (`/K2_DT` trace on `B.Cu`) $\rightarrow$ **PASS**
* **`H3` at $(91.50, 120.50)$**: Closest copper = **$12.69\text{ mm}$** (`/BTN_STOP` trace on `F.Cu`) $\rightarrow$ **PASS**
* **`H4` at $(197.00, 120.50)$**: Closest copper = **$5.29\text{ mm}$** (`/CHAIN_RX` trace on `F.Cu`) $\rightarrow$ **PASS**

### 4.3 Clearance to Adjacent Onboard Components
* Nearest pad to U1 Pad 1 $(172.78, 91.63)$: `DISP1` Pad at $(176.50, 90.50)$ — **$3.89\text{ mm}$** clearance.
* Nearest pad to U1 Pad 23 $(172.78, 66.23)$: `DISP1` Pad at $(176.50, 65.50)$ — **$3.79\text{ mm}$** clearance.
* All other components have $>4.0\text{ mm}$ physical separation.

---

## 5. Prototype #1-1 Directory Structure & Manufacturing Artifacts

```
hardware/prototype_1_1/
├── master_block/
│   ├── robosen_master_block.kicad_pro       # KiCad 10 project file
│   ├── robosen_master_block.kicad_sch       # Master schematic
│   ├── robosen_master_block.kicad_pcb       # 100% routed carrier PCB (U1 spacing = 25.40 mm)
│   ├── robosen_master_block_schematic.pdf   # Vector schematic PDF
│   ├── robosen_master_block_gerbers.zip     # Production Gerbers for JLCPCB re-order
│   ├── gerbers/                             # Exported Gerber & Excellon drill files
│   │   ├── robosen_master_block-F_Cu.gbr
│   │   ├── robosen_master_block-B_Cu.gbr
│   │   ├── robosen_master_block-F_Silkscreen.gbr
│   │   ├── robosen_master_block-B_Silkscreen.gbr
│   │   ├── robosen_master_block-F_Mask.gbr
│   │   ├── robosen_master_block-B_Mask.gbr
│   │   ├── robosen_master_block-Edge_Cuts.gbr
│   │   ├── robosen_master_block-PTH.drl
│   │   └── robosen_master_block-NPTH.drl
│   ├── reports/
│   │   ├── routing_drc_after.json           # Machine-readable KiCad DRC report
│   │   ├── drc_report.txt                   # Human-readable DRC text report
│   │   ├── independent_audit_geometry.json  # Python geometric audit database
│   │   ├── independent_audit_F_Cu.svg       # Standalone Top copper visualization
│   │   └── independent_audit_B_Cu.svg       # Standalone Bottom copper visualization
│   ├── robosen_master.pretty/
│   │   └── ESP32-S3-DevKitC-1-Socket.kicad_mod # Corrected footprint (25.40 mm spacing)
│   ├── README.md                            # Directory guide
│   └── ROUTING_REPORT.md                    # Detailed routing analysis
└── action_block/                            # Unchanged Action Block carrier (100% verified)
```

---

## 6. JLCPCB Re-Order Instructions for Master Block

1. Navigate to [JLCPCB Quick Order](https://cart.jlcpcb.com/quote).
2. Upload archive: [`hardware/prototype_1_1/master_block/robosen_master_block_gerbers.zip`](file:///C:/Users/nnnn/Projects/robosen_block/hardware/prototype_1_1/master_block/robosen_master_block_gerbers.zip).
3. Confirm PCB Specifications:
   - **Dimensions:** $115.5\text{ mm} \times 62.0\text{ mm}$
   - **Layers:** 2 Layers
   - **PCB Thickness:** $1.6\text{ mm}$
   - **Base Material:** FR-4
   - **Copper Weight:** 1 oz ($35\,\mu\text{m}$)
   - **Surface Finish:** HASL with lead (or ENIG if preferred)
   - **Solder Mask:** Green (or preferred color)
   - **Silkscreen:** White
   - **Via Covering:** Tented
4. Note: **No changes are needed for the Action Blocks** — the Prototype #1 Action Block batch from JLCPCB is completely compatible with Prototype #1-1 Master Blocks.
