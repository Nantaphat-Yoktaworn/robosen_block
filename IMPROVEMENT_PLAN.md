# Tangible Modular Coding Block System: Master Improvement Plan

> **Project:** Physical Modular Programming Blocks $\longleftrightarrow$ Robosen K1 Humanoid Robot  
> **Goal:** High reliability, low-cost bill of materials (BOM), robust Bluetooth BLE execution, and engaging tactile STEM learning experience.

---

## 1. Executive Summary & Improvement Pillars

```
+---------------------------------------------------------------------------------------------------+
|                                    5-PILLAR IMPROVEMENT PLAN                                      |
+-----------------+-----------------+------------------+--------------------+-----------------------+
|   1. HARDWARE   |   2. PROTOCOL   |   3. MASTER BLE  |   4. UX & VISUAL   |    5. SMART BLOCKS    |
|   & POWER BOM   |  & RESILIENCE   |  FIRMWARE QUEUE  |     FEEDBACK       |  & UNIFIED FIRMWARE   |
+-----------------+-----------------+------------------+--------------------+-----------------------+
| * $0.15 MCUs    | * Binary Frames | * Async Queue    | * Real-time Active | * Push-Button Action  |
|   (CH32V003)    | * CRC8 Checksum | * 100% Action Ack|   Step RGB LEDs    | * Rotary Knob Params  |
| * LiPo + BMS    | * Auto-Discovery| * Auto-Reconnect | * Audio Buzzer     | * Single Shared FW    |
| * Magnetic Pogo | * Bidirectional | * Fall Recovery  | * Error Indication | * Smart End Loopback  |
+-----------------+-----------------+------------------+--------------------+-----------------------+
```

---

## 2. Pillar 1: Hardware & Electrical Optimization

### 1.1 Microcontroller Downsizing (BOM Cost & Power Reduction)
- **Current State**: Every instruction block uses an ESP32 (~$2.50-$3.50), consuming 50-100 mA each. A 10-block chain draws nearly 1 Amp of idle power.
- **Improved Design**:
  - **Master Block**: Keep **ESP32-C3 / ESP32-S3** (~$2.20) for Bluetooth BLE central communication and queue management.
  - **Instruction & Action Blocks**: Migrate to the ultra-low-cost **WCH CH32V003 (32-bit RISC-V)** (~$0.15), or alternatively **ATtiny85** / **STM32C0** (~$0.40).
  - **Power Savings**: Instruction MCUs stay in ultra-low-power sleep (< 10 uA) and wake on UART pin change interrupt.

### 1.2 Unified Firmware Architecture (Single Binary for All Action & End Blocks)
- **One Firmware Binary**: Compile and flash a single unified firmware image across all manufactured blocks.
- **Runtime Role & Mode Detection**:
  - **Smart Multi-Action Block**: Reads user Push Button + Rotary Knob to dynamically set action & parameter.
  - **Dedicated 1-Action Block**: Reads an onboard hardware ID resistor divider on boot to lock into a fixed action.
  - **Smart End Block**: Senses downstream connection state; if no downstream block is present, it acts as the chain terminator, calculates CRC-8, and loops data back to the Return RX rail.

### 1.3 Power Supply & Battery Subsystem
- **Master Battery**: Single-cell LiPo/18650 battery (3.7V, 1500-2200 mAh) with onboard TP4056 USB-C charging circuit and battery protection (BMS).
- **Power Rail Regulation**: High-efficiency synchronous buck-boost converter providing regulated 3.3V across `Pin 1 (V+)` to prevent brownouts across long chains.

### 1.4 Magnetic Pogo Connector & Mechanical Keying
- **Polarity Keying**: Asymmetrical magnetic attraction (North-South pairing) or keyed physical notches to prevent accidental reverse connection.
- **Electrical Protection**: Reverse-polarity Schottky diode on `V+` and 10 kOhm pull-up with 22 pF RC noise filtering on UART data pins to eliminate contact bounce.

---

### 3. Pillar 2: Robust Communication Protocol & Bus Architecture

### 3.1 Protocol Evaluation & Selection Research
To determine the best physical communication method for the modular blocks, 7 candidate protocols were evaluated against four critical system constraints: **Physical Order Auto-Discovery**, **Pogo Pin Count**, **BOM Cost per Block**, and **Hot-Plug / Contact Bounce Resilience**:

| Protocol / Architecture | Pin Count | Auto-Discovers Physical Order? | BOM Cost per Block | Hot-Plug Robustness | GPIOs on MCU | Key Bottleneck / Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Daisy-Chain UART (Point-to-Point + Return Rail)** | **4 Pins** | ✅ **Native** (Data cascades in physical sequence) | **Lowest** (~$0.15 MCU only) | 🟢 **High** (Per-link framing + CRC) | **2 GPIOs** (`RX_IN`, `TX_OUT`) | ⭐ **SELECTED**: Optimal for linear physical order, low pin count, and SOP-8 pin budget. |
| **I2C Bus with Cascade Address Enable** | **5–6 Pins** | ⚠️ Needs cascade lines (`EN_IN` $\to$ `EN_OUT`) | **Medium** (~$0.25 MCU >10 pins) | 🔴 **Low** (SDA hang if pulled low mid-plug) | **4 GPIOs** (`SDA`, `SCL`, `EN_IN`, `EN_OUT`) | High bus capacitance over pogo chains; consumes too many GPIOs for SOP-8. |
| **Pure I2C Multi-Drop (Standard)** | **4 Pins** | ❌ **Impossible** (Cannot tell block sequence) | **Low** (~$0.15) | 🔴 **Low** (Bus hang risk) | **2 GPIOs** (`SDA`, `SCL`) | Address collision (multiple identical "Walk" blocks share same I2C address). |
| **SPI Daisy-Chain (Shift-Register Mode)** | **5–6 Pins** | ✅ **Native** (Bit shifting through chain) | **Low–Med** (~$0.20) | 🔴 **Very Low** (Single glitch shifts all bits) | **4 GPIOs** (`MOSI`, `MISO`, `SCK`, `CS`) | High-speed clock line (`SCK`) radiates EMI over pogo pins; contact bounce corrupts stream. |
| **1-Wire / MicroLAN (Dallas/Maxim style)** | **3 Pins** | ⚠️ Needs sequential cascade FET switches | **High** (~$0.60+ switch silicon) | 🟡 **Medium** (Timing critical) | **2 GPIOs** (`DQ`, `CASCADE`) | Bit-banging timing conflicts with WS2812B LED timing interrupts. |
| **CAN Bus / CAN-FD** | **4 Pins** | ❌ **Impossible** without cascade line | **Very High** (~$0.80+ transceiver IC) | 🟢 **Extreme** (Differential noise immunity) | **2 GPIOs** + Transceiver | Overkill cost; no CH32V003 hardware CAN support. |
| **Analog Resistor Ladder (Passive)** | **3 Pins** | ⚠️ Limited sequence resolution | **Lowest** (Resistors only) | 🟡 **Medium** (Contact resistance shifts ADC) | **1 ADC Pin** | Max 4–6 blocks before ADC quantization error & resistor tolerances fail. |

**Conclusion**: **Daisy-Chain UART** is the optimal topology. It naturally solves physical spatial ordering without requiring complex address arbitration or extra cascade GPIO lines, keeping the connector at a standard, reliable 4-pin magnetic interface.

---

### 3.2 Enhanced 2-Phase Bi-Directional UART Protocol
To overcome the one-way limitation of traditional daisy-chain UART and enable **real-time active LED feedback** while the robot moves, the system implements an **Enhanced 2-Phase Protocol**:

```
+───────────────────────────────────────────────────────────────────────────────────────────────────+
| 4-PIN CONNECTOR INTERFACE:                                                                        |
|   Pin 1: V+ (Regulated 3.3V Power Rail)                                                           |
|   Pin 2: GND (Common System Ground)                                                               |
|   Pin 3: UART TX_DOWN (Point-to-Point Downstream Link: Master -> Block 1 -> Block 2 ... -> End)  |
|   Pin 4: UART RX_BUS (Continuous Return Rail & Real-Time Broadcast Feedback Bus)                 |
+───────────────────────────────────────────────────────────────────────────────────────────────────+
```

