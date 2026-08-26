# Project Notes & Engineering Guidelines

> **Project:** Tangible Modular Coding Block System for Robosen Robot  
> **Repository:** Private (`https://github.com/Nantaphat-Yoktaworn/robosen_block.git`)  
> **Last Updated:** August 26, 2026

---

## 1. Agent & Developer Workflow Rules

1. **Wait for Explicit Orders:** Propose and discuss design choices first. Do **NOT** modify files, commit, or push until explicitly commanded by the user.
2. **Proactive Commit Reminders:** Always check for uncommitted changes and proactively remind the user to commit and push before moving to a new topic or when wrapping up a feature.
3. **Repository Visibility:** Ensure the repository remains strictly **Private**.

---

## 2. Core Hardware & System Architecture

### 2.1 Master Controller Block
* **MCU:** **ESP32-S3** (Dual-Core Xtensa LX7, Native Bluetooth 5.0 BLE Central, Hardware SPI for E-Ink, dual hardware UARTs for Config and Run ports).
* **Display:** 1.54" or 2.13" Ultra-Low-Power **E-Ink E-Paper screen** (SPI) with fast partial refresh (~0.3s) showing action names, icons, and parameters.
* **Rotary Encoders:** Dual **EC11 Incremental Rotary Encoders** with tactile detents (clicks):
  * **Knob 1 (Action Selector):** Bidirectional stepping through action list with optional wrap or clamping.
  * **Knob 2 (Parameter Adjuster):** Bidirectional stepping (e.g. 1–10 steps) with strict min/max boundary clamping.
  * Built-in center push-button click on shafts for selection.
* **Dual Connector Ports (4-Pin Magnetic Pogo):**
  1. **Config Port (Dock):** Docks 1 Action Block to read/write settings to its internal non-volatile flash via UART (`0xCF`).
  2. **Run Port (Chain):** Connects the linear daisy-chain sequence to compile (`0xAA`) and execute (`0xBB`).
* **Visual Light Language (Silent Classroom / No Buzzer):**
  * Expressive **WS2812B RGB light choreography** (Cyan dock pulse, Color morphing, Parameter flash count, Emerald green save ACK, Comet compilation wave, Pulsing green active step, Rainbow victory sparkle).
* **Power Subsystem:** 3.7V LiPo / 18650 cell with onboard TP4056 USB-C charging, BMS protection, and synchronous 3.3V buck-boost rail.

---

### 2.2 Multi-Robot Classroom BLE Pairing (Smart NVS Binding)
* **Default Boot:** ESP32-S3 reads `last_paired_mac` from internal **NVS Flash** on boot and connects directly in $<500\,\text{ms}$ with zero classroom crosstalk.
* **E-Ink Teacher Pairing Menu:** Hold Start button / Knob for 3 seconds $\to$ Master enters BLE scan mode $\to$ displays nearby `K1-*` robots sorted by **RSSI signal strength (nearest robot on top)** $\to$ Turn Knob 1 to select $\to$ Click to confirm.
* **Persistence:** The last manually selected robot becomes the new default MAC stored in NVS across all future boots.
* **Physical Tagging:** Color-coded number labels (e.g. *Red 1*, *Blue 2*) matching Master Block to Robot.

---

### 2.3 Solid Smart Action Blocks
* **MCU:** **WCH CH32V003** (32-bit RISC-V in SOP-8 package, ~$0.15).
* **Zero Moving Parts:** No potentiometers or push buttons on individual blocks (drop-proof, indestructible).
* **Memory:** Action Token ID and Parameter stored inside internal 192-byte non-volatile flash/EEPROM emulation.
* **Visual LED:** 1x top-mounted **WS2812B RGB LED**.
* **BOM Cost:** **~$0.25 – $0.35** per block.

---

### 2.4 Serial Protocol Summary
* **Config Port UART (`0xCF`):** Master read/write to single docked block flash.
* **Phase 1 Compilation (`0xAA`):** Forward daisy-chain token accumulation + CRC-8 calculation.
* **Phase 2 Step Execution (`0xBB`):** Return bus broadcast of active step index $\to$ active block glows pulsing green.
