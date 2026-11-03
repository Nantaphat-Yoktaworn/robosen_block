# 📘 Prototype #1: First Custom PCB Engineering Specification & Production Release

> **Project:** Tangible Modular Physical Block Coding System for Robosen K1 Humanoid Robot  
> **Iteration:** Prototype #1 (First Custom PCB Production Release) & Prototype #1-1 ECO Respin  
> **Document Purpose:** Complete technical specification, PCB design files, electrical schematics, bill of materials, pre-order audit verification, and assembly guidelines.  
> **Author:** Nantaphat Yoktaworn  
> **Date:** October 5, 2026 (Respun October 14, 2026)  
> **Status:** **PROTOTYPE #1-1 VERIFIED & ACTIVE IN HARDWARE REPO**  
> **Repository:** `https://github.com/Nantaphat-Yoktaworn/robosen_block.git`

---

## 1. Executive Summary: Evolution from Prototype #0 to Prototype #1

| Metric / Feature | **Prototype #0 (Breadboard)** | **Prototype #1 / #1-1 (Custom Carrier PCB)** |
| :--- | :--- | :--- |
| **Physical Construction** | 5× MB-102 solderless breadboards & Dupont jumper wires | Custom 2-layer FR-4 carrier PCBs ($1.6\text{ mm}$, 1 oz Cu) |
| **Form Factor** | Bulky desktop breadboard array ($>400\text{ mm}$ width) | **$32 \times 32\text{ mm}$** modular Action Blocks; **$115.5 \times 62.0\text{ mm}$** Master Block |
| **Inter-Block Coupling** | Manual M-M jumper wire daisy chaining | **4-Pin Magnetic Pogo Connectors (2.54 mm)** with centered flush alignment |
| **Power Management** | USB-C cable tethered to PC / bench power supply | **Self-contained 18650 Li-ion battery** with TP4056 BMS + TPS63020 Buck-Boost |
| **Display Interface** | 2.13" E-Paper display (SPI) | **2.13" E-Paper display (SPI, DEPG0213BN / SSD1680)**, sunlight-readable, partial refresh |
| **Master UI Inputs** | 2 Rotary Encoders + 1 Button (Breadboard) | **4 UI Inputs**: 2 Rotary Encoders (`SW1`, `SW2`) + Green Start (`SW3`) + Red Stop/E-Stop (`SW5`) |
| **Battery Monitoring** | External DMM / Bench supply | **BATSENSE (ADC1_CH0 / GPIO 1)**: 100k/100k divider + 100nF filter for live battery % |
| **Block MCU Platform** | CH32V003F4P6 breakout on breadboard | Dedicated 2×11 DIP socketed CH32V003F4P6 with SWIO programming port |
| **End Block Solution** | Separate dedicated breadboard or external wire loop | **Software-configurable via MCU Pin 15 (`PD0`)** on unified Action Block PCB (Token `0xEE`) |
| **Manufacturing State** | Lab bench wire-up | **Production Gerbers verified & ordered at JLCPCB** (Dual-Agent audited) |

---

## 2. Hardware Architecture & Board Designs

Prototype #1 consists of two distinct PCB designs engineered in KiCad 10:

### 2.1 Master Controller Board ([`hardware/master_block/`](file:///Users/nnnn/Projects/robosen_block/hardware/master_block/))
* **Dimensions:** $115.5\text{ mm} \times 62.0\text{ mm}$ rectangular form factor.
* **Core Controller:** Socketed **ESP32-S3-DevKitC-1-N16R8** (Xtensa 32-bit dual-core @ 240 MHz, 16 MB Flash, 8 MB Octal PSRAM).
  * *Note on Socket Spacing:* Initial Prototype #1 had a 22.86 mm row spacing defect; Prototype #1-1 corrected row spacing to exact **25.40 mm (1.000")**, now active in `hardware/master_block/`. The retired defective board is archived in [`archive/prototype_1_0_retired/master_block/`](file:///Users/nnnn/Projects/robosen_block/archive/prototype_1_0_retired/master_block/).
* **Power Subsystem:**
  * Single 18650 Li-ion cell (onboard through-hole battery clips `BT1`).
  * **TP4056 Type-C Charging Module** (`MOD1`) with integrated DW01A battery management system (over-charge, over-discharge, over-current protection).
  * **TPS63020 Buck-Boost Module** (`MOD2`): Converts varying battery voltage ($3.0\text{V} - 4.2\text{V}$) into a rock-solid **$3.30\text{V}$ rail** (up to 2.0A peak current).
  * Dedicated SS12D00 slide power switch (`SW4`) or 2-pin auxiliary power wiring pads.
  * Isolated `/VBAT_GND` return path to prevent ground-loop bypass of BMS safety MOSFETs.
  * Precision 1:1 voltage divider (`R3 = 100k\Omega`, `R4 = 100k\Omega`, `C1 = 100nF`) on `GPIO 1` (`BATSENSE`).
