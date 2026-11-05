# Master Block Screen Area Finder & Bezel Calibration Utility

> **Target MCU:** ESP32-S3 (DevKitC-1-N8R8 / N16R8) on Master Block Carrier PCB  
> **Target Display:** 2.13" E-Paper Display (DEPG0213BN / SSD1680, 250×122 Landscape)  
> **Source File:** [`screen_area_finder.ino`](file:///Users/nnnn/Projects/robosen_block/firmware/tests/screen_area_finder/screen_area_finder.ino)  
> **Git Branch:** `feat/screen-area-finder`  
> **Status:** Verified Working (0 Compilation Errors/Warnings)  

---

## 1. Overview

In the physical Master Block prototype, the 2.13" E-Paper display is positioned slightly off-center relative to the dual rotary knobs due to PCB routing constraints. To visually center the screen on the handheld enclosure, the custom 3D-printed top housing masks part of the screen edges.

This standalone utility allows users to:
1. Interactively calibrate the usable visible rectangle using the Master Block's rotary knobs and buttons.
2. Align the displayed border lines directly against the inner opening of the 3D-printed enclosure.
3. Automatically save the calibrated bounds to internal ESP32-S3 Non-Volatile Storage (NVS flash via `Preferences`).
4. Output ready-to-copy C++ `#define` macros directly to the Serial Monitor (115200 baud).

```
+-----------------------------------------------------------+
| Physical 2.13" Panel Perimeter (250 x 122)               |
|   +---------------------------------------------------+   |
|   | 3D-Printed Bezel Cutout Opening                   |   |
|   |   TL *-------------------------------------* TR   |   |
|   |      |                                     |      |   |
|   |      |  Calibrated Active Screen Area      |      |   |
|   |      |  Width = (X_max - X_min + 1)        |      |   |
|   |      |  Height = (Y_max - Y_min + 1)       |      |   |
|   |      |                                     |      |   |
|   |   BL *-------------------------------------* BR   |   |
|   +---------------------------------------------------+   |
+-----------------------------------------------------------+
```

---

## 2. Hardware Controls

| Input Component | GPIO | Physical Control | Function |
|:---|:---|:---|:---|
| **Green Button (`SW3`)** | **GPIO 14** | Tactile Button (Green) | **Cycle Corner**: Switches active corner: `Top-Left` $\to$ `Top-Right` $\to$ `Bottom-Right` $\to$ `Bottom-Left` |
| **Left Knob (`SW1`)** | **GPIO 8 / 9** | KY-040 Rotary Encoder | **Vertical Move (Y)**: Moves top/bottom edge up or down |
| **Right Knob (`SW2`)** | **GPIO 11 / 12** | KY-040 Rotary Encoder | **Horizontal Move (X)**: Moves left/right edge left or right |
| **Knob Switches** | **GPIO 10 / 13** | Push Switch (`K1_SW` / `K2_SW`) | **Toggle Step**: Toggles between **Fine (1px)** and **Coarse (5px)** increments |
| **Red Button (`SW5`)** | **GPIO 2** | Tactile Button (Red) | **Save & Finish**: Writes to NVS flash, prints C++ macros, draws final summary |
| **Status RGB LED** | **GPIO 48** | WS2812 NeoPixel | Color-coded active corner feedback (Blue = TL, Magenta = TR, Amber = BR, Teal = BL, Green = Saved) |

---

## 3. Step-by-Step Calibration Procedure

1. **Upload Firmware:**
   Compile and flash `screen_area_finder.ino` to the Master Block ESP32-S3.
2. **Mount Master Block into 3D-Printed Housing:**
   Place the PCB inside the enclosure so the bezel opening sits over the display.
3. **Calibrate Top-Left (TL) Corner:**
   - Active Corner defaults to `TOP-LEFT (TL)`.
   - Turn **Left Knob (SW1)** until the top edge is just visible inside the bezel.
   - Turn **Right Knob (SW2)** until the left edge is just visible inside the bezel.
   - Click either knob to switch between 1px (fine alignment) and 5px (rapid movement).
4. **Calibrate Top-Right (TR) Corner:**
   - Press **Green Button (SW3)** to advance to `TOP-RIGHT (TR)`.
   - Turn **Right Knob (SW2)** to align the right edge with the bezel cutout.
5. **Calibrate Bottom-Right (BR) Corner:**
   - Press **Green Button (SW3)** to advance to `BOTTOM-RIGHT (BR)`.
   - Turn **Left Knob (SW1)** to align the bottom edge with the bezel cutout.
6. **Save Calibration:**
   - Press **Red Button (SW5)** (or hold Green Button for 1.5s).
   - The screen freezes with a solid border and `*** CALIBRATION SAVED ***` banner.
   - Open Serial Monitor (115200 baud) to view the generated macros.

---

## 4. Output Example & Integration

Upon saving, the firmware generates a formatted block in the Serial Monitor:

```cpp
// ==============================================================================
// CALIBRATED 3D-PRINT BEZEL VISIBLE SCREEN DIMENSIONS
// ==============================================================================
#define SCREEN_VISIBLE_X_MIN    14
#define SCREEN_VISIBLE_Y_MIN    8
#define SCREEN_VISIBLE_X_MAX    236
#define SCREEN_VISIBLE_Y_MAX    114
#define SCREEN_VISIBLE_WIDTH    223
#define SCREEN_VISIBLE_HEIGHT   107
// ==============================================================================
```

These definitions can be directly placed into [`firmware/esp32_master/esp32_master.ino`](file:///Users/nnnn/Projects/robosen_block/firmware/esp32_master/esp32_master.ino) to constrain headers, middle bands, and footers within the visible cutout area.

### NVS Flash Storage Details:
- **Namespace:** `"screen_cal"`
- **Keys:** `x_min`, `y_min`, `x_max`, `y_max`, `width`, `height`, `calibrated` (bool).
