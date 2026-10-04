# Robosen K1 Master Block — KiCad 10 Hardware Project

> **Project:** Custom Carrier Motherboard PCB for Robosen K1 Tangible Coding Block  
> **KiCad Version:** KiCad 10.0.6 (Fully compatible with KiCad 8.x / 9.x / 10.x)  
> **Workspace Directory:** `hardware/master_block/`  
> **Schematic Status:** Fully pre-wired, verified with KiCad ERC (**0 violations**)  
> **PCB Routing Status:** 100% Routed, verified with KiCad DRC (**0 unconnected items**)  
> **Fabrication Files:** Gerbers & Excellon drill files generated and packaged in `robosen_master_block_gerbers.zip`  
> **Order Status:** **ORDERED AT JLCPCB (October 5, 2026)**  
> **Author:** Nantaphat Yoktaworn / Antigravity AI  

---

## 1. Project Directory Structure

```
hardware/master_block/
├── robosen_master_block.kicad_pro       # KiCad Master Project configuration
├── robosen_master_block.kicad_sch       # Complete pre-wired Starter Schematic (A3 format)
├── robosen_master_block.kicad_pcb       # Carrier Board PCB Layout (17 components pre-placed)
├── robosen_master_block.kicad_prl       # KiCad Project local settings
├── robosen_master_block.net             # Exported netlist (kicadsexpr format)
├── robosen_master_block_schematic.pdf   # High-resolution vector PDF export of schematic
├── footprint_svg/                       # Vector SVG renders of all 12 custom footprints
│   ├── 18650_Battery_Holder_Single.svg
│   ├── C_Disc_P2.54mm.svg
│   ├── EPaper_2.13in_Header_1x08.svg
│   ├── ESP32-S3-DevKitC-1-Socket.svg
│   ├── KY-040_Rotary_Encoder_Module.svg
│   ├── Pogo_4Pin_Dock_2.54mm.svg
│   ├── R_Axial_P10.16mm.svg
│   ├── SW_Power_2Wire_Pads.svg
│   ├── SW_PUSH_12x12mm.svg
│   ├── SW_Slide_SS12D00.svg
│   ├── TP4056_Type-C_Module.svg
│   └── TPS63020_BuckBoost_Module.svg
├── schematic_svg/
│   └── robosen_master_block.svg         # Vector SVG render of schematic
├── sym-lib-table                        # Project Symbol Library mapping table
├── robosen_master.kicad_sym             # Native KiCad symbol library (11 custom symbols)
├── fp-lib-table                         # Project Footprint Library mapping table
├── build_schematic.py                   # Automated Python generator for schematic & symlib
├── erc_report.txt                       # KiCad Electrical Rules Check report (0 violations)
├── TODO.md                              # Hardware & schematic design task checklist
├── README.md                            # Hardware documentation & pinout guide
└── robosen_master.pretty/               # Custom Footprint Library (12 verified .kicad_mod)
    ├── 18650_Battery_Holder_Single.kicad_mod# Keystone 1042 / BK-18650-PC2 Single-Cell Holder
    ├── C_Disc_P2.54mm.kicad_mod             # 100nF Ceramic Disc Capacitor for ADC filtering (2.54mm pitch)
    ├── EPaper_2.13in_Header_1x08.kicad_mod  # 8-Pin SPI header & 71x30mm mechanical outline (4x M2 holes)
    ├── ESP32-S3-DevKitC-1-Socket.kicad_mod   # Dual 22-pin header socket with 6x17.5mm antenna keepout
    ├── KY-040_Rotary_Encoder_Module.kicad_mod# 5-Pin Rotary Encoder Module breakout
    ├── Pogo_4Pin_Dock_2.54mm.kicad_mod      # Config Dock & Run Chain Bus Port
    ├── R_Axial_P10.16mm.kicad_mod           # 1/4W 10.16mm (0.4") Axial Resistors
    ├── SW_Power_2Wire_Pads.kicad_mod        # 2-Wire External Power Switch Solder Pads (1.2mm drill)
    ├── SW_PUSH_12x12mm.kicad_mod            # 12x12mm Tactile Push Button (START & STOP buttons)
    ├── SW_Slide_SS12D00.kicad_mod           # SS12D00 1P2T SPST Power Switch
    ├── TP4056_Type-C_Module.kicad_mod       # USB-C Lithium Charger + BMS Module
    └── TPS63020_BuckBoost_Module.kicad_mod  # 3.3V Synchronous Buck-Boost Regulator
```