```mermaid
sequenceDiagram
    autonumber
    participant Master as Master Block (ESP32)
    participant B1 as Block 1 (Walk)
    participant B2 as Block 2 (Punch)
    participant End as End Block (Loopback)

    Note over Master,End: PHASE 1: DISCOVERY & PROGRAM COMPILATION (FORWARD PIPELINE)
    Master->>B1: Frame [0xAA, Len=0, Count=0, CRC] (Pin 3 TX)
    Note over B1: Sets MyIndex = 1<br/>Appends: ID=0x01, Param=3 steps<br/>Increments Count = 1
    B1->>B2: Frame [0xAA, Len=2, Count=1, 0x01, 0x03, CRC]
    Note over B2: Sets MyIndex = 2<br/>Appends: ID=0x10, Param=1 combo<br/>Increments Count = 2
    B2->>End: Frame [0xAA, Len=4, Count=2, 0x01, 0x03, 0x10, 0x01, CRC]
    End->>Master: Loopback Frame over Pin 4 (Return RX Rail)

    Note over Master,End: PHASE 2: REAL-TIME EXECUTION BROADCAST (RETURN BUS)
    Master->>Master: BLE Send Walk 3 Steps -> Robot
    Master-->>B1: Broadcast [0xBB, ActiveStep=1, CRC] (Pin 4 RX_BUS)
    Note over B1: MyIndex(1) == ActiveStep(1) -> Glows Bright Green!
    Note over B2: MyIndex(2) != ActiveStep(1) -> Displays Mode Color (Red)
    Master->>Master: Robot Emits 100% Progress ACK
    Master-->>B2: Broadcast [0xBB, ActiveStep=2, CRC] (Pin 4 RX_BUS)
    Note over B1: Reverts to Mode Color (Blue)
    Note over B2: MyIndex(2) == ActiveStep(2) -> Glows Bright Green!
    Master->>Master: Program Completed -> Piezo Victory Fanfare
```

---

### 3.3 Binary Frame Structures & CRC-8 Verification

All serial communications utilize binary frames protected by **CRC-8** (Polynomial: $x^8 + x^2 + x + 1$, `0x07`):

#### 1. Discovery & Compilation Frame (`Header = 0xAA`)
Transmitted downstream from Master through each block to compile the user program:
```
+-------------+------------+-------------+-----------+-------------+-----------+-------------+--------+-------------+
| HEADER      | PACKET LEN | BLOCK COUNT | BLOCK 1   | PARAMETER 1 | BLOCK 2   | PARAMETER 2 | CRC-8  | FOOTER      |
| 1 Byte: 0xAA| 1 Byte (N) | 1 Byte (K)  | 1 Byte ID | 1 Byte Val  | 1 Byte ID | 1 Byte Val  | 1 Byte | 1 Byte: 0x55|
+-------------+------------+-------------+-----------+-------------+-----------+-------------+--------+-------------+
```

#### 2. Live Step Execution Broadcast Frame (`Header = 0xBB`)
Broadcast by the Master across Pin 4 during BLE robot movement to trigger live step LEDs:
```
+-------------+-------------+-------------+--------+-------------+
| HEADER      | ACTIVE STEP | TOTAL STEPS | CRC-8  | FOOTER      |
| 1 Byte: 0xBB| 1 Byte (1-N)| 1 Byte (N)  | 1 Byte | 1 Byte: 0x55|
+-------------+-------------+-------------+--------+-------------+
```
- `ACTIVE STEP = 0x00`: Standby / Idle (all blocks show selected action color).
- `ACTIVE STEP = 0x01..0xFE`: The specific block index that is currently executing turns **bright pulsing green**.
- `ACTIVE STEP = 0xFF`: Program Complete / Victory state (all blocks flash green).

#### 3. System Reset / Mode Sync Frame (`Header = 0xCC`)
Broadcast to clear block indexes or force parameter re-evaluation.

---

### 3.4 Token ID & Parameter Mapping Table

