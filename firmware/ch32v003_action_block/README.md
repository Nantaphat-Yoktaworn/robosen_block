# Robosen Tangible Modular Block - Unified Action Block Firmware

Firmware for the **TENSTAR CH32V003F4P6** (32-bit RISC-V microcontroller @ 24MHz) implementing the complete **2-Phase Binary Communication Protocol (V2)** and **Config Port Protocol (0xCF)** with **WS2812B RGB LED** state-machine animations and **Non-Volatile Flash Parameter Storage**.

---

## 1. Pin Configuration (TENSTAR CH32V003F4P6)

| Pin Name | Board Label | Physical Role | Notes |
| :--- | :--- | :--- | :--- |
| **`PD6`** | **RX** | **USART1 RX** (115200 8N1) | Upstream data in (from Master Config Dock or Upstream Block Pin 3) |
| **`PD5`** | **TX** | **USART1 TX** (115200 8N1) | Downstream data out (to Master ACK or Next Block Pin 3) |
| **`PA2`** | **PA2** | **WS2812B DIN** (800kHz bitbang) | Status / Step-tracking RGB LED |
| **`PD0`** | **PD0** | **Role Detect** (Internal Pull-Up) | **Floating** = Action Block<br>**Grounded** = Smart End Block (validates CRC & returns packet) |
| **`PD4`** | **PD4** | **Activity LED** | Toggles whenever a valid packet is processed |
| **`PD1`** | **PD1** | **SWIO** | 1-wire programming line (connected to ESP32 programmer) |
| **`V`** | **V** | **Power Supply** (3.3V) | Decoupled with 0.1µF ceramic capacitor to GND |
| **`G`** | **G** | **Ground** (GND) | Common system ground |

---

## 2. Protocols Supported

### Protocol 1: Master Config Dock Protocol (`0xCF`)
* Master writes: `[ 0xCF, 0x02, ACTION_ID, PARAM_VAL, CRC8, 0x55 ]`
* Action Block saves configuration to non-volatile flash page (`0x08003FC0`).
* Action Block replies: `[ 0xCF, 0x06, CRC8, 0x55 ]` (ACK).
* Visual feedback: **Emerald Green Success Flash** (`ws2812_set(0, 255, 40)`).

### Protocol 2: Run Chain Phase 1 Discovery (`0xAA`)
* Master seeds: `[ 0xAA, Len=0, Count=0, CRC8, 0x55 ]`
* Each block appends its `[ActionID, ParamVal]`, increments `Count` and `Len`, updates CRC-8, and forwards downstream.
* Each block records its dynamic position index (`g_my_index = count + 1`).

### Protocol 3: Run Chain Phase 2 Real-Time Step Tracking (`0xBB`)
* Master broadcasts: `[ 0xBB, ACTIVE_STEP, TOTAL_STEPS, CRC8, 0x55 ]`
* If `ACTIVE_STEP == g_my_index`: Block glows **Bright Pulsing Green (100%)**!
* If `ACTIVE_STEP == 0xFF`: Program complete! All blocks play **Rainbow Sparkle**!
* Otherwise: Block glows at dim 20% in its designated Action color.

---

## 3. How to Build & Flash

### Rebuild Binary:
```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

### Flash using ESP32 Programmer on COM3:
```powershell
python ../esp32_ch32v003_programmer/flash_tool.py --port COM3 --bin action_block.bin --reset
```