---

## 2. Schematic Functional Architecture

The schematic is organized on an **A3 sheet** into 4 functional zones on a strict **1.27 mm (50 mil) grid**:

```
+-----------------------------------------------------------------------------------------+
|                                    A3 SCHEMATIC SHEET                                   |
|                                                                                         |
|  [ ZONE 1: USER INTERFACE ]               [ ZONE 2: CORE MCU ]                          |
|  - Knob 1: KY-040 Action (SW1)            - ESP32-S3 DevKitC-1 (U1)                     |
|  - Knob 2: KY-040 Param (SW2)               * SPI BUS -> EPD Display                    |
|  - Confirm / Start: 12mm Push [Green] (SW3) * UART1   -> Config Dock (J1)               |
|  - Cancel / Stop: 12mm Push [Red] (SW5)     * UART2   -> Run Chain Bus (J2)             |
|  - Display: 2.13" E-Paper Header (DISP1)    * GPIO 8-14, 2 -> Encoders & Dual Buttons   |
|                                             * GPIO 1 (ADC1_CH0) -> Battery Sense Divider|
|                                                                                         |
|                                           [ ZONE 3: DOCKS & BUS PULL-UPS ]              |
|                                           - Config Dock Port (J1)                       |
|                                           - Run Chain Port (J2)                         |
|                                           - R1 / R2: 10k Pull-ups for Open-Drain Chain  |
|                                                                                         |
|                                           [ ZONE 4: POWER & CHARGING ]                  |
|                                           - BT1 (18650 3.7V Li-ion Cell)                |
|                                           - U2 (TP4056 USB-C Charger & Protection)      |
|                                           - SW4 (SS12D00 SPST Power Switch)             |
|                                           - U3 (TPS63020 3.3V Synchronous Buck-Boost)   |
|                                           - R3/R4/C1 (100k Battery Sense Divider + ADC) |
+-----------------------------------------------------------------------------------------+
```

---

## 3. Pre-Wired Net Connections & Pinout Table

| Net Name | Origin Pin | Destination Pin | Description |
|:---|:---|:---|:---|
| **`K1_CLK`** | SW1 Pin 1 (`CLK`) | U1 Pin 12 (`GPIO8`) | Action Knob quadrature phase A |
| **`K1_DT`** | SW1 Pin 2 (`DT`) | U1 Pin 15 (`GPIO9`) | Action Knob quadrature phase B |
| **`K1_SW`** | SW1 Pin 3 (`SW`) | U1 Pin 16 (`GPIO10`) | Action Knob push button switch |
| **`K2_CLK`** | SW2 Pin 1 (`CLK`) | U1 Pin 17 (`GPIO11`) | Parameter Knob quadrature phase A |
| **`K2_DT`** | SW2 Pin 2 (`DT`) | U1 Pin 18 (`GPIO12`) | Parameter Knob quadrature phase B |
| **`K2_SW`** | SW2 Pin 3 (`SW`) | U1 Pin 19 (`GPIO13`) | Parameter Knob push button switch |
| **`BTN_START`**| SW3 Pin 1 (`1`) | U1 Pin 20 (`GPIO14`) | 12mm tactile Confirm / Start / Next button [Green] |
| **`BTN_STOP`** | SW5 Pin 1 (`1`) | U1 Pin 27 (`GPIO2`) | 12mm tactile Cancel / Stop / Back button [Red] |
| **`BATSENSE`** | R3:2, R4:1, C1:1 | U1 Pin 26 (`GPIO1`) | Battery voltage sense divider midpoint (1/2 Vbat) with 100nF filter |
| **`EPD_BUSY`** | DISP1 Pin 1 (`BUSY`) | U1 Pin 4 (`GPIO4`) | E-Paper busy status output |
| **`EPD_CS`** | DISP1 Pin 2 (`CS`) | U1 Pin 7 (`GPIO7`) | E-Paper SPI chip select |
| **`EPD_DC`** | DISP1 Pin 3 (`DC`) | U1 Pin 6 (`GPIO6`) | E-Paper data/command select |
| **`EPD_RES`** | DISP1 Pin 4 (`RES`) | U1 Pin 5 (`GPIO5`) | E-Paper hardware reset |
| **`EPD_MOSI`** | DISP1 Pin 5 (`SDA`) | U1 Pin 32 (`GPIO38`) | SPI MOSI data to display |
| **`EPD_SCK`** | DISP1 Pin 6 (`SCL`) | U1 Pin 40 (`GPIO21`) | SPI clock to display |
| **`CFG_TX`** | U1 Pin 10 (`GPIO17`) | J1 Pin 4 (`PASS`) | Config Dock UART TX output |
| **`CFG_RX`** | U1 Pin 11 (`GPIO18`) | J1 Pin 3 (`DATA`) | Config Dock UART RX input |
| **`CHAIN_TX`** | U1 Pin 8 (`GPIO15`) | J2 Pin 3 (`DATA`), R1 Pin 2 | Command TX to first instruction block |
| **`CHAIN_RX`** | U1 Pin 9 (`GPIO16`) | J2 Pin 4 (`PASS`), R2 Pin 2 | Status RX from last instruction block |
| **`VBAT_RAW`** | BT1 Pin 1 (`+`) | U2 Pin 2 (`B+`) | Raw battery positive terminal |
| **`VBAT_GND`** | BT1 Pin 2 (`-`) | U2 Pin 3 (`B-`) | Raw battery negative terminal |
| **`VBAT_PROT`**| U2 Pin 1 (`OUT+`) | SW4 Pin 1 (`1`) | Protected battery voltage to switch |
| **`VBAT_SW`** | SW4 Pin 2 (`2`) | U3 Pin 3, Pin 4 (`VIN`), R3:1 | Switched battery power into regulator and sense divider |
| **`+3V3`** | U3 Pin 7, Pin 8 (`OUT`) | U1:1, U1:2, SW1:4, SW2:4, DISP1:7, J1:1, J2:1, R1:1, R2:1 | Regulated system power rail |
| **`GND`** | System Common Rail | U1:22,23,43,44, SW1:5, SW2:5, SW3:2, SW5:2, DISP1:8, J1:2, J2:2, U2:4, U3:1,2,5,6, R4:2, C1:2 | System ground rail |