| Token ID | Command Name | Parameter (1 Byte) | Robosen BLE Mapping | Default LED Color |
| :---: | :--- | :--- | :--- | :---: |
| `0x01` | `MOVE_FORWARD` | Steps (`1`–`10`) / Duration | Opcode `0x01` (Walk Forward) | 🔵 Blue |
| `0x02` | `MOVE_BACKWARD` | Steps (`1`–`10`) / Duration | Opcode `0x05` (Walk Backward) | 🔵 Dark Blue |
| `0x03` | `TURN_LEFT` | Angle (`45°`, `90°`, `135°`, `180°`) | Opcode `0x08` (Turn Left) | 🔷 Cyan |
| `0x04` | `TURN_RIGHT` | Angle (`45°`, `90°`, `135°`, `180°`) | Opcode `0x02` (Turn Right) | 🔷 Cyan |
| `0x07` | `MOVE_LEFT` | Side-steps (`1`–`5`) | Opcode `0x07` (Step Left) | 🟦 Sky Blue |
| `0x08` | `MOVE_RIGHT` | Side-steps (`1`–`5`) | Opcode `0x03` (Step Right) | 🟦 Sky Blue |
| `0x10` | `LEFT_PUNCH` | Strike Style (`0`–`3`) | Opcode `0x17` (`"ProAction/Left Punch"`) | 🔴 Red |
| `0x11` | `RIGHT_PUNCH` | Strike Style (`0`–`3`) | Opcode `0x17` (`"ProAction/Right Punch"`) | 🔴 Bright Red |
| `0x12` | `KUNG_FU` | Routine Variant | Opcode `0x17` (`"ProAction/Kung Fu"`) | 🟠 Orange |
| `0x13` | `DANCE_BOOGALOO`| Track Variant | Opcode `0x17` (`"Action/Boogaloo"`) | 🟣 Magenta |
| `0x14` | `PUSH_UPS` | Repetitions (`1`–`3`) | Opcode `0x17` (`"ProAction/Push Ups"`) | 🟤 Amber |
| `0x15` | `HANDSTAND` | Balance Duration | Opcode `0x17` (`"ProAction/Handstand"`) | 🟤 Amber |
| `0x20` | `HEAD_MOVE` | Head Angle (`42`–`202`) | Opcode `0xE8` (Servo index 16) | 🩵 Teal |
| `0x30` | `WAIT_DELAY` | Seconds (`1`–`5`s) | Master delay timer | 🟡 Yellow |
| `0x40` | `REPEAT_LOOP` | Iterations (`2x`–`5x`) | Master queue repeat sub-loop | 🟢 Lime |

---

## 4. Pillar 3: Master ESP32 Firmware & Robosen BLE Engine

### 4.1 Non-Blocking Asynchronous Command Queue
The Master ESP32 coordinates the robot actions and feeds execution states back to the physical blocks:

```
[ Master Receives Return Program (0xAA) via Pin 4 RX ]
                       │
                       ▼
             [ Verify CRC-8 Checksum ]
                       │
                       ▼
┌──────────────────────┴────────────────────────────────────────────────┐
│ FOR EACH COMMAND (Step Index = 1 to N):                                │
│                                                                       │
│  1. Broadcast Step State: Send [0xBB, StepIndex, N, CRC] on Pin 4     │
│     -> Target physical block turns bright green immediately           │
│                                                                       │
│  2. Dispatch Robosen BLE Command:                                     │
│     - If Action (0x17): Send BLE frame, listen on 0xFFE1 for progress │
│       Wait asynchronously until Progress Byte === 100% (0x64)         │
│     - If Locomotion (0x01-0x08): Start precision hardware timer       │
│       When timer expires, send Stop frame (0x0C)                      │
│     - If Delay (0x30): Run master sleep timer                         │
│                                                                       │
│  3. Stabilization Buffer: 300-500ms posture stabilization             │
└──────────────────────┬────────────────────────────────────────────────┘
                       │
                       ▼
 [ Broadcast [0xBB, 0xFF, N] (Victory Fanfare on Buzzer & All LEDs Green) ]
```

### 4.2 BLE Connection Management
- Auto-discovery on Service `0xFFE0` with Local Name filter (`"K1"`).
- Persistent keep-alive handshake (`0x0B`) every 5 seconds when idle.
- Automatic reconnection with exponential backoff on signal drop.
- Telemetry monitoring: battery voltage, volume, and fall-recovery status via Opcode `0x0F`.

---

## 5. Pillar 4: Visual & Auditory User Experience (UX)

