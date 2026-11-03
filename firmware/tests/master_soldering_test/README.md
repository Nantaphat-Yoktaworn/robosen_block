# Robosen Master Block - All-Input & Screen Soldering Test Firmware

> **Target MCU:** ESP32-S3 (DevKitC-1-N8R8 / N16R8) on Master Block Carrier PCB  
> **Source Sketch:** [`master_soldering_test.ino`](master_soldering_test.ino)  
> **Status:** All Soldered Input Devices Verified  
> **Display Mode:** Pure Text Interface (No UI lines, zero decoration for maximum clarity & speed)  
> **Verified Scope:**
> - **Rotary Encoder 1 (`SW1` Action Knob):** CLK, DT, and integrated push switch (IO 8, 9, 10)
> - **Rotary Encoder 2 (`SW2` Param Knob):** CLK, DT, and integrated push switch (IO 11, 12, 13)
> - **Green Start Push Button (`SW3`):** GPIO 14
> - **Red Stop Push Button (`SW5`):** GPIO 2
> - **Li-Ion Battery Voltage Monitor:** 1:1 divider ($100\text{k}\Omega : 100\text{k}\Omega$) on ADC1_CH0 (GPIO 1)
> - **2.13" E-Paper SPI Display:** SSD1680 (DEPG0213BN, 122x250)
> - **Onboard WS2812 Status RGB LED:** GPIO 48

---

## 1. Hardware Pinout Table

| Hardware Component | Reference | ESP32-S3 GPIO | Function | Verification Expected Behavior |
|:---|:---:|:---:|:---|:---|
| **Knob 1 Phase A (`CLK`)** | `SW1` Pin 1 | **GPIO 8** | `INPUT_PULLUP` | Rotating clockwise increments `Pos`, CCW decrements |
| **Knob 1 Phase B (`DT`)** | `SW1` Pin 2 | **GPIO 9** | `INPUT_PULLUP` | Quadrature phase decoding |
| **Knob 1 Push Switch (`SW`)** | `SW1` Pin 3 | **GPIO 10** | `INPUT_PULLUP` | Clicking shows `PRESS` on screen & lights LED Cyan |
| **Knob 2 Phase A (`CLK`)** | `SW2` Pin 1 | **GPIO 11** | `INPUT_PULLUP` | Rotating clockwise increments `Pos`, CCW decrements |
| **Knob 2 Phase B (`DT`)** | `SW2` Pin 2 | **GPIO 12** | `INPUT_PULLUP` | Quadrature phase decoding |
| **Knob 2 Push Switch (`SW`)** | `SW2` Pin 3 | **GPIO 13** | `INPUT_PULLUP` | Clicking shows `PRESS` on screen & lights LED Magenta |
| **Green Start Push Button** | `SW3` | **GPIO 14** | `INPUT_PULLUP` | Pressing lights LED Green, increments hit counter |
| **Red Stop Push Button** | `SW5` | **GPIO 2** | `INPUT_PULLUP` | Pressing lights LED Red, increments hit counter |
| **Battery Voltage Sense** | `R3`, `R4`, `C1` | **GPIO 1** | ADC1_CH0 ($1:1$) | Reads $3.2\text{V} - 4.2\text{V}$ Li-ion voltage & capacity percentage |
| **E-Paper Clock** | `DISP1` Pin 6 | **GPIO 21** | SPI SCK (`SCL`) | 4 MHz hardware SPI bus |
| **E-Paper Data In** | `DISP1` Pin 5 | **GPIO 38** | SPI MOSI (`SDA`) | SPI data bus |
| **E-Paper Chip Select** | `DISP1` Pin 2 | **GPIO 7** | Chip Select (`CS`) | Active LOW |
| **E-Paper Data / Command** | `DISP1` Pin 3 | **GPIO 6** | `DC` | High = Data, Low = Command |
| **E-Paper Reset** | `DISP1` Pin 4 | **GPIO 5** | `RES` / `RST` | Active LOW hardware reset pulse |
| **E-Paper Busy Flag** | `DISP1` Pin 1 | **GPIO 4** | `BUSY` | Status line |
| **Status RGB LED** | Built-in | **GPIO 48** | Onboard WS2812 | Instant feedback for all inputs |

---

## 2. Pure Text Display Readout

The display renders clean, monospace text lines with no borders, boxes, or lines:

```text
== ROBOSEN ALL-INPUT TEST ==
K1 (SW1-IO08): Pos:  +12 | SW:IDLE 
K2 (SW2-IO11): Pos:   -3 | SW:PRESS
SW3 Start(14): [PRESS] | Hits:5
SW5 Stop (02): [IDLE]  | Hits:2
Battery (01) : 3.65V (43%) 1825mV
Health Status: HEALTHY (OK)
Cmds: 'r'=Refresh | 'c'=Clear | 'b'=Batt
```

---

## 3. Interactive Serial Commands

Open the Serial Monitor at **115200 baud** and send any single-character command:

| Key | Action | What it Tests |
|:---:|:---|:---|
| `r` | **Reinit & Full Refresh** | Sends hardware reset pulse to display, re-runs buffer sync, and does full clean screen wipe. |
| `s` | **Pin Readout Diagnostic** | Prints live digital logic level (0 or 1) of all 10 pins (`K1_CLK`, `K1_DT`, `K1_SW`, `K2_CLK`, `K2_DT`, `K2_SW`, `SW3`, `SW5`, `BUSY`, `RES`). |
| `c` | **Clear Counters** | Resets both knob positions and all button hit counters back to 0. |
| `b` | **Deep Battery Diagnostic** | 16-sample ADC noise burst test to verify filter capacitor `C1` soldering. |
| `l` | **Cycle RGB LED** | Tests WS2812 Red $\to$ Green $\to$ Blue $\to$ White $\to$ Off. |
| `?` | **Help Menu** | Prints command guide and pin table. |
