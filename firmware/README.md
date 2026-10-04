# Robosen Tangible Block System — Firmware Repository

This directory contains the complete source code, flashing scripts, and documentation for all microcontrollers in the Robosen Tangible Modular Coding Block ecosystem.

---

## 1. Directory Structure & Firmware Projects

| Subdirectory | Target Hardware | Role / Description | Status |
|:---|:---|:---|:---|
| **[`esp32_master/`](file:///C:/Users/nnnn/Projects/robosen_block/firmware/esp32_master/)** | ESP32-S3 DevKitC-1 | **Master Block Controller**: Dual-knob UI, 2.13" E-Paper driver, BLE 5.0 Robosen client, Config Dock (UART1) & Run Chain (UART2). | ⚠️ **Update Required** (Add Red Button `GPIO2` & Battery Sense `GPIO1`) |
| **[`ch32v003_action_block/`](file:///C:/Users/nnnn/Projects/robosen_block/firmware/ch32v003_action_block/)** | WCH CH32V003 RISC-V | **Modular Action Block**: Solid slave block with 192-byte flash token storage, WS2812B RGB light feedback, and single-wire UART cascade. | ✅ **Production Ready** |
| **[`ch32v003_end_block/`](file:///C:/Users/nnnn/Projects/robosen_block/firmware/ch32v003_end_block/)** | WCH CH32V003 RISC-V | **Smart End Terminator**: Closing block that loops downstream execution data back to Master RX return rail with green ready LED indicator. | ✅ **Production Ready** |
| **[`standalone_eink_test/`](file:///C:/Users/nnnn/Projects/robosen_block/firmware/standalone_eink_test/)** | ESP32-S3 DevKitC-1 | **E-Paper Benchmark Suite**: Isolated testing for DEPG0213BN / SSD1680 display showing 746ms partial refresh and zero-flicker boot. | ✅ **Verified** |
| **[`esp32_master_eink_test/`](file:///C:/Users/nnnn/Projects/robosen_block/firmware/esp32_master_eink_test/)** | ESP32-S3 DevKitC-1 | Master block E-Paper driver validation sketches. | ✅ **Verified** |
| **[`esp32_ch32v003_programmer/`](file:///C:/Users/nnnn/Projects/robosen_block/firmware/esp32_ch32v003_programmer/)** | ESP32 | High-speed SWIO programmer to flash CH32V003 microcontrollers. | ✅ **Utility** |
| **[`arduino_uno_ch32v003_programmer/`](file:///C:/Users/nnnn/Projects/robosen_block/firmware/arduino_uno_ch32v003_programmer/)** | Arduino Uno (ATmega328P)| Bit-bang SWIO programmer for CH32V003. | ✅ **Utility** |

---

## 2. Firmware Backlog & Hardware Revision Notice

Following the completion of the KiCad carrier board design (`hardware/kicad/`), the **ESP32 Master Block firmware** requires the following planned updates:

1. **Dual Button UI Support**:
   - **`PIN_START_BTN` (GPIO 14)**: Green Tactile Button (`SW3`) — Confirm, Start Run, Next Step.
   - **`PIN_STOP_BTN` (GPIO 2)**: Red Tactile Button (`SW5`) — Cancel, Immediate Stop / Emergency Halt, Back to Previous Screen.
2. **Battery Voltage Sensing (`BATSENSE`)**:
   - **`PIN_BATSENSE` (GPIO 1 / ADC1_CH0)**: Sample the 1:1 $100\text{ k}\Omega / 100\text{ k}\Omega$ voltage divider with $100\text{ nF}$ filter cap, convert to battery percentage ($3.0\text{V} - 4.2\text{V}$), and render battery indicator on E-Paper display.
3. **Display Geometry Alignment**:
   - Full layout compatibility with the upgraded $71.0 \times 30.0\text{ mm}$ physical E-Paper module outline.

Detailed firmware implementation instructions are documented in [`firmware/esp32_master/README.md`](file:///C:/Users/nnnn/Projects/robosen_block/firmware/esp32_master/README.md).
