# Robosen Tangible Action Block Hardware & PCB Design

> **Project:** Tangible Modular Coding Block System for Robosen Robot  
> **Target Module:** Modular Action Block (CH32V003 RISC-V Slave)  
> **Form Factor:** 32.0 mm × 32.0 mm 2-Layer FR-4 Carrier PCB (1.6 mm thickness, 1 oz copper)  
> **KiCad Version:** KiCad 10.0.6  
> **Fabrication Status:** **ORDERED AT JLCPCB (October 5, 2026)** — `robosen_action_block_gerbers.zip`  

---

## 1. System Overview & Electrical Architecture

Every Action Block is a drop-proof, solid modular unit with **zero moving parts** (no potentiometers, dials, or buttons). It contains:
1. **Microcontroller (`MCU`)**: **TENSTAR CH32V003F4P6** 2×11 DIP module (WCH 32-bit RISC-V core @ 24 MHz, 16 KB Flash, 2 KB SRAM).
2. **Visual Feedback (`RGB`)**: 3-pin 2.54 mm pitch header for a pre-soldered **WS2812 RGB LED module** (Top-to-Bottom: `GND`, `VCC`, `IN`).
3. **Decoupling Capacitor (`C104`)**: 100 nF ceramic capacitor placed adjacent to `VDD` and `GND`.
4. **Upstream Pogo Connector (`IN`)**: 4-pin 2.54 mm pitch magnetic pogo interface, **vertically centered** at $Y = 72.50\text{ mm}$.
5. **Downstream Pogo Connector (`OUT`)**: 4-pin 2.54 mm pitch magnetic pogo interface, **vertically centered** at $Y = 72.50\text{ mm}$ (ensures collinear flush alignment across chained blocks).
6. **Programming Header (`PROG`)**: 3-pin 2.54 mm header (`GND`, `3V3`, `SWIO`) for rapid 1-wire firmware flashing via `minichlink` or ESP32 programmer.

---

## 2. Pinout & Net Assignments

### 4-Pin Pogo Interface (`IN` & `OUT`, Centered at $Y = 72.50\text{ mm}$)

| Pin # | Signal Name | Upstream Connector (`IN`) | Downstream Connector (`OUT`) |
|:---:|:---|:---|:---|
| **1** | `+3V3` | Power Input ($Y = 68.69\text{ mm}$) | Power Output ($Y = 68.69\text{ mm}$) |
| **2** | `GND` | System Ground Reference ($Y = 71.23\text{ mm}$) | System Ground Reference ($Y = 71.23\text{ mm}$) |
| **3** | `UART_DATA` | Point-to-Point Input (`/RX_IN` $\to$ `PD6`, $Y = 73.77\text{ mm}$) | Point-to-Point Output (`/TX_OUT` $\gets$ `PD5`, $Y = 73.77\text{ mm}$) |
| **4** | `RETURN_BUS`| Continuous Return Rail Pass-Through ($Y = 76.31\text{ mm}$) | Continuous Return Rail Pass-Through ($Y = 76.31\text{ mm}$) |

> **Return Rail Detour:**  
> The `/RETURN_BUS` rail is routed on `B.Cu` ($0.40\text{ mm}$) with a 45° detour below the MCU DIP socket at $Y = 87.25\text{ mm}$ to prevent shorting through-hole pins 4 & 15.

### WS2812 RGB LED Header (`RGB`, 1×03 Pin Header)

| Pin # | Silk Label | Board Position ($X, Y$) | Net Assignment | Notes |
|:---:|:---|:---|:---|:---|
| **1** | `GND` | $(84.00, 59.96)\text{ mm}$ (Top) | `GND` | Thermal relief connection to continuous GND planes |
| **2** | `VCC` | $(84.00, 62.50)\text{ mm}$ (Middle) | `+3V3` | $0.60\text{ mm}$ power bus connection |
| **3** | `IN` | $(84.00, 65.04)\text{ mm}$ (Bottom) | `/LED_DIN` | High-speed 800 kHz signal to MCU pin 6 (`PA2`) |

### Programming & Debug Header (`PROG`, 1×03 Pin Header)

| Pin # | Silk Label | Board Position ($X, Y$) | Net Assignment |
|:---:|:---|:---|:---|
| **1** | `GND` | $(109.50, 81.42)\text{ mm}$ | `GND` |
| **2** | `3V3` | $(109.50, 83.96)\text{ mm}$ | `+3V3` |
| **3** | `SWIO` | $(109.50, 86.50)\text{ mm}$ | `/SWIO` (`PD1` on MCU pin 16) |

---

## 3. PCB Layout & Manufacturing Specifications

| Parameter | Specification |
| :--- | :--- |
| **Dimensions** | $32.00\text{ mm} \times 32.00\text{ mm}$ |
| **Layers** | 2 Layers (`F.Cu`, `B.Cu`) |
| **Thickness** | $1.6\text{ mm}$ FR-4 |
| **Copper Weight** | 1 oz ($35\text{ }\mu\text{m}$) |
| **Surface Finish** | Lead-Free HASL (or ENIG) |
| **Min Track / Spacing**| $0.30\text{ mm} / 0.25\text{ mm}$ ($0.60\text{ mm}$ for `+3V3`, $0.40\text{ mm}$ for `/RETURN_BUS`) |
| **Min Drill Size** | $0.85\text{ mm}$ (Zero vias; all connections use through-hole component pads) |
| **Ground Planes** | Continuous filled copper zones on both `F.Cu` and `B.Cu` with thermal reliefs |

---

## 4. Verification & Dual-Agent Audit

* **KiCad DRC**: **0 Errors, 0 Unconnected Items, 0 Copper Clearance Violations**.
* **Dual-Agent Verification**: Independently audited and verified by Antigravity and Codex Astra (`gpt-6-astra`).
* **Artifacts**:
  * Gerber Package: [`robosen_action_block_gerbers.zip`](robosen_action_block_gerbers.zip)
  * Schematic PDF: [`action_block_schematic.pdf`](action_block_schematic.pdf)
  * Top 3D Render: [`pcb_preview/action_block_top.png`](pcb_preview/action_block_top.png)
  * Bottom 3D Render: [`pcb_preview/action_block_bottom.png`](pcb_preview/action_block_bottom.png)
  * Routed Vector: [`pcb_preview/action_block_routed.svg`](pcb_preview/action_block_routed.svg)