---

## 4. Verified Custom Footprints & Physical Measurements

All 12 custom footprints in `robosen_master.pretty/` have been created and verified against manufacturer mechanical drawings and physical caliper measurements:

### 1. ESP32-S3-DevKitC-1-Socket (`U1`)
- **Format:** Dual 22-pin female header sockets spaced **0.900" (22.86 mm)** row-to-row.
- **Orientation:** Antenna at **TOP**, Dual USB-C ports at **BOTTOM**.
- **Antenna Overhang & RF Keepout:** $17.5\text{ mm} \text{ wide} \times 6.0\text{ mm} \text{ stick-out}$ ($X \in [-8.75, +8.75]$, $Y \in [-35.0, -29.0]$) with a strict all-layer copper keepout zone (`keepout_copper`) under and around the RF antenna region.
- **Pin Numbering:**
  - Left Row: Pads **1 to 22** (Pin 1 `3V3` at top, Pin 22 `GND` at bottom).
  - Right Row: Pads **23 to 44** (Pin 23 `GND` at top, Pin 44 `IO21` at bottom).
  - Strictly aligned with Espressif official DevKitC-1 pinout and physical board silkscreen.

### 2. 2.13" E-Paper Display Module (`DISP1`)
- **Module Physical Boundary:** $71.0\text{ mm} \times 30.0\text{ mm}$ on `F.SilkS` and `F.Fab`.
- **Active Display Area:** $48.55\text{ mm} \times 23.71\text{ mm}$ (2.13" diagonal, $250 \times 122$ pixels) and $59.2\text{ mm} \times 29.2\text{ mm}$ glass outline drawn on `F.Fab`.
- **Mounting Holes:** 4× M2 NPTH holes (Ø $2.2\text{ mm}$) inset $2.5\text{ mm}$ from all four corners ($X = \pm 33.0\text{ mm}$, $Y = \pm 12.5\text{ mm}$).
- **Pin Header:** 1×08 $2.54\text{ mm}$ pitch vertical through-hole header centered on the left edge ($1.5\text{ mm}$ from left edge, $X = -34.0\text{ mm}$, $Y \in [-8.89, +8.89]$).
- **Pinout (Top to Bottom):** `1:BUSY`, `2:CS`, `3:DC`, `4:RES`, `5:SDA`, `6:SCL`, `7:VCC`, `8:GND`.

### 3. TPS63020 3.3V Synchronous Buck-Boost (`U3`)
- **Manufacturer Dimensions:** $26.32\text{ mm} \times 17.51\text{ mm}$ ($1036.19 \times 689.20\text{ mils}$).
- **Horizontal Pin Separation:** $23.78\text{ mm}$ center-to-center ($X = \pm 11.89\text{ mm}$).
- **Vertical Pin Pitch:** $2.54\text{ mm}$ (100 mil) standard header pitch within each corner pair.
- **Hole Diameter:** 1.0 mm drill, 1.8 mm annular ring.
- **Pinout:**
  - Left (IN): Pads 1 & 2 = `GND` (top), Pads 3 & 4 = `VIN` (bottom).
  - Right (OUT): Pads 5 & 6 = `GND` (top), Pads 7 & 8 = `OUT` / +3.3V (bottom).

### 4. TP4056 Type-C Charger & BMS Module (`U2`)
- **Dimensions:** $25.6\text{ mm} \times 17.0\text{ mm}$ ($28.0\text{ mm}$ total depth with Type-C connector overhang).
- **Horizontal Pin Separation:** $21.7\text{ mm}$ center-to-center ($X = \pm 10.85\text{ mm}$).
- **Right Column (Top to Bottom):**
  - Pad 1: `OUT+` (top-right, square mark)
  - Pad 2: `B+` (3.20 mm below Pad 1)
  - Pad 3: `B-` (7.40 mm below Pad 2)
  - Pad 4: `OUT-` (3.20 mm below Pad 3)
- **Left Column:** Pad 6 = `IN+` (top-left), Pad 5 = `IN-` (bottom-left).

### 5. KY-040 Rotary Encoder Breakout Module (`SW1`, `SW2`)
- **Dimensions:** $25.0\text{ mm} \text{ Wide} \times 18.0\text{ mm} \text{ High}$.
- **Mounting Holes:** Dual $3.2\text{ mm}$ NPTH holes spaced $16.0\text{ mm}$ center-to-center ($4.5\text{ mm}$ from left/right edges, $2.5\text{ mm}$ from bottom edge).
- **Pin Header:** 1×05 straight vertical pins on standard $2.54\text{ mm}$ ($0.1''$) breadboard pitch ($2.5\text{ mm}$ from right edge).
- **Pinout (Top to Bottom):**
  - Pad 1: `CLK` (quadrature phase A, $2.0\text{ mm}$ from top edge, square pad)
  - Pad 2: `DT` (quadrature phase B, $2.54\text{ mm}$ pitch)
  - Pad 3: `SW` (tactile push button switch, $2.54\text{ mm}$ pitch)
  - Pad 4: `+` (+3.3V power, $2.54\text{ mm}$ pitch)
  - Pad 5: `GND` (ground return, $2.54\text{ mm}$ pitch)
- **Knob Shaft:** Center at $10.0\text{ mm}$ from left edge ($X = -2.50\text{ mm}$, $Y = -1.92\text{ mm}$ from module center), $6.0\text{ mm}$ D-shaft outline.

### 6. 2-Wire External Power Switch Solder Pads (`SW4`)
- **Format:** 1×02 through-hole solder pads with a **1-hole gap ($5.08\text{ mm} / 0.2''$ pitch)** for easy wire soldering and heatshrink clearance without bridging.
- **Drill & Pad:** $1.2\text{ mm}$ drill with generous $2.4\text{ mm}$ annular ring (accommodates 20–26 AWG stranded hookup wire or standard headers).
- **Pinout:**
  - Pad 1 (`IN`): Square pad at $(-2.54\text{ mm}, 0)$, connects to `VBAT_PROT` (protected battery positive from TP4056 `OUT+`).
  - Pad 2 (`SW`): Round pad at $(+2.54\text{ mm}, 0)$, connects to `VBAT_SW` (switched power feeding TPS63020 `VIN` and divider `R3`).

### 7. 18650 Single-Cell Battery Holder (`BT1`)
- **Dimensions:** $77.5\text{ mm} \text{ Long} \times 20.5\text{ mm} \text{ Wide}$.
- **Mounting Holes:** Dual $3.2\text{ mm}$ NPTH holes spaced $55.5\text{ mm}$ center-to-center along horizontal centerline ($11.0\text{ mm}$ from left and right edges).
- **Wire Solder Pads:** Placed outside the holder ends for direct wire soldering without pinching leads:
  - Pad 1 (`+` / `BAT+`): Square pad at Left ($X = -41.5\text{ mm}, Y = 0$), $1.2\text{ mm}$ drill, connects to `VBAT_RAW` (feeds TP4056 `B+`).
  - Pad 2 (`-` / `BAT-`): Round pad at Right ($X = +41.5\text{ mm}, Y = 0$), $1.2\text{ mm}$ drill, connects to `VBAT_GND` (feeds TP4056 `B-`).

### 8. 12×12mm Tactile Push Buttons (`SW3`, `SW5`)
- **Format:** Standard 4-pin DIP tactile momentary switch ($12.0\text{ mm} \times 12.0\text{ mm}$ body, $5.0\text{ mm}$ round actuator).
- **Pin Spacing:** $12.5\text{ mm} \times 5.0\text{ mm}$ diagonal through-hole pins.
- **Roles:**
  - `SW3`: Confirm / Next / Start button [Green cap] (`BTN_START`, `GPIO14`).
  - `SW5`: Cancel / Stop / Back button [Red cap] (`BTN_STOP`, `GPIO2`).

### 9. Config Dock & Run Chain Bus Ports (`J1`, `J2`)
- **Format:** 1×04 vertical through-hole header on standard $2.54\text{ mm}$ ($0.1''$) pitch.
- **Drill & Pad:** $1.1\text{ mm}$ drill with $2.0\text{ mm}$ annular ring.
- **Pinout (1 to 4):**
  - Pin 1: `+3V3`
  - Pin 2: `GND`
  - Pin 3: `DATA` (`CFG_RX` on J1, `CHAIN_TX` on J2)
  - Pin 4: `PASS` (`CFG_TX` on J1, `CHAIN_RX` on J2)

### 10. Axial Resistors (`R1`, `R2`, `R3`, `R4`)
- **Format:** Standard 1/4W axial through-hole resistor with $10.16\text{ mm}$ ($0.4''$) lead pitch (`R_Axial_P10.16mm`).
- **Values & Usage:**
  - `R1`, `R2`: $10\text{ k}\Omega$ pull-ups to `+3V3` for the open-drain bidirectional bus lines.
  - `R3`, `R4`: $100\text{ k}\Omega$ (1% precision) voltage divider resistors for battery monitoring.

### 11. Ceramic Disc Capacitor (`C1`)
- **Format:** Standard radial ceramic disc capacitor with $2.54\text{ mm}$ ($0.1''$) lead pitch (`C_Disc_P2.54mm`).
- **Value & Usage:** $100\text{ nF}$ (0.1 $\mu$F) noise filtering and ADC sample stabilization across `BATSENSE` to `GND`.

### 12. SS12D00 Slide Switch (`SW4` Alternative)
- **Format:** SS12D00 1P2T SPST slide switch footprint ($8.5\text{ mm} \times 4.3\text{ mm}$ body, $2.0\text{ mm}$ travel).
- **Lead Pitch:** $3\times 1$ pins on $2.0\text{ mm}$ pitch.

---

## 5. How to Open and Review in KiCad

1. Launch **KiCad 10** (or KiCad 8/9).
2. Open Project:
   ```
   hardware/master_block/robosen_master_block.kicad_pro
   ```
3. Double-click **`robosen_master_block.kicad_sch`** to open the schematic.
4. Run Electrical Rules Check (**Tools → Electrical Rules Check**):
   - Status: **0 errors, 0 warnings** (`Found 0 violations`).
5. Open PCB Editor (**`robosen_master_block.kicad_pcb`**):
   - All 21 footprints are placed, 100% routed, and verified with **0 unconnected items**.
   - Press **`Alt + 3`** to inspect the complete 3D assembly.

---

## 6. PCB Routing Architecture & Power Planes

- **Board Dimensions:** $115.50\text{ mm} \times 62.00\text{ mm}$ (2 Layers, $1.6\text{ mm}$ FR-4).
- **Power Planes (`GND`):** Both `F.Cu` and `B.Cu` are flooded with continuous copper `GND` planes with standard thermal relief spokes (`0.4 mm` spoke, `0.3 mm` gap) and automatic isolated island removal.
- **Power Rails:** `+3V3`, `/VBAT_SW`, `/VBAT_PROT`, `/VBAT_RAW`, and `/VBAT_GND` are routed with **$0.80\text{ mm}$ wide traces** (supporting $> 1.5\text{ A}$ continuous load) and $1.0\text{ mm} / 0.5\text{ mm}$ power vias.
- **Battery Protection Isolation:** `/VBAT_GND` connects exclusively between `BT1` Pad 2 (`BAT-`) and `U2` Pad 3 (`B-`), maintaining strict $> 0.25\text{ mm}$ physical separation from system `GND` to preserve TP4056 under-voltage/over-current protection.
- **Signals:** Display SPI, UART ports, encoders, and buttons are routed with $0.25\text{ mm}$ signal traces and $0.6\text{ mm} / 0.3\text{ mm}$ vias.
- **Antenna Keepout:** Zero copper traces, vias, or ground flood enter the $17.5\text{ mm} \times 6.0\text{ mm}$ ESP32 antenna exclusion zone.
- **Mounting Hole Clearance:** All copper traces and vias maintain $\ge 3.68\text{ mm}$ radial clearance from `H1`–`H4` centers, safely clearing standard M3 screw heads ($R \le 2.85\text{ mm}$) and 3D print standoff bosses ($R \le 3.50\text{ mm}$).

---

## 7. PCB Manufacturing & Fabrication Files

The fabrication outputs have been exported using `kicad-cli` and packaged for direct 1-click upload to board manufacturers (JLCPCB, PCBWay, OSHPark):

- **Production ZIP Archive:** [`robosen_master_block_gerbers.zip`](robosen_master_block_gerbers.zip)
- **Directory:** [`hardware/master_block/gerbers/`](gerbers/)
  - `robosen_master_block-F_Cu.gtl` (Top Copper Layer)
  - `robosen_master_block-B_Cu.gbl` (Bottom Copper Layer)
  - `robosen_master_block-F_Mask.gts` (Top Solder Mask)
  - `robosen_master_block-B_Mask.gbs` (Bottom Solder Mask)
  - `robosen_master_block-F_Silkscreen.gto` (Top Silkscreen)
  - `robosen_master_block-B_Silkscreen.gbo` (Bottom Silkscreen)
  - `robosen_master_block-Edge_Cuts.gm1` (Board Outline & Routing Profile)
  - `robosen_master_block-PTH.drl` (Plated Through-Hole Drill Hits)
  - `robosen_master_block-NPTH.drl` (Non-Plated Through-Hole Drill Hits: M3 holes & module holes)
  - `robosen_master_block-drl.rpt` (Drill Hole Size & Count Report)

### Manufacturer Order Parameters (JLCPCB / PCBWay)
- **Base Material:** FR-4 Standard ($T_g \ge 130^\circ\text{C}$)
- **Layer Count:** 2 Layers
- **Dimensions:** $115.50\text{ mm} \times 62.00\text{ mm}$
- **PCB Thickness:** $1.6\text{ mm}$
- **Finished Copper:** $1\text{ oz}$ ($35\ \mu\text{m}$)
- **Solder Mask:** Matte Green (or Matte Black)
- **Silkscreen:** White
- **Surface Finish:** Lead-Free HASL or ENIG

---

## 8. Assembly & Prototyping Notes

1. **Through-Hole Leads Under Battery Holder (`BT1`):**  
   12 through-hole pins sit directly under the plastic body of the 18650 holder (`U2` pads 1–4, `U3` pads 5–8, `SW3` pad 1, `SW5` pad 2).  
   *Action:* Clip all leads completely flush on the bottom side after soldering, and place a **$1.0\text{ mm} - 1.5\text{ mm}$ piece of EVA foam tape** under `BT1` to absorb solder joint fillet height.
2. **Mounting Fasteners (`H1`–`H4`):**  
   Use non-conductive nylon washers or nylon screws/standoffs to eliminate any friction or abrasion against the solder mask.
3. **Bluetooth Range:**  
   The e-paper display sits physically above the ESP32 antenna on the opposite side. Test BLE wireless connectivity through your assembled 3D casing to ensure signal range meets your needs.
