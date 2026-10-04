# 📘 Prototype #1: First Custom PCB Engineering Specification & Production Release

> **Project:** Tangible Modular Physical Block Coding System for Robosen K1 Humanoid Robot  
> **Iteration:** Prototype #1 (First Custom PCB Production Release)  
> **Document Purpose:** Complete technical specification, PCB design files, electrical schematics, bill of materials, pre-order audit verification, and assembly guidelines.  
> **Author:** Nantaphat Yoktaworn  
> **Date:** October 5, 2026  
> **Status:** **ORDERED AT JLCPCB** (October 5, 2026)  
> **Repository:** `https://github.com/Nantaphat-Yoktaworn/robosen_block.git`

---

## 1. Executive Summary: Evolution from Prototype #0 to Prototype #1

| Metric / Feature | **Prototype #0 (Breadboard)** | **Prototype #1 (Custom PCB)** |
| :--- | :--- | :--- |
| **Physical Construction** | 5× MB-102 solderless breadboards & Dupont jumper wires | Custom 2-layer FR-4 carrier PCBs ($1.6\text{ mm}$, 1 oz Cu) |
| **Form Factor** | Bulky desktop breadboard array ($>400\text{ mm}$ width) | **$32 \times 32\text{ mm}$** modular Action Blocks; **$120 \times 65\text{ mm}$** Master Block |
| **Inter-Block Coupling** | Manual M-M jumper wire daisy chaining | **4-Pin Magnetic Pogo Connectors (2.54 mm)** with centered flush alignment |
| **Power Management** | USB-C cable tethered to PC / bench power supply | **Self-contained 18650 Li-ion battery** with TP4056 BMS + TPS63020 Buck-Boost |
| **Display Interface** | 2.13" E-Paper display (SPI) | 0.96" SSD1306 I2C OLED (fast 60 FPS refresh, crisp status icons) |
| **Block MCU Platform** | CH32V003F4P6 breakout on breadboard | Dedicated 2×11 DIP socketed CH32V003F4P6 with SWIO programming port |
| **End Block Solution** | Separate dedicated breadboard or external wire loop | **Software-configurable via MCU Pin 15 (`PD0`)** on unified Action Block PCB |
| **Manufacturing State** | Lab bench wire-up | **Production Gerbers released to JLCPCB** (Dual-Agent audited) |

---

## 2. Hardware Architecture & Board Designs

Prototype #1 consists of two distinct PCB designs engineered in KiCad 10:

### 2.1 Master Controller Board (`hardware/master_block/`)
* **Dimensions:** $120.0\text{ mm} \times 65.0\text{ mm}$ rectangular form factor.
* **Core Controller:** Socketed **ESP32-S3-DevKitC-1-N16R8** (Xtensa 32-bit dual-core @ 240 MHz, 16 MB Flash, 8 MB Octal PSRAM).
* **Power Subsystem:**
  * Single 18650 Li-ion cell (onboard through-hole battery clips).
  * **TP4056 Type-C Charging Module** with integrated DW01A battery management system (over-charge, over-discharge, over-current protection).
  * **TPS63020 Buck-Boost Module**: Converts varying battery voltage ($3.0\text{V} - 4.2\text{V}$) into a rock-solid **$3.30\text{V}$ rail** (up to 2.0A peak current).
  * Dedicated SS12D00 slide power switch or 2-pin auxiliary power wiring pads.
  * Isolated `/VBAT_GND` return path to prevent ground-loop bypass of BMS safety MOSFETs.
* **User Interface:**
  * **0.96" SSD1306 I2C OLED Display** ($128 \times 64$ pixels, 4-pin header).
  * **2× KY-040 / EC11 Rotary Encoders** with tactile detents & integrated push clicks (Knob 1 = Action Type, Knob 2 = Parameter Value).
  * **12×12 mm Momentary Push Button**: High-visibility Master Start / Emergency Stop trigger.
* **Docking Interfaces:**
  * **Config Dock (`DOCK`)**: 4-pin magnetic pogo port at the top for reading and flashing parameters onto individual blocks.
  * **Run Port (`OUT`)**: 4-pin magnetic pogo port on the right edge for sequence discovery and run execution.
* **Mechanical Mounting:** 4× M3 plated mounting holes (`H1`–`H4`) with $\ge 3.68\text{ mm}$ clearance around every hole for screw heads, standoffs, and 3D printed case bosses.

