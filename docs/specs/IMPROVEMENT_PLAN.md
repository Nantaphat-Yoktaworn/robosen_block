# Tangible Modular Coding Block System: Master Improvement Plan

> **Project:** Physical Modular Programming Blocks $\longleftrightarrow$ Robosen K1 Humanoid Robot  
> **Goal:** High reliability, ultra-low BOM cost per block, robust Bluetooth BLE execution, and engaging screenless STEM learning experience for young children ($\le 7$ years old).

---

## 1. Executive Summary & Improvement Pillars

```text
+---------------------------------------------------------------------------------------------------+
|                                    5-PILLAR IMPROVEMENT PLAN                                      |
+-----------------+-----------------+------------------+--------------------+-----------------------+
|   1. HARDWARE   |   2. PROTOCOL   |   3. MASTER BLE  |   4. UX & VISUAL   |  5. SOLID BLOCKS &    |
|   & POWER BOM   |  & RESILIENCE   |  FIRMWARE QUEUE  |     FEEDBACK       |  CENTRAL CONFIG DOCK  |
+-----------------+-----------------+------------------+--------------------+-----------------------+
| * $0.15 RISC-V  | * Binary Frames | * ESP32-S3 BLE   | * E-Ink Display    | * Master Config Dock  |
|   (CH32V003)    | * CRC-8 Checksum| * 100% Action Ack|   (Text & Icons)   | * Dual Rotary Dials   |
| * Solid Blocks  | * Config UART   | * Dual Hardware  | * WS2812B Light    | * Zero Moving Parts   |
|   (No Knobs/Btn)|   + 2-Phase Bus |   UART Queues    |   Choreography     |   on Action Blocks    |
| * LiPo + USB-C  | * Auto-Discovery| * Auto-Reconnect | * Silent Classroom | * Internal Non-Volatile|
| * Magnetic Pogo | * Bidirectional | * Fall Recovery  |   (No Buzzer Noise)|   Flash / EEPROM      |
+-----------------+-----------------+------------------+--------------------+-----------------------+
```

---

## 2. Pillar 1: Hardware & Electrical Optimization

### 1.1 Microcontroller Downsizing & Component Optimization
- **Master Block**: Upgraded to **ESP32-S3** (Dual-Core Xtensa LX7) to provide native Bluetooth 5.0 BLE, SPI interface for the E-Ink display, ADC/GPIOs for 2 Rotary Knobs, and dual independent UART ports for the **Config Port** and **Run Port**.
- **Action Blocks**: Transition to the ultra-low-cost **WCH CH32V003 (32-bit RISC-V)** in SOP-8 package (~$0.15).
- **Zero Mechanical Wear on Blocks**: By moving the action selector and parameter knob directly to the Master Block dock, action blocks have **no potentiometers or tactile buttons**.
  - **BOM Cost per Action Block**: Drops from ~$1.50+ to **~$0.25 – $0.35** (CH32V003 + WS2812B LED + 4-pin magnetic pogo connector + solid PCB).
  - **Ultra-Low Idle Power**: CH32V003 draws $< 10\,\mu\text{A}$ in standby sleep mode.

### 1.2 Master Battery & Power Subsystem
- **Master Battery**: Single-cell LiPo / 18650 battery (3.7V, 1500–2200 mAh) with onboard TP4056 USB-C charging circuit and battery management system (BMS).
- **Power Rail Delivery**: High-efficiency synchronous buck-boost converter providing regulated 3.3V across `Pin 1 (V+)` of both the Config Port and the Run daisy chain.

### 1.3 Magnetic Pogo Connector & Mechanical Keying
- **Polarity Keying**: Asymmetrical magnetic attraction (North-South pairing) or keyed physical notches to prevent accidental reverse connection.
- **Electrical Protection**: Reverse-polarity Schottky diode on `V+` and 10 kΩ pull-up with 22 pF RC noise filtering on UART data pins to eliminate contact bounce.

---

## 3. Pillar 2: Robust Communication Protocol & Bus Architecture

### 3.1 Dual-Port Communication Topology

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 MASTER BLOCK CONTROLLER                                │
│                                                                                        │
│        ┌─────────────────────────────┐        ┌─────────────────────────────┐         │
│        │      1. CONFIG PORT         │        │        2. RUN PORT          │         │
│        │  (4-Pin Magnetic Dock)      │        │  (4-Pin Daisy-Chain Start)  │         │
│        └──────────────┬──────────────┘        └──────────────┬──────────────┘         │
└───────────────────────┼──────────────────────────────────────┼────────────────────────┘
                        │                                      │
              (Dock 1 Block to Flash)             (Snap Full Sequence to Run)
                        │                                      │
                        ▼                                      ▼
             ┌─────────────────────┐             ┌───────────┐   ┌───────────┐   ┌─────┐
             │ SINGLE ACTION BLOCK │             │  BLOCK 1  │──►│  BLOCK 2  │──►│ END │
             │  - CH32V003 ($0.15) │             │ (CH32V003)│   │ (CH32V003)│   │     │
             │  - WS2812B RGB LED  │             └─────┬─────┘   └─────┬─────┘   └─────┘
             │  - NO BUTTON/KNOB!  │                   └───────────────┴────────────▲
             └─────────────────────┘                     (Return Rail / Live LED)  │