* **User Interface (4 Inputs + Display):**
  * **2.13" E-Paper SPI Display** (`DISP1`): DEPG0213BN / SSD1680 (122×250, 1×08 2.54mm Header).
  * **2× KY-040 / EC11 Rotary Encoders**: Tactile detents & push click (`SW1` Knob 1 = Action, `SW2` Knob 2 = Parameter).
  * **Green 12×12 mm Push Button** (`SW3`, `GPIO 14`): Master Start / Confirm / Teacher Pairing trigger.
  * **Red 12×12 mm Push Button** (`SW5`, `GPIO 2`): Emergency Stop / Abort Run / Cancel / Disconnect.
  * **Status RGB LED**: Built-in WS2812 on `GPIO 48`.
* **Docking Interfaces:**
  * **Config Dock (`J1`)**: 4-pin magnetic pogo port (`CFG_TX` GPIO 17, `CFG_RX` GPIO 18 @ 115200 baud).
  * **Run Port (`J2`)**: 4-pin magnetic pogo port (`CHAIN_TX` GPIO 15, `CHAIN_RX` GPIO 16 @ 115200 baud).
* **Mechanical Mounting:** 4× M3 plated mounting holes (`H1`–`H4`) with $\ge 3.68\text{ mm}$ clearance around every hole.

### 2.2 Tangible Action Block Board ([`hardware/action_block/`](file:///Users/nnnn/Projects/robosen_block/hardware/action_block/))
* **Dimensions:** **$32.0\text{ mm} \times 32.0\text{ mm}$** square carrier board.
* **Core Controller:** Socketed **TENSTAR CH32V003F4P6** 2×11 DIP module (32-bit QingKe RISC-V @ 24 MHz, 16 KB Flash, 2 KB SRAM).
* **Modular Pogo Interfaces:**
  * **Upstream Dock (`IN`)**: 4-pin 2.54 mm pogo receptacle, **vertically centered at $Y = 72.50\text{ mm}$**.
  * **Downstream Dock (`OUT`)**: 4-pin 2.54 mm pogo pin header, **vertically centered at $Y = 72.50\text{ mm}$**.
  * Exact vertical centering ensures collinear, flush alignment when chaining arbitrary numbers of blocks together.
* **Visual Light Language:** 3-pin 2.54 mm header for pre-soldered **WS2812 RGB LED module** (Top-to-Bottom: `GND`, `VCC`, `IN`).
* **Noise Suppression:** 100 nF (`104`) ceramic disc decoupling capacitor adjacent to MCU `VDD` and `GND`.
* **In-System Programming:** 3-pin 2.54 mm header (`PROG`: `GND`, `3V3`, `SWIO`) for 1-wire firmware flashing with `minichlink`.
* **Dynamic Role Support (End Block Configurable):**
  * MCU Pin 15 (`PD0`) is routed via a 0.40 mm `B.Cu` trace directly to Net `/RETURN_BUS` (Pin 4).
  * In **Action Block Mode**: `PD0` is set to High-Z floating input (`GPIO_CFGLR_IN_FLOAT`) to preserve passive pass-through.
  * In **End Block Mode (`0xEE`)**: `PD0` is configured as active push-pull TX to loop the `0xAA` discovery frame back to the Master along `/RETURN_BUS`.
  * **Result:** Single unified PCB layout manufactured for all modular blocks!

---

## 3. Prototype #1 Bill of Materials (BOM)

### Master Controller Unit
| # | Component | Package / Footprint | Designator | Qty | Role / Purpose |
| :-: | :--- | :--- | :--- | :-: | :--- |
| 1 | ESP32-S3-DevKitC-1 | 2×22 2.54mm Socket (25.40mm row) | `U1` | 1 | Master CPU, BLE 5.0 gateway, E-Paper & UI coordinator |
| 2 | 2.13" E-Paper SPI Display | 1×08 2.54mm Header | `DISP1` | 1 | 122×250 DEPG0213BN / SSD1680 e-paper display |
| 3 | EC11 Rotary Encoder | 5-Pin Module / KY-040 | `SW1`, `SW2` | 2 | Knob 1 (Action selector), Knob 2 (Parameter adjuster) |
| 4 | Tactile Switch 12×12mm | 4-Pin THT | `SW3` | 1 | Master Start / Confirm button (Green cap) |
| 5 | Tactile Switch 12×12mm | 4-Pin THT | `SW5` | 1 | Master Stop / Cancel / E-Stop button (Red cap) |
| 6 | Slide Switch SS12D00 | 1×03 THT / 2-Pin pads | `SW4` | 1 | System power switch |
| 7 | TP4056 Type-C Module | 1×04 SMT Module Pads | `MOD1` | 1 | 1A Li-ion charger with DW01A BMS protection |
| 8 | TPS63020 Module | 1×06 SMT Module Pads | `MOD2` | 1 | High-efficiency buck-boost regulator ($3.30\text{V}$ output) |
| 9 | 18650 Battery Holder | Single Cell Through-Hole | `BT1` | 1 | 3.7V 2600–3500 mAh rechargeable Li-ion power |
| 10 | Pogo 4-Pin Dock | 1×04 2.54mm THT | `J1`, `J2` | 2 | Upstream Config Dock (`J1`) & Run Port (`J2`) |
| 11 | Metal Film Resistors 100kΩ | Axial P10.16mm (1% precision) | `R3`, `R4` | 2 | Battery voltage divider for ADC sensing |
| 12 | Metal Film Resistors 10kΩ | Axial P10.16mm | `R1`, `R2` | 2 | Run Chain open-drain bus pull-ups |
| 13 | Ceramic Disc Cap 100nF | Radial P2.54mm | `C1` | 1 | ADC battery sample stabilization filter |

