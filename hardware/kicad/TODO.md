# KiCad Hardware & Schematic Design TODO List

> **Project:** Robosen K1 Master Tangible Coding Block — Carrier Motherboard  
> **Status:** Active Backlog & Action Items  
> **KiCad Version:** KiCad 10.0.6  
> **Directory:** `hardware/kicad/`  

---

## 📋 Task Checklist

- [x] **1. Add Battery Percentage Monitoring Divider (ADC Voltage Sensor)**
  - [x] Add voltage divider resistors (`R3`, `R4`) to schematic `robosen_master_block.kicad_sch`
  - [x] Choose high-value resistors ($100\text{ k}\Omega / 100\text{ k}\Omega$, 1% precision) to minimize parasitic battery drain
  - [x] Connect divider top to `VBAT_SW` (switched power) so current drain is 0.00 $\mu$A when power switch `SW4` is turned off
  - [x] Route divider midpoint (`BATSENSE`) to ESP32-S3 `GPIO1` (Pin 26, ADC1_CH0)
  - [x] Add 100nF ceramic capacitor (`C1`, `C_Disc_P2.54mm`) across `BATSENSE` to `GND` for noise filtering and ADC sample stabilization
  - [x] Update `build_schematic.py` generator script and regenerate schematic & symbols
  - [x] Run KiCad ERC check (`0 violations`)

- [x] **2. Fix Footprint of ESP32-S3 Socket (Antenna Keepout & Clearance)**
  - [x] Update `ESP32-S3-DevKitC-1-Socket.kicad_mod` with antenna overhang boundary ($17.5\text{ mm} \text{ wide} \times 6.0\text{ mm} \text{ stick-out}$)
  - [x] Draw meander antenna physical zone on `F.Fab` and `F.SilkS` ($X \in [-8.75, +8.75]$, $Y \in [-35.0, -29.0]$)
  - [x] Add copper keepout zone (`keepout`, no copper on all layers) under and around the RF antenna region
  - [x] Add silkscreen label: `ANTENNA`
  - [x] Verify clearance to carrier board edge so the antenna can hang over the PCB edge for optimal 2.4 GHz RF / BLE performance

- [x] **3. Add Full E-Paper Display Mechanical Outline & Layout to Footprint**
  - [x] Upgrade `EPaper_2.13in_Header_1x08.kicad_mod` with complete physical module boundary ($71.0\text{ mm} \times 30.0\text{ mm}$) on `F.SilkS` and `F.Fab`
  - [x] Draw active display window ($46.0\text{ mm} \times 24.0\text{ mm}$) on `F.Fab` and silkscreen label
  - [x] Add 4 corner mounting holes (Ø $2.2\text{ mm}$ for M2 standoffs, $2.5\text{ mm}$ inset from both edges) with silkscreen screw head keepouts
  - [x] Position 1×08 $2.54\text{ mm}$ header centered on the left edge ($1.5\text{ mm}$ from left edge, $Y \in [-8.89, +8.89]$) with pin labels
  - [x] Add full courtyard boundary ($72.0\text{ mm} \times 31.0\text{ mm}$) on `F.CrtYd`

- [x] **4. KiCad Project & Repository Clean-Up**
  - [x] Organize generated footprint SVG files into a dedicated subdirectory (`hardware/kicad/footprint_svg/`) to keep `hardware/kicad/` clean
  - [x] Verify `.gitignore` rules for KiCad temporary files (`*.kicad_prl`, `*.lck`, `*.bak`, `*-save.kicad_*`, `_autosave-*`, `*.kicad_sch-bak`, `*.kicad_pcb-bak`, `*-backups/`, `~*.lck`)
  - [x] Remove obsolete/legacy footprints or duplicate files no longer referenced by the project
  - [x] Audit repository root to ensure clean structure per project deliverables storage rules

- [x] **5. Add Second Push Button (Cancel / Stop / Back — Red Button) & Confirm Button (Green Button)**
  - [x] Add `SW5` (12×12 mm Push Button, `SW_PUSH_12x12mm`) to schematic `robosen_master_block.kicad_sch`
  - [x] Connect one pin of `SW5` to ESP32-S3 `GPIO2` (Pin 27) with net label `BTN_STOP`
  - [x] Connect the opposite pin of `SW5` to `GND` (leveraging internal ESP32 `INPUT_PULLUP`)
  - [x] Update existing button `SW3` in schematic to designate as Confirm / Next / Start (Green Button, `BTN_START`, `GPIO14`)
  - [x] Update `build_schematic.py` schematic generator script and regenerate schematic & symbols
  - [x] Place `SW5` on schematic layout alongside `SW3` with clear role indicators (`START_CONFIRM [Green]` vs `STOP_CANCEL [Red]`)
  - [x] Run KiCad ERC check (`0 violations`)

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

### Task 5: Dual Push Button UI Specification
- **Primary Button (`SW3` - Green Button):**
  - **Function:** Confirm / Next / Start / Select
  - **Net:** `BTN_START`
  - **Pin:** `GPIO14` (Pin 20 on DevKit left header)
  - **Footprint:** `robosen_master:SW_PUSH_12x12mm` (Active LOW with internal pull-up)
- **Secondary Button (`SW5` - Red Button):**
  - **Function:** Cancel / Stop / Back / Exit
  - **Net:** `BTN_STOP` (or `BTN_CANCEL`)
  - **Recommended Pin:** `GPIO2` (Pin 27 on DevKit right header)
  - **Footprint:** `robosen_master:SW_PUSH_12x12mm` (Active LOW with internal pull-up)
- **Ergonomics & Placement:**
  - Standard UI convention: Symmetrical placement for intuitive physical interaction.
  - Can be placed side-by-side or stacked vertically near the rotary encoders / E-paper display.
  - Clear silkscreen labels on PCB: `CONFIRM / START` and `CANCEL / BACK`.