```

1. **Config Port (Dedicated Dock UART)**: Master connects point-to-point with 1 docked action block to read current flash settings, preview action/parameters on the E-Ink display, and write new settings to the block's internal flash (`0xCF`).
2. **Run Port (Daisy-Chain UART + Return RX Rail)**: Connected sequence auto-discovers physical order in Phase 1 (`0xAA`) and receives real-time step broadcasts in Phase 2 (`0xBB`).

---

### 3.2 Protocol Frame Specifications & CRC-8 Verification

All communications use binary framing protected by **CRC-8** (Polynomial: $x^8 + x^2 + x + 1$, `0x07`):

#### 1. Config Port Write & ACK Frames (`Header = 0xCF`)
* **Master Write Command**:
  ```text
  [ 0xCF ] [ 0x02 (Write) ] [ ActionID ] [ ParamVal ] [ CRC-8 ] [ 0x55 ]
  ```
* **Block ACK Response**:
  ```text
  [ 0xCF ] [ 0x06 (ACK) ] [ CRC-8 ] [ 0x55 ]
  ```

#### 2. Phase 1: Discovery & Compilation Frame (`Header = 0xAA`)
Transmitted downstream from Master Run Port; each block appends its stored flash token:
```text
+-------------+------------+-------------+-----------+-------------+-----------+-------------+--------+-------------+
| HEADER      | PACKET LEN | BLOCK COUNT | BLOCK 1   | PARAMETER 1 | BLOCK 2   | PARAMETER 2 | CRC-8  | FOOTER      |
| 1 Byte: 0xAA| 1 Byte (N) | 1 Byte (K)  | 1 Byte ID | 1 Byte Val  | 1 Byte ID | 1 Byte Val  | 1 Byte | 1 Byte: 0x55|
+-------------+------------+-------------+-----------+-------------+-----------+-------------+--------+-------------+
```

#### 3. Phase 2: Live Step Execution Broadcast Frame (`Header = 0xBB`)
Transmitted along Pin 3 (`CHAIN_TX` $\to$ `PD6` $\to$ `PD5`) during robot movement to trigger live step LEDs:
```text
+-------------+-------------+-------------+--------+-------------+
| HEADER      | ACTIVE STEP | TOTAL STEPS | CRC-8  | FOOTER      |
| 1 Byte: 0xBB| 1 Byte (1-N)| 1 Byte (N)  | 1 Byte | 1 Byte: 0x55|
+-------------+-------------+-------------+--------+-------------+
```

---

## 4. Pillar 3: Master ESP32-S3 Firmware & Robosen BLE Engine

### 4.1 Non-Blocking Asynchronous Command Queue
The Master ESP32-S3 coordinates robot actions and feeds execution states back to the physical blocks:

```text
[ Master Receives Return Program (0xAA) via Pin 4 RX ]
                       │
                       ▼
             [ Verify CRC-8 Checksum ]
                       │
                       ▼
┌──────────────────────┴────────────────────────────────────────────────┐
│ FOR EACH COMMAND (Step Index = 1 to N):                                │
│                                                                       │
│  1. Broadcast Step State: Send [0xBB, StepIndex, N, CRC] on Pin 3     │
│     -> Forwarded PD6 -> PD5; target block turns bright green (0,255,0)│
│                                                                       │
│  2. Dispatch Robosen BLE Command:                                     │
│     - If Action (0x17): Send BLE frame & wait via abortableDelay()    │
│       (Duration lookup 2.5s–55s; Python daemon also parses 0x64 ACK)  │
│     - If Locomotion (0x01-0x08): Start abortable timer, then 0x0C Stop│
│                                                                       │
│  3. Stabilization Buffer: 300-500ms posture stabilization             │
└──────────────────────┬────────────────────────────────────────────────┘
                       │
                       ▼
 [ Broadcast [0xBB, 0xFF, N] (Synchronized Rainbow Sparkle Across All Blocks) ]