### 2.2 Tangible Action Block Board (`hardware/action_block/`)
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
  * MCU Pin 15 (`PD0`, at $104.00, 77.78\text{ mm}$) is routed via a 0.40 mm `B.Cu` trace directly to Net `/RETURN_BUS` (Pin 4).
  * In **Action Block Mode**: `PD0` is set to High-Z floating input (`GPIO_CFGLR_IN_FLOAT`) to preserve passive pass-through.
  * In **End Block Mode (`0xEE`)**: `PD0` is configured as active push-pull TX to loop the `0xAA` discovery frame back to the Master along `/RETURN_BUS`.
  * **Result:** The user only needs to manufacture a single PCB layout for all modular blocks!

---

## 3. Prototype #1 Bill of Materials (BOM)

### Master Controller Unit
| # | Component | Package / Footprint | Designator | Qty | Role / Purpose |
| :-: | :--- | :--- | :--- | :-: | :--- |
| 1 | ESP32-S3-DevKitC-1 | 2×22 2.54mm Female Socket | `U1` | 1 | Master CPU, BLE 5.0 gateway, OLED & UI coordinator |
| 2 | SSD1306 0.96" OLED | 1×04 2.54mm Header | `DISP1` | 1 | $128 \times 64$ graphics, pairing telemetry & battery meter |
| 3 | EC11 Rotary Encoder | 5-Pin Module / KY-040 | `K1`, `K2` | 2 | Knob 1 (Action selector), Knob 2 (Parameter adjuster) |
| 4 | Tactile Switch 12×12mm | 4-Pin THT | `SW1` | 1 | Master Start / Execution trigger button |
| 5 | Slide Switch SS12D00 | 1×03 THT / 2-Pin pads | `SW2` | 1 | System power switch |
| 6 | TP4056 Type-C Module | 1×04 SMT Module Pads | `MOD1` | 1 | 1A Li-ion charger with DW01A BMS protection |
| 7 | TPS63020 Module | 1×06 SMT Module Pads | `MOD2` | 1 | High-efficiency buck-boost regulator ($3.30\text{V}$ output) |
| 8 | 18650 Battery Holder | Single Cell Through-Hole | `BT1` | 1 | 3.7V 2600–3500 mAh rechargeable Li-ion power |
| 9 | Pogo 4-Pin Dock | 1×04 2.54mm THT | `J1`, `J2` | 2 | Upstream Config Dock (`DOCK`) & Run Port (`OUT`) |
| 10 | Ceramic Cap 100nF | Radial P2.54mm | `C1` | 1 | High-frequency noise decoupling on 3.3V rail |

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

