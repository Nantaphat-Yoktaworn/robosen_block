# Robosen Tangible Block System — Firmware Repository

This directory contains the complete source code, flashing scripts, and documentation for all microcontrollers in the Robosen Tangible Modular Coding Block ecosystem.

---

## 1. Directory Structure & Firmware Projects

### Production Firmware
| Subdirectory | Target Hardware | Role / Description | Status |
|:---|:---|:---|:---|
| **[`esp32_master/`](file:///Users/nnnn/Projects/robosen_block/firmware/esp32_master/)** | ESP32-S3 DevKitC-1 | **Master Block Controller**: Dual-knob UI (SW1/SW2), dual buttons (Green Start GPIO 14, Red Stop GPIO 2), Battery ADC monitor (GPIO 1), 2.13" E-Paper driver (SSD1680), BLE 5.0 Robosen client, Config Dock (UART1) & Run Chain (UART2). | ✅ **Production Verified** |
| **[`ch32v003_action_block/`](file:///Users/nnnn/Projects/robosen_block/firmware/ch32v003_action_block/)** | WCH CH32V003 RISC-V | **Modular Action Block**: Solid slave block with 192-byte flash token storage, WS2812B RGB light feedback, and single-wire UART cascade. | ✅ **Production Verified** |
| **[`ch32v003_end_block/`](file:///Users/nnnn/Projects/robosen_block/firmware/ch32v003_end_block/)** | WCH CH32V003 RISC-V | **Smart End Terminator**: Closing block (Token 0xEE) that loops downstream execution data back to Master RX return rail with emerald green ready LED indicator. | ✅ **Production Verified** |

### Test & Bring-up Suites (`firmware/tests/`)
| Subdirectory | Target Hardware | Role / Description | Status |
|:---|:---|:---|:---|
| **[`tests/master_soldering_test/`](file:///Users/nnnn/Projects/robosen_block/firmware/tests/master_soldering_test/)** | ESP32-S3 DevKitC-1 | **All-Input Hardware Verification Suite**: Diagnostic firmware testing both rotary encoders (`SW1`, `SW2`), dual push buttons (`SW3`, `SW5`), battery ADC monitor (`GPIO 1`), WS2812 RGB LED (`GPIO 48`), and pure-text 2.13" E-Paper display. | ✅ **Hardware Verified** |
| **[`tests/standalone_eink_test/`](file:///Users/nnnn/Projects/robosen_block/firmware/tests/standalone_eink_test/)** | ESP32-S3 DevKitC-1 | **E-Paper Benchmark Suite**: Isolated testing for DEPG0213BN / SSD1680 display showing 746ms partial refresh and zero-flicker boot. | ✅ **Verified** |

### Programmers & Flashing Tools (`firmware/tools_programmer/`)
| Subdirectory | Target Hardware | Role / Description | Status |
|:---|:---|:---|:---|
| **[`tools_programmer/esp32_ch32v003_programmer/`](file:///Users/nnnn/Projects/robosen_block/firmware/tools_programmer/esp32_ch32v003_programmer/)** | ESP32 / ESP32-S3 | High-speed SWIO programmer to flash CH32V003 microcontrollers via 1-wire DMI. | ✅ **Utility** |
| **[`tools_programmer/arduino_uno_ch32v003_programmer/`](file:///Users/nnnn/Projects/robosen_block/firmware/tools_programmer/arduino_uno_ch32v003_programmer/)** | Arduino Uno (ATmega328P)| Bit-bang SWIO programmer for CH32V003 using Ardulink. | ✅ **Utility** |

---

## 2. Master Block Verified Hardware Pinout

The Master Block carrier PCB uses the following pin allocations:
- **Knob 1 (Action Selector - SW1)**: `CLK = GPIO 8`, `DT = GPIO 9`, `SW = GPIO 10`
- **Knob 2 (Parameter Adjuster - SW2)**: `CLK = GPIO 11`, `DT = GPIO 12`, `SW = GPIO 13`
- **Master Start Button (SW3 - Green 12mm)**: `GPIO 14` (Active LOW)
- **Master Stop / E-Stop Button (SW5 - Red 12mm)**: `GPIO 2` (Active LOW)
- **Battery Sense (BATSENSE)**: `GPIO 1` (ADC1_CH0 with 100k/100k precision divider + 100nF filter)
- **Config Dock (UART1)**: `TX = GPIO 17`, `RX = GPIO 18` (115200 baud)
- **Run Chain (UART2)**: `TX = GPIO 15`, `RX = GPIO 16` (115200 baud)
- **2.13" E-Paper SPI**: `BUSY = GPIO 4`, `RES = GPIO 5`, `DC = GPIO 6`, `CS = GPIO 7`, `SCK = GPIO 21`, `MOSI = GPIO 38`
- **Status RGB LED**: `GPIO 48` (Onboard WS2812)

Detailed firmware implementation instructions are documented in [`firmware/esp32_master/README.md`](file:///Users/nnnn/Projects/robosen_block/firmware/esp32_master/README.md).