### Modular Action Block Unit (Per Block)
| # | Component | Package / Footprint | Designator | Qty | Role / Purpose |
| :-: | :--- | :--- | :--- | :-: | :--- |
| 1 | TENSTAR CH32V003F4P6 | 2×11 2.54mm DIP Socket | `MCU` | 1 | RISC-V 24MHz slave processor & non-volatile storage |
| 2 | WS2812B RGB Module | 1×03 2.54mm Header | `RGB` | 1 | Color feedback (`GND`, `+3V3`, `DIN`) |
| 3 | Ceramic Cap 100nF | Radial P2.54mm | `C104` | 1 | MCU supply decoupling capacitor |
| 4 | Pogo 4-Pin Dock | 1×04 2.54mm THT | `IN`, `OUT` | 2 | Upstream input & Downstream output docks |
| 5 | Programming Header | 1×03 2.54mm Header | `PROG` | 1 | SWIO debug / factory flash header |

---

## 4. Pinout & Electrical Interconnect Matrix

### 4.1 Master Block Pinout (`robosen_master_block`)

| ESP32-S3 Pin | Net Name | Hardware Destination | Signal Description | Mode |
| :--- | :--- | :--- | :--- | :--- |
| **`GPIO 1`** | `BATSENSE` | R3:2, R4:1, C1:1 | Battery Voltage Divider (100k/100k) | ADC1_CH0 Analog Input |
| **`GPIO 2`** | `BTN_STOP` | SW5 Pin 1 (Red Button) | Cancel / Emergency Halt / Back | Digital In (Pull-up) |
| **`GPIO 4`** | `EPD_BUSY` | DISP1 Pin 1 (`BUSY`) | E-Paper Busy Status Flag | Digital Input |
| **`GPIO 5`** | `EPD_RES` | DISP1 Pin 4 (`RES`) | E-Paper Hardware Reset | Digital Output |
| **`GPIO 6`** | `EPD_DC` | DISP1 Pin 3 (`DC`) | E-Paper Data / Command Select | Digital Output |
| **`GPIO 7`** | `EPD_CS` | DISP1 Pin 2 (`CS`) | E-Paper SPI Chip Select | Digital Output |
| **`GPIO 8`** | `K1_CLK` | SW1 Pin 1 (`CLK`) | Action Knob Quadrature Phase A | Interrupt (Falling) |
| **`GPIO 9`** | `K1_DT` | SW1 Pin 2 (`DT`) | Action Knob Quadrature Phase B | Digital In (Pull-up) |
| **`GPIO 10`** | `K1_SW` | SW1 Pin 3 (`SW`) | Action Knob Push Switch Click | Digital In (Pull-up) |
| **`GPIO 11`** | `K2_CLK` | SW2 Pin 1 (`CLK`) | Parameter Knob Quadrature Phase A | Interrupt (Falling) |
| **`GPIO 12`** | `K2_DT` | SW2 Pin 2 (`DT`) | Parameter Knob Quadrature Phase B | Digital In (Pull-up) |
| **`GPIO 13`** | `K2_SW` | SW2 Pin 3 (`SW`) | Parameter Knob Push Switch Click | Digital In (Pull-up) |
| **`GPIO 14`** | `BTN_START` | SW3 Pin 1 (Green Button) | Master Start / Confirm / Teacher Scan | Digital In (Pull-up) |
| **`GPIO 15`** | `CHAIN_TX` | J2 Pin 3 (`DATA`) | Run Chain Downstream Serial TX | UART2 TX (115200) |
| **`GPIO 16`** | `CHAIN_RX` | J2 Pin 4 (`PASS`) | Run Chain Return Rail Serial RX | UART2 RX (115200) |
| **`GPIO 17`** | `CFG_TX` | J1 Pin 4 (`PASS`) | Config Dock Serial TX (to Block RX) | UART1 TX (115200) |
| **`GPIO 18`** | `CFG_RX` | J1 Pin 3 (`DATA`) | Config Dock Serial RX (from Block TX) | UART1 RX (115200) |
| **`GPIO 21`** | `EPD_SCK` | DISP1 Pin 6 (`SCL`) | E-Paper SPI Clock | SPI SCK |
| **`GPIO 38`** | `EPD_MOSI` | DISP1 Pin 5 (`SDA`) | E-Paper SPI Master Out | SPI MOSI |
| **`GPIO 48`** | `RGB_BUILTIN` | Internal Onboard LED | Status RGB Indicator | Addressable NeoPixel |