| Pin | Net Name | Connected To | Signal Description |
| :--- | :--- | :--- | :--- |
| `IO4` | `/K1_CLK` | Rotary 1 Pin CLK | Action knob rotation clock |
| `IO5` | `/K1_DT` | Rotary 1 Pin DT | Action knob rotation data |
| `IO6` | `/K1_SW` | Rotary 1 Push Switch | Action knob selection click |
| `IO7` | `/K2_CLK` | Rotary 2 Pin CLK | Parameter knob rotation clock |
| `IO8` | `/K2_DT` | Rotary 2 Pin DT | Parameter knob rotation data |
| `IO9` | `/K2_SW` | Rotary 2 Push Switch | Parameter knob confirmation click |
| `IO10` | `/SW_START` | 12×12mm Start Button | Run / Program Compile trigger (Active-LOW, pull-up) |
| `IO17` | `/I2C_SDA` | OLED Display SDA | I2C Data line ($400\text{ kHz}$) |
| `IO18` | `/I2C_SCL` | OLED Display SCL | I2C Clock line ($400\text{ kHz}$) |
| `IO43` | `/TX_DOCK` | Dock Pin 3 | Master UART TX $\to$ Docked Block RX (`115200` baud) |
| `IO44` | `/RX_DOCK` | Dock Pin 4 | Master UART RX $\gets$ Docked Block TX ACK (`115200` baud) |
| `IO15` | `/TX_CHAIN` | Run Port Pin 3 | Master UART TX $\to$ Action Block 1 RX (`115200` baud) |
| `IO16` | `/RX_RETURN` | Run Port Pin 4 | Master UART RX $\gets$ End Block Return Rail (`115200` baud) |

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
| **Board Dimensions** | $120.0\text{ mm} \times 65.0\text{ mm}$ | $32.0\text{ mm} \times 32.0\text{ mm}$ | Standard rectangular outlines |
| **Layer Count** | 2 Layers (`F.Cu`, `B.Cu`) | 2 Layers (`F.Cu`, `B.Cu`) | Dual-layer continuous GND planes |
| **Board Thickness** | $1.6\text{ mm}$ FR-4 | $1.6\text{ mm}$ FR-4 | Standard rigidity |
| **Copper Weight** | 1 oz ($35\text{ }\mu\text{m}$) | 1 oz ($35\text{ }\mu\text{m}$) | Handles up to 2.0A continuous |
| **Solder Mask** | Green (Glossy) | Green (Glossy) | Standard fast turnaround |
| **Silkscreen** | White | White | High-contrast component labels |
| **Surface Finish** | Lead-Free HASL | Lead-Free HASL | RoHS compliant, child-safe |
| **Min Track Width** | $0.25\text{ mm}$ (Signal) / $0.80\text{ mm}$ (Power) | $0.30\text{ mm}$ (Signal) / $0.60\text{ mm}$ (Power) | Easily manufactured |
| **Min Clearance** | $\ge 0.25\text{ mm}$ | $\ge 0.25\text{ mm}$ | 100% DRC verified |
| **Via / Hole Size** | $0.60\text{ mm} / 0.30\text{ mm}$ drill | **0 vias** (all THT pads) | Simplified fabrication |
| **Production ZIP** | [`robosen_master_block_gerbers.zip`](file:///Users/nnnn/Projects/robosen_block/hardware/master_block/robosen_master_block_gerbers.zip) | [`robosen_action_block_gerbers.zip`](file:///Users/nnnn/Projects/robosen_block/hardware/action_block/robosen_action_block_gerbers.zip) | 10 standard production files each |

---

## 6. Pre-Order Dual-Agent Audit Verification

Before submitting fabrication files to JLCPCB, an independent dual-agent verification was conducted by **Antigravity** and **Codex Astra** (`gpt-6-astra`):

1. **Geometry & Placement Invariants:**
   - Master Block: 4× M3 mounting holes verified at $(88.5, 63.5)$, $(200.0, 63.5)$, $(88.5, 122.0)$, and $(200.0, 122.0)\text{ mm}$. Minimum copper clearance to drill edge $= 3.68\text{ mm}$.
   - Action Block: Collinear vertical centering of `IN` and `OUT` docks verified at $Y = 72.50\text{ mm}$.
2. **KiCad DRC Verification:**
   - Master Block: **0 unconnected items, 0 copper clearance errors**.
   - Action Block: **0 unconnected items, 0 copper clearance errors**.
3. **Netlist & Thermal Relief Parity:**
   - 100% netlist matching between schematics and routed PCBs.
   - Dual-layer continuous GND power planes with thermal spokes and automatic island removal verified.

---

## 7. Step-by-Step Soldering & Assembly Guide

### Assembly Order
1. **SMD / Module Solder Pads:**
   - Solder the TP4056 Type-C module and TPS63020 buck-boost module flat onto their surface-mount carrier pads on the Master PCB.
2. **Passive Components:**
   - Solder the 100nF decoupling capacitors (`C1` on Master, `C104` on Action Blocks).
3. **Through-Hole Headers & Sockets:**
   - Solder female header sockets for the ESP32-S3 and CH32V003 DIP modules (enables quick module replacement if needed).
   - Solder the 1×04 female OLED header and 1×03 SWIO programming headers.
4. **Mechanical Components:**
   - Solder the rotary encoders (`K1`, `K2`), 12×12mm Start button, and slide switch (`SW2`).
   - Solder the 4-pin magnetic pogo docks (`IN` / `OUT`).
5. **Battery Installation:**
   - Solder the through-hole 18650 battery holder clips (`BT1`).
   - Insert 18650 cell observing correct polarity (`+` terminal towards power switch).

---

## 8. Firmware Deployment & Factory Flashing

### 8.1 Master Block Firmware Flashing
```sh
cd firmware/esp32_master_controller
idf.py build flash -p /dev/cu.usbserial-XXXX
```
* **Status Confirmation:** OLED boots with *"Robosen Block System v1.0"*, battery percentage icon, and begins BLE background scan for K1 robot.

### 8.2 Action Block Firmware Flashing
Using `minichlink` connected to the 3-pin `PROG` header (`GND`, `3V3`, `SWIO`):
```sh
cd firmware/ch32v003_action_block
minichlink -w action_block.bin flash -b
```
* **Status Confirmation:** Onboard LED flashes emerald green for 300ms, then settles into its assigned action color.
