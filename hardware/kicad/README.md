# Robosen K1 Master Block — KiCad 10 Hardware Project

> **Project:** Custom Carrier Motherboard PCB for Robosen K1 Tangible Coding Block  
> **KiCad Version:** KiCad 10.0.6 (Fully compatible with KiCad 8.x / 9.x / 10.x)  
> **Workspace Directory:** `hardware/kicad/`  
> **Schematic Status:** Fully pre-wired, verified with KiCad ERC (**0 violations**)  
> **Author:** Nantaphat Yoktaworn / Antigravity AI  

---

## 1. Project Directory Structure

```
hardware/kicad/
├── robosen_master_block.kicad_pro       # KiCad Master Project configuration
├── robosen_master_block.kicad_sch       # Complete pre-wired Starter Schematic (A3 format)
├── robosen_master_block.kicad_prl       # KiCad Project local settings
├── robosen_master_block.net             # Exported netlist (kicadsexpr format)
├── robosen_master_block_schematic.pdf   # High-resolution vector PDF export of schematic
├── schematic_svg/
│   └── robosen_master_block.svg         # Vector SVG render of schematic
├── sym-lib-table                        # Project Symbol Library mapping table
├── robosen_master.kicad_sym             # Native KiCad symbol library (10 custom symbols)
├── fp-lib-table                         # Project Footprint Library mapping table
├── build_schematic.py                   # Automated Python generator for schematic & symlib
├── erc_report.txt                       # KiCad Electrical Rules Check report (0 violations)
├── README.md                            # Hardware documentation & pinout guide
└── robosen_master.pretty/               # Custom Footprint Library (10 verified .kicad_mod)
    ├── ESP32-S3-DevKitC-1-Socket.kicad_mod   # Dual 22-pin header socket (0.9" row span)
    ├── TP4056_Type-C_Module.kicad_mod       # USB-C Lithium Charger + BMS Module
    ├── TPS63020_BuckBoost_Module.kicad_mod  # 3.3V Synchronous Buck-Boost Regulator
    ├── 18650_Battery_Holder_Single.kicad_mod# Keystone 1042 / BK-18650-PC2 Single-Cell Holder
    ├── KY-040_Rotary_Encoder_Module.kicad_mod# 5-Pin Rotary Encoder Module breakout
    ├── EPaper_2.13in_Header_1x08.kicad_mod  # 8-Pin SPI header for DEPG0213BN / SSD1680
    ├── Pogo_4Pin_Dock_2.54mm.kicad_mod      # Config Dock & Run Chain Bus Port
    ├── SW_PUSH_12x12mm.kicad_mod            # 12x12mm Tactile Push Button (START_BUTTON)
    ├── SW_Slide_SS12D00.kicad_mod           # SS12D00 1P2T SPST Power Switch
    └── R_Axial_P10.16mm.kicad_mod           # 1/4W 10.16mm (0.4") Axial Resistors
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
|  - Start Button: 12mm Push (SW3)            * UART1   -> Config Dock (J1)               |
|  - Display: 2.13" E-Paper Header (DISP1)    * UART2   -> Run Chain Bus (J2)             |
|                                             * GPIO 8-14 -> Encoders & Button            |
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
| **`BTN_START`** | SW3 Pin 1 (`1`) | U1 Pin 20 (`GPIO14`) | 12mm tactile execute/start button |
| **`EPD_BUSY`** | DISP1 Pin 8 (`BUSY`) | U1 Pin 4 (`GPIO4`) | E-Paper busy status output |
| **`EPD_RES`** | DISP1 Pin 7 (`RES`) | U1 Pin 5 (`GPIO5`) | E-Paper hardware reset |
| **`EPD_DC`** | DISP1 Pin 6 (`D/C`) | U1 Pin 6 (`GPIO6`) | E-Paper data/command select |
| **`EPD_CS`** | DISP1 Pin 5 (`CS`) | U1 Pin 7 (`GPIO7`) | E-Paper SPI chip select |
| **`EPD_SCK`** | DISP1 Pin 4 (`SCLK`) | U1 Pin 40 (`GPIO21`) | SPI clock to display |
| **`EPD_MOSI`** | DISP1 Pin 3 (`SDI`) | U1 Pin 32 (`GPIO38`) | SPI MOSI data to display |
| **`CFG_TX`** | U1 Pin 10 (`GPIO17`) | J1 Pin 4 (`PASS`) | Config Dock UART TX output |
| **`CFG_RX`** | U1 Pin 11 (`GPIO18`) | J1 Pin 3 (`DATA`) | Config Dock UART RX input |
| **`CHAIN_TX`** | U1 Pin 8 (`GPIO15`) | J2 Pin 3 (`DATA`), R1 Pin 2 | Command TX to first instruction block |
| **`CHAIN_RX`** | U1 Pin 9 (`GPIO16`) | J2 Pin 4 (`PASS`), R2 Pin 2 | Status RX from last instruction block |
| **`VBAT_RAW`** | BT1 Pin 1 (`+`) | U2 Pin 1 (`B+`) | Raw battery positive terminal |
| **`VBAT_GND`** | BT1 Pin 2 (`-`) | U2 Pin 2 (`B-`) | Raw battery negative terminal |
| **`VBAT_PROT`** | U2 Pin 3 (`OUT+`) | SW4 Pin 1 (`1`) | Protected battery voltage to switch |
| **`VBAT_SW`** | SW4 Pin 2 (`2`) | U3 Pin 3 (`VIN`), Pin 4 (`EN`) | Switched battery power into regulator |
| **`+3V3`** | U3 Pin 1 (`VOUT`) | U1:1, U1:2, SW1:4, SW2:4, DISP1:1, J1:1, J2:1, R1:1, R2:1 | Regulated system power rail |
| **`GND`** | System Common Rail | U1:22,23,43,44, SW1:5, SW2:5, SW3:2, DISP1:2, J1:2, J2:2, U2:4, U3:2, U3:5 | System ground rail |

---

## 4. How to Open and Review in KiCad

1. Launch **KiCad 10**.
2. Open Project:
   ```
   C:\Users\nnnn\Projects\robosen_block\hardware\kicad\robosen_master_block.kicad_pro
   ```
3. Double-click **`robosen_master_block.kicad_sch`** to open the schematic.
4. Run Electrical Rules Check (**Tools → Electrical Rules Check**):
   - Status: **0 errors, 0 warnings**.
5. To update PCB from schematic:
   - Click **Tools → Update PCB from Schematic** (`F8`).
   - All 13 component footprints will appear ready for placement on your carrier board PCB outline!
