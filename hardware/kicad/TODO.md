# KiCad Hardware & Schematic Design TODO List

> **Project:** Robosen K1 Master Tangible Coding Block — Carrier Motherboard  
> **Status:** Active Backlog & Action Items  
> **KiCad Version:** KiCad 10.0.6  
> **Directory:** `hardware/kicad/`  

---

## 📋 Task Checklist

- [ ] **1. Add Battery Percentage Monitoring Divider (ADC Voltage Sensor)**
  - [ ] Add voltage divider resistors (`R3`, `R4`) to schematic `robosen_master_block.kicad_sch`
  - [ ] Choose high-value resistors ($100\text{ k}\Omega / 100\text{ k}\Omega$ or $200\text{ k}\Omega / 200\text{ k}\Omega$, 1% precision) to minimize parasitic battery drain
  - [ ] Connect divider top to `VBAT_SW` (switched power) so current drain is 0.00 $\mu$A when power switch `SW4` is turned off
  - [ ] Route divider midpoint (`BATSENSE`) to an unused ADC1 pin on ESP32-S3 (e.g. `GPIO1` / Pin 26 or `GPIO3` / Pin 13)
  - [ ] Add optional $100\text{ nF}$ ceramic capacitor (`C1`) across `BATSENSE` to `GND` for noise filtering and ADC sample stabilization
  - [ ] Update `build_schematic.py` generator script and regenerate schematic & symbols
  - [ ] Run KiCad ERC check (`0 violations`)

- [ ] **2. Fix Footprint of ESP32-S3 Socket (Antenna Keepout & Clearance)**
  - [ ] Update `ESP32-S3-DevKitC-1-Socket.kicad_mod` with antenna overhang boundary
  - [ ] Draw meander antenna physical zone on `F.Fab` and `F.SilkS` ($X \in [-9.0, +9.0]$, $Y \in [-24.0, -31.5]$)
  - [ ] Add copper keepout zone (`zone_type keepout`, no copper on all layers) under and around the RF antenna region
  - [ ] Add silkscreen warning label: `ANTENNA OVERHANG / NO COPPER ZONE`
  - [ ] Verify clearance to carrier board edge so the antenna can hang over the PCB edge for optimal 2.4 GHz RF / BLE performance

- [ ] **3. Add Full E-Paper Display Mechanical Outline & Layout to Footprint**
  - [ ] Upgrade `EPaper_2.13in_Header_1x08.kicad_mod` from a simple 1×08 pin header to include the complete physical display module outline
  - [ ] Draw display module outer boundary ($65.0\text{ mm} \times 30.2\text{ mm}$ or $59.2\text{ mm} \times 29.2\text{ mm}$) on `F.SilkS` and `F.Fab`
  - [ ] Draw active display window ($48.55\text{ mm} \times 23.71\text{ mm}$, $250 \times 122$ pixels) on `F.Fab`
  - [ ] Add 4 corner mounting holes (Ø $2.2\text{ mm}$ for M2 standoffs) if matching standard breakout PCB modules (e.g. Waveshare / GoodDisplay)
  - [ ] Show FPC ribbon cable fold area and clearance zone to prevent collisions with neighboring components

- [ ] **4. KiCad Project & Repository Clean-Up**
  - [ ] Organize generated footprint SVG files into a dedicated subdirectory (e.g., `hardware/kicad/footprint_svg/`) to keep `hardware/kicad/` clean
  - [ ] Verify `.gitignore` rules for KiCad temporary files (`*.kicad_prl`, `*.lck`, `*.bak`, `*-save.kicad_*`, `_autosave-*`)
  - [ ] Remove obsolete/legacy footprints or duplicate files no longer referenced by the project
  - [ ] Audit repository root to ensure clean structure per project deliverables storage rules

---

## 📐 Detailed Engineering Notes for Implementation

### Task 1: Battery Voltage Divider Calculation
$$V_{ADC} = V_{BAT} \times \frac{R_4}{R_3 + R_4}$$

With $R_3 = 100\text{ k}\Omega$ (1%) and $R_4 = 100\text{ k}\Omega$ (1%):
- **Full charge ($4.20\text{ V}$):** $V_{ADC} = 2.10\text{ V}$ (well within ESP32-S3 $0 - 3.1\text{ V}$ ADC range at 11 dB attenuation).
- **Nominal ($3.70\text{ V}$):** $V_{ADC} = 1.85\text{ V}$.
- **Cutoff ($3.00\text{ V}$):** $V_{ADC} = 1.50\text{ V}$.
- **Quiescent Current:** $I = 4.2\text{ V} / 200\text{ k}\Omega = 21\ \mu\text{A}$. Connected to `VBAT_SW` so current is **0 $\mu$A** in storage / off state.
- **Recommended ADC Pin:** `GPIO1` (Pin 26 on right header) — part of **ADC1 Channel 0**, which functions simultaneously while BLE is transmitting (ADC2 is restricted during wireless operation).

### Task 2: ESP32-S3 Antenna Keepout Zone
- **ESP-IDF Hardware Design Guidelines:** The antenna area must extend beyond the edge of the carrier board by at least $15\text{ mm}$, or have a cutout / no copper zone extending at least $15\text{ mm}$ on all three sides of the antenna.
- **Keepout Dimensions:** $18.0\text{ mm}$ wide $\times 8.0\text{ mm}$ deep from the top socket edge.

### Task 3: E-Paper 2.13" Display Mechanical Integration
- **Display Model:** DEPG0213BN / SSD1680 2.13-inch Black/White Flexible E-Paper.
- **Driver Module Outer Size:** $65.0\text{ mm} \times 30.2\text{ mm}$.
- **Header Location:** 1×08 header ($2.54\text{ mm}$ pitch) located along the short edge or back connector.
- **Mounting:** Can be mounted using double-sided foam tape directly onto the carrier board, or secured via 4 corner M2 screws into threaded standoffs.