### 4.2 Action Block Pinout (`action_block`)

| Pin | Net Name | Connected To | Signal Description |
| :--- | :--- | :--- | :--- |
| `IN-1` | `+3V3` | Power Rail | Upstream 3.3V power input |
| `IN-2` | `GND` | Ground Plane | System ground reference |
| `IN-3` | `/RX_IN` | MCU Pin 8 (`PD6/RX`) | Incoming point-to-point UART data |
| `IN-4` | `/RETURN_BUS`| MCU Pin 15 (`PD0`) & `OUT-4` | Return bus pass-through / Active loopback driver |
| `OUT-1`| `+3V3` | Power Rail | Downstream 3.3V power output |
| `OUT-2`| `GND` | Ground Plane | System ground reference |
| `OUT-3`| `/TX_OUT` | MCU Pin 9 (`PD5/TX`) | Outgoing point-to-point UART data to next block |
| `OUT-4`| `/RETURN_BUS`| `IN-4` & MCU Pin 15 | Return rail passing back upstream |
| `RGB-3`| `/LED_DIN` | MCU Pin 6 (`PA2`) | WS2812 800 kHz serial pixel driver |
| `PROG-3`| `/SWIO` | MCU Pin 16 (`PD1/SWIO`)| 1-wire programming line |

---

## 5. Manufacturing Specifications (JLCPCB Release)

| Parameter | Master Controller PCB | Action Block PCB | Notes / JLCPCB Selection |
| :--- | :--- | :--- | :--- |
| **Board Dimensions** | $115.5\text{ mm} \times 62.0\text{ mm}$ | $32.0\text{ mm} \times 32.0\text{ mm}$ | Standard rectangular outlines |
| **Layer Count** | 2 Layers (`F.Cu`, `B.Cu`) | 2 Layers (`F.Cu`, `B.Cu`) | Dual-layer continuous GND planes |
| **Board Thickness** | $1.6\text{ mm}$ FR-4 | $1.6\text{ mm}$ FR-4 | Standard rigidity |
| **Copper Weight** | 1 oz ($35\text{ }\mu\text{m}$) | 1 oz ($35\text{ }\mu\text{m}$) | Handles up to 2.0A continuous |
| **Surface Finish** | Lead-Free HASL | Lead-Free HASL | RoHS compliant, child-safe |
| **Min Track Width** | $0.25\text{ mm}$ (Signal) / $0.80\text{ mm}$ (Power) | $0.30\text{ mm}$ (Signal) / $0.60\text{ mm}$ (Power) | Easily manufactured |
| **Min Clearance** | $\ge 0.25\text{ mm}$ | $\ge 0.25\text{ mm}$ | 100% DRC verified |
| **Production ZIP** | [`hardware/master_block/robosen_master_block_gerbers.zip`](file:///Users/nnnn/Projects/robosen_block/hardware/master_block/robosen_master_block_gerbers.zip) | [`hardware/action_block/robosen_action_block_gerbers.zip`](file:///Users/nnnn/Projects/robosen_block/hardware/action_block/robosen_action_block_gerbers.zip) | Verified fabrication packages |

---

## 6. Pre-Order Dual-Agent Audit Verification

Before submitting fabrication files to JLCPCB, independent dual-agent verification was conducted by **Antigravity** and **Codex Astra** (`gpt-6-astra`):

1. **Geometry & Placement Invariants:**
   - Master Block: 4× M3 mounting holes verified with $>3.68\text{ mm}$ copper clearance to drill edges.
   - Action Block: Collinear vertical centering of `IN` and `OUT` docks verified at $Y = 72.50\text{ mm}$.
2. **KiCad DRC Verification:**
   - Master Block: **0 unconnected items, 0 copper clearance errors**.
   - Action Block: **0 unconnected items, 0 copper clearance errors**.
3. **Netlist & Thermal Relief Parity:**
   - 100% netlist matching between schematics and routed PCBs.
   - Dual-layer continuous GND power planes with thermal spokes and automatic island removal verified.