```

### 4.2 Multi-Robot Classroom BLE Pairing (Smart NVS Binding)
- **Direct Instant Boot (<500ms)**: Master ESP32-S3 reads `last_paired_mac` from internal Non-Volatile Storage (NVS) on power-up and connects directly without broadcast scanning delays or classroom crosstalk.
- **Teacher Pairing Menu on E-Ink**: Holding the Start button or Knob for 3 seconds enters Pairing Mode. Nearby `K1-*` robots are scanned, sorted by **RSSI Proximity (nearest robot first)**, selected via Knob 1, and saved to NVS as the new persistent default.
- **Persistent Keep-Alive & Health**: Handshake ping (`0x0B`) every 5s when idle, auto-reconnect with exponential backoff, and live battery telemetry monitoring via Opcode `0x0F`.

---

## 5. Pillar 4: Visual Feedback & UX (E-Ink & Light Language)

### 5.1 E-Ink Display (Master Block Interface)
- **High Contrast & Sunlight Readable**: Perfect for children in daylight/classroom environments.
- **Ultra-Low Idle Power**: Consumes 0 mA once image is drawn.
- **Fast Partial Refresh (~0.3s)**: Updates dynamic action names, large friendly icons, and numerical parameters as the user turns Knob 1 and Knob 2.

### 5.2 Classroom-Friendly Visual Light Language (No Buzzer)
To prevent noisy distractions in classrooms with multiple student groups, all sound buzzers are removed in favor of **expressive WS2812B RGB light choreography**:

| State / Trigger | Master Status LED | Action Block LED Behavior | Visual Meaning |
| :--- | :--- | :--- | :--- |
| **Block Docked (Config Port)** | Soft cyan glow | Gentle cyan pulse | *"Block connected & recognized"* |
| **Action Changed (Knob 1)** | Morphs to action color | Matches action color (Blue, Cyan, Red, Orange, Purple) | *"Action selected"* |
| **Param Changed (Knob 2)** | E-Ink text updates | Flashes $N$ times rapidly | *"Parameter value preview"* |
| **Config Saved (Flash Write)** | Single green flash | **Emerald Green "Success Pulse"** | *"Saved to permanent memory"* |
| **Start Press (Phase 1)** | Bright white pulse | **"Data Comet Wave":** Light sweeps rapidly Block 1 $\to$ End | *"Program compiled & verified"* |
| **Active Execution (Phase 2)**| Solid green | **Bright pulsating green (100%)** on active step; others dim (20%) | *"Robot currently running this block"* |
| **Program Finished** | Rainbow ripple | **Synchronized Rainbow Sparkle** across all blocks | *"Sequence complete / Victory!"* |
| **Error / Broken Loop** | Double red flash | Double red flash on disconnected block | *"Check magnetic snap connection"* |

---

## 6. Pillar 5: Simplified Solid Action Blocks & Memory

### 6.1 Action Block Hardware Architecture (Updated for Production `TSSOP-20`)
- **Solid Shell Design**: Sealed 3D/injection-molded block with no holes or mechanical cutouts for dials/buttons.
- **Non-Volatile Storage**: Production builds (`CH32V003F4P6 TSSOP-20`, evolved from early SOP-8 BOM baseline) use a `64-byte` Flash page at `0x08003FC0` storing `[CFG_MAGIC, ActionID, ParamVal]` permanently across power cycles.
- **Zero Configuration Loss**: Blocks can be powered down, stored in a toy box for months, and instantly retain their programmed action when snapped together.

### 6.2 Early SOP-8 Concept vs. Production `CH32V003F4P6` (`TSSOP-20`) Pinout

```text
   Early Concept (SOP-8)               Production Unified PCB (CH32V003F4P6 TSSOP-20)
        +---------+                       - PD6 (UART1 RX_IN, J1/J2 Pin 3)
 VDD ---| 1     8 |--- GND                - PD5 (UART1 TX_OUT, J1/J2 Pin 3)
 PA1 ---| 2     7 |--- PC4                - PD0 (RETURN_BUS / SW 0xCF RX / End TX)
 PA2 ---| 3     6 |--- PD6 (RX)           - PA2 (WS2812B LED DIN)
 PD1 ---| 4     5 |--- PD5 (TX)           - PD1 (SWIO PROG), PD4/PC0 (Heartbeat LED)
```

---

## 7. Phased Implementation Roadmap

| Phase | Milestone | Focus Areas | Deliverables | Status |
| :---: | :--- | :--- | :--- | :---: |
| **Phase 1** | **ESP32-S3 Master Firmware & E-Ink GUI** | Dual UART handlers (`J1` Config Dock + `J2` Run Chain), E-Ink partial refresh UI, BLE queue engine | Complete ESP32-S3 Arduino firmware (`esp32_master.ino`) | ✅ **Verified on Hardware** |
| **Phase 2** | **CH32V003 Unified Action Block Firmware** | Config Port UART flash writer (`0xCF`), Phase 1 flash reader (`0xAA`), Phase 2 LED tracker (`0xBB`) | C RISC-V firmware (`firmware/ch32v003_action_block`) | ✅ **Verified on Hardware** |
| **Phase 3** | **Light Language Choreography** | Emerald green success pulse, active green step tracking, rainbow victory sparkle | WS2812B animation state machine | ✅ **Verified on Hardware** |
| **Phase 4** | **Solid Enclosure & PCB Layout** | 4-pin magnetic PCB for Master (`115.5×62mm` Proto #1-1) & Unified Action/End (`32×32mm`), solid shells | KiCad PCB projects + 3D CAD | ✅ **Routed / Active Production** |



