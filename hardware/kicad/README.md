# Robosen K1 Master Block — KiCad 10 Hardware Project

> **Project:** Custom Carrier Motherboard PCB for Robosen K1 Master Controller  
> **KiCad Version:** 10.0.6 (Fully compatible with KiCad 8.x / 9.x / 10.x)  
> **Location:** `hardware/kicad/`  
> **Author:** Nantaphat Yoktaworn / Antigravity AI  

---

## 1. Project Directory Structure

```
hardware/kicad/
├── robosen_master_block.kicad_pro   # KiCad Master Project configuration
├── fp-lib-table                     # Local project footprint library registry
├── README.md                        # Hardware reference & guide (this file)
└── robosen_master.pretty/           # Custom Master Block Footprint Library (.kicad_mod)
    ├── ESP32-S3-DevKitC-1-Socket.kicad_mod   # Dual 22-pin header socket (0.9" spacing)
    ├── TP4056_Type-C_Module.kicad_mod       # USB-C Lithium Charger + BMS Module
    ├── TPS63020_BuckBoost_Module.kicad_mod  # 3.3V Synchronous DC-DC Regulator
    ├── 18650_Battery_Holder_Single.kicad_mod# Keystone 1042 / BK-18650-PC2 Holder
    ├── KY-040_Rotary_Encoder_Module.kicad_mod# 5-Pin Rotary Encoder breakout
    ├── EPaper_2.13in_Header_1x08.kicad_mod  # 8-Pin SPI header for DEPG0213BN / SSD1680
    └── Pogo_4Pin_Dock_2.54mm.kicad_mod      # Config Dock & Run Chain Bus Port
```

---

## 2. Footprint Specifications & Pinout Summary

### 1. `ESP32-S3-DevKitC-1-Socket`
- **Type:** 2x22 Pin Header Socket (THT, 2.54mm pitch).
- **Row Spacing:** 22.86mm (0.9" standard DIP).
- **Features:** USB-C top orientation marker, courtyard boundary, 1.0mm drill holes with 1.7mm pads.

### 2. `TP4056_Type-C_Module`
- **Board Outline:** 28.0mm × 17.3mm with USB-C connector edge overhang.
- **Pads:**
  - `Pad 1`: `B+` (Battery Positive)
  - `Pad 2`: `B-` (Battery Negative)
  - `Pad 3`: `OUT+` (Protected System Positive)
  - `Pad 4`: `OUT-` (Protected System Ground)
  - `Pads 5 & 6`: `IN-` / `IN+` (External 5V USB power)

### 3. `TPS63020_BuckBoost_Module`
- **Board Outline:** 25.0mm × 15.0mm.
- **Pads (2.54mm pitch):**
  - `Pin 1`: `VOUT` (+3.3V DC Regulated Output)
  - `Pin 2`: `GND` (Common Ground)
  - `Pin 3`: `VIN` (Input from battery switch)
  - `Pin 4`: `EN` (Active HIGH Enable; tie to VIN)
  - `Pin 5`: `PS` (Power Save mode; tie to GND)

### 4. `18650_Battery_Holder_Single`
- **Dimensions:** 77.0mm × 21.0mm.
- **Pin Spacing:** 73.0mm center-to-center (1.6mm drill, 3.0mm pad).
- **Polarity:** Clear `[ + ]` and `[ - ]` silkscreen markings.

### 5. `Pogo_4Pin_Dock_2.54mm`
- **Connector Type:** 1x4 2.54mm pitch header for spring-loaded pogo pins.
- **Standard Pinout:**
  - `Pin 1`: `V+` (3.3V Power Rail)
  - `Pin 2`: `GND` (Ground Rail)
  - `Pin 3`: `DATA` (Config RX / Chain TX)
  - `Pin 4`: `PASS` (Config TX / Chain RX Return Rail)

---

## 3. How to Open & Work in KiCad

1. Launch **KiCad 10** on your computer.
2. Click **Open Project** and select:
   `C:\Users\nnnn\Projects\robosen_block\hardware\kicad\robosen_master_block.kicad_pro`
3. The custom library `robosen_master` is already registered in `fp-lib-table` and will automatically appear in your Footprint Chooser.
4. When drawing schematics, assign footprints from `robosen_master:<Footprint_Name>`.

---

## 4. JLCPCB Fabrication Checklist

When the board layout is complete:
1. **DRC:** Run Design Rules Check (`kicad-cli pcb drc`).
2. **Export Gerbers:** Run `kicad-cli pcb export gerbers` and `kicad-cli pcb export drill`.
3. **Zip & Upload:** Zip all `.gbr` and `.drl` files into a `.zip` file and upload directly to [jlcpcb.com](https://jlcpcb.com/).