### 5.1 Real-Time Step-by-Step LED Tracking
Each block features an addressable **WS2812B RGB LED**:
- **Idle / Configuration State**: Displays the block's chosen action color (Blue, Cyan, Red, Orange, Magenta, Yellow).
- **Parameter Confirmation**: Flashes $N$ times corresponding to the knob setting (e.g., 3 flashes = 3 steps).
- **Active Step Execution**: **Bright pulsating Green (100% brightness)** while the robot is physically performing that step.
- **Error / Disconnect State**: **Rapid pulsing Red** if a CRC error or broken loopback is detected.

### 5.2 Audio Chimes & Sound Effects (Master Block Piezo Buzzer)
- **Snap-in Click**: Low subtle click tone when a new block is detected.
- **Start Chime**: 3-tone ascending major chord when Start button is pressed.
- **Step Tick**: Soft high-pitch blip as execution advances from one block to the next.
- **Victory Fanfare**: 5-note celebratory melody when the complete sequence finishes.
- **Error Warning**: 2 low buzzes on invalid CRC or BLE disconnection.

---

## 6. Pillar 5: Smart Multi-Action Blocks & Control Hardware

```
+────────────────────────────────────────────────────────────────────────────────────────+
|                          SMART MULTI-ACTION BLOCK HARDWARE                             |
+──────────────────────────+───────────────────────────+─────────────────────────────────+
| 1. PUSH BUTTON           | 2. ROTARY KNOB            | 3. WS2812B RGB LED FEEDBACK     |
| (Action Selector)        | (Parameter Adjuster)      | (Real-time Visual Status)       |
+──────────────────────────+───────────────────────────+─────────────────────────────────+
| * Click: Cycle Action    | * Potentiometer (ADC)     | * Color: Active Action Mode     |
|   Walk -> Turn -> Punch  | * Adjust: Steps (1-10)    | * Pulse: Parameter Value        |
| * Long Press: Reset/Mode | * Adjust: Angle (45°-180°)| * Bright Green: Step Executing  |
| * Debounced (20ms)       | * Adjust: Delay (1-5s)    | * Red Flash: Error / Disconnect |
+──────────────────────────+───────────────────────────+─────────────────────────────────+
```

### 6.1 User Interaction Model
1. **Push Button (Action Selector)**:
   - User presses the tactile button to cycle through available robot actions.
   - Each press advances the internal mode index and updates the RGB LED color immediately.
2. **Rotary Knob (Parameter Adjuster)**:
   - User rotates the knob (10 kΩ potentiometer read via CH32V003 10-bit ADC or EC11 rotary encoder) to increase or decrease the value.
   - Firmware applies a 5-sample moving average with hysteresis window to eliminate analog jitter.

### 6.2 CH32V003 Microcontroller Pinout (SOP-8 Package)
All functions (Button, Knob ADC, Status LED, and Daisy-Chain UART) fit perfectly into the 8-pin package:

```
                       CH32V003 (SOP-8 Package)
                             +-------------+
             (V+ 3.3V)    ---| 1 VDD 8 GND |----  (GND)
      (Push Button) [PA1]  ---| 2 PA1 7 PC4 |----  (Rotary Knob ADC)
    (WS2812B LED)   [PA2]  ---| 3 PA2 6 PD6 |----  (UART RX - Pin 3 In)
          (Debug / NRST)  ---| 4 PD1 5 PD5 |----  (UART TX - Pin 3 Out)
                             +-------------+
```

---

## 7. Phased Implementation Roadmap

| Phase | Milestone | Focus Areas | Deliverables |
| :---: | :--- | :--- | :--- |
| **Phase 1** | **2-Phase Protocol & Master Firmware** | Master ESP32 async queue, BLE 100% ACK listener, 2-phase binary framing (`0xAA`/`0xBB`) | Complete ESP32 Arduino/IDF firmware |
| **Phase 2** | **CH32V003 Unified Slave Firmware** | Single firmware binary, button debouncing, knob ADC hysteresis, sleep wake on RX interrupt | C/C++ RISC-V firmware (MounRiver/WCH) |
| **Phase 3** | **Interactive UX & Feedback** | Push-button cycling, WS2812B real-time color feedback, buzzer sound effects | Integrated LED & buzzer state machine |
| **Phase 5** | **Smart Enclosure & Integration** | 3D snap enclosures for knob/button, End Block active loopback testing | 3D CAD (.STL/.STEP) + Complete Kit |

