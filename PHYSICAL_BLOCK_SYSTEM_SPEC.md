# Tangible Modular Coding Block System for Robosen Robot Control

> **Document Version:** 2.0  
> **Target Hardware:** Physical Modular Programming Blocks (ESP32 Master + CH32V003 Slaves) $\longleftrightarrow$ Robosen K1 Humanoid Robot (Bluetooth BLE)

---

## 1. System Overview

This project is a **tangible / physical block-based programming system** designed to control the Robosen humanoid robot without a screen or computer. 

Users physically snap together modular code blocks in a linear sequence to create an algorithmic program. When the user presses the **Start Button** on the Master Block:
1. **Phase 1 (Discovery & Compilation)**: A binary seed frame (`0xAA`) is transmitted down the daisy chain. Each connected instruction block appends its unique token ID & rotary parameter, increments the block count, and records its own index. The complete program loops back at the End Block over the shared Return RX rail to the Master Block.
2. **Phase 2 (Execution & Live Feedback)**: The Master Block parses each command, dispatches **Robosen Bluetooth Low Energy (BLE) protocol packets** to the physical robot, and simultaneously broadcasts the active step index (`0xBB`) across the return rail so the corresponding physical block's **WS2812B RGB LED pulses bright green** in real time.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       PHYSICAL HARDWARE CHAIN                                          │
│                                                                                                        │
│  [ MASTER BLOCK ] ──Pin 3 (TX)──► [ INSTRUCTION BLOCK 1 ] ──Pin 3 (TX)──► [ END BLOCK (Loopback) ]     │
│  - Battery & BMS                   - CH32V003 ($0.15 RISC-V)       ▲          - Loopback Bridge        │
│  - Power Switch                    - Button + Knob + WS2812B LED   │            (Pin 3 TX ─► Pin 4 RX) │
│  - Start Button                    - Pin In (RX) & Pin Out (TX)    │                                   │
│  - Master ESP32                                                    │                                   │
│         ▲                                                          │                                   │
│         └─────────────────────── Pin 4 (Return RX & Broadcast Bus) ┴───────────────────────────────────┘
│                                            │
│                                 Binary Program Return (0xAA)
│                                 & Real-Time LED Broadcast (0xBB)
│                                            │
│                                            ▼
│                              [ MASTER ESP32 PARSER ]
│                         - Verifies CRC-8 Checksum
│                         - Asynchronous Queue Engine with 100% ACK
│                                            │
│                                            ▼ (Bluetooth Low Energy)
│                                  [ ROBOSEN K1 ROBOT ]
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Block Hardware Specifications

### Block 1: Master Block (Start / Controller Block)
The Master Block is the brain, power station, and BLE gateway of the physical system.

- **Onboard Components**:
  1. **Rechargeable Battery**: 3.7V 18650/LiPo with TP4056 USB-C charging and BMS protection.
  2. **Buck-Boost Regulator**: High-efficiency 3.3V power rail delivery.
  3. **Main Power Switch & Start Button**: Tactile user inputs.
  4. **Audio Feedback**: Miniature piezo buzzer for start, step ticks, and victory chimes.
  5. **4-Pin Magnetic Pogo Connector (Pin Out)**: Polarized magnetic interface.
  6. **Master ESP32 Microcontroller (ESP32-C3 / S3)**:
     - Drives the 2-phase UART protocol.
     - Operates as a **Bluetooth BLE Central Client** (`Service: 0xFFE0`, `Char: 0xFFE1`).
     - Coordinates asynchronous execution queue with dynamic 100% action ACK resolution.

---

### Block 2: Smart Instruction Blocks (Command Modules)
Each instruction block physically represents one modular command and features an interactive button and parameter dial.

- **Onboard Components**:
  1. **Microcontroller**: Ultra-low-cost **WCH CH32V003** (32-bit RISC-V, SOP-8 package, ~$0.15).
  2. **Push Button (Action Selector)**: Cycles through action modes (Walk $\to$ Turn $\to$ Punch $\to$ Kung Fu $\to$ Dance $\to$ Delay).
  3. **Rotary Knob (Parameter Adjuster)**: 10 kΩ potentiometer read via 10-bit ADC to set step counts, angles, or durations.
  4. **WS2812B RGB LED**: Real-time visual feedback (Mode color, parameter flash count, bright pulsating green when active).
  5. **Pin In (4-Pin Pogo Connector)**: Receives `V+`, `GND`, upstream `UART TX`, and passes through `Return RX`.
  6. **Pin Out (4-Pin Pogo Connector)**: Transmits `V+`, `GND`, downstream `UART TX`, and passes through `Return RX`.

---

### Block 3: End Block (Termination Module)
The End Block marks the physical end of the user's code sequence.

- **Variants**:
  1. **Passive End Block**: Contains an internal electrical bridge connecting **Pin 3 (`UART TX`) directly to Pin 4 (`UART RX`)**.
  2. **Smart End Block**: Contains a CH32V003 MCU that senses end-of-chain, auto-calculates CRC-8, and displays a green "Ready" status LED.

---

## 3. 4-Pin Pogo Connector Pinout & Electrical Layout

All blocks share a standardized 4-pin pogo pin connector layout:

| Pin # | Signal Name | Type | Description |
| :---: | :--- | :---: | :--- |
| **Pin 1** | **`V+`** | Power | Regulated 3.3V power rail supplied by Master Block |
| **Pin 2** | **`GND`** | Power | Common system ground |
| **Pin 3** | **`UART TX_DOWN`** | Data Out | Downstream serial link (Master $\to$ Block 1 $\to$ Block 2 $\dots \to$ End) |
| **Pin 4** | **`UART RX_BUS`** | Bidirectional Bus | Continuous return rail & active step broadcast bus |

```
                ┌────────────────────────────────┐
                │ 4-PIN POGO PIN CONNECTOR       │
                │                                │
                │  (1) [ V+ 3.3V ] (Power)       │
                │  (2) [ GND ]     (Ground)      │
                │  (3) [ TX_DOWN ] (Downstream)  │
                │  (4) [ RX_BUS ]  (Return Rail) │
                └────────────────────────────────┘
```

---

## 4. 2-Phase Protocol & Signal Flow

### Phase 1: Discovery & Program Compilation (`0xAA`)
1. User presses **Start Button** on Master Block.
2. Master transmits Seed Frame: `[0xAA, Len=0, Count=0, CRC, 0x55]` on **Pin 3**.
3. **Block 1** receives frame, records its own address as `Index = 1`, appends its `Token ID` and `Parameter Byte`, increments `Count = 1`, and forwards downstream to **Block 2**.
4. **Block 2** records `Index = 2`, appends its data, increments `Count = 2`, and forwards downstream.
5. The **End Block** loops the complete binary packet into **Pin 4 (Return RX)** directly back to the Master Block.
6. Master verifies the **CRC-8 checksum**.

### Phase 2: Execution & Real-Time Broadcast (`0xBB`)
1. Master iterates through the compiled command queue from Step 1 to $N$.
2. For each step, Master broadcasts `[0xBB, StepIndex, TotalSteps, CRC, 0x55]` across **Pin 4**:
   - The block matching `StepIndex` turns its **WS2812B LED bright pulsating green**.
   - All other blocks remain in their normal mode colors.
3. Master sends the corresponding **Robosen BLE packet** to the K1 robot and waits for completion:
   - **Actions (`0x17`)**: Listens on BLE Characteristic `0xFFE1` until progress reaches $100\%$ (`0x64`).
   - **Locomotion (`0x01`–`0x08`)**: Runs hardware step timer, then sends Stop (`0x0C`).
4. Master advances to the next step until all blocks are complete.
5. Master sounds a victory fanfare and broadcasts `[0xBB, 0xFF]` to flash all LEDs green.

---

## 5. Command Token Mapping Table

| Token ID | Command Name | Parameter (1 Byte) | Robosen Opcode | Payload / BLE Frame | Default LED Color |
| :---: | :--- | :--- | :---: | :--- | :---: |
| `0x01` | `MOVE_FORWARD` | Steps (`1`–`10`) | `0x01` | `ffff020103` + Stop | 🔵 Blue |
| `0x02` | `MOVE_BACKWARD` | Steps (`1`–`10`) | `0x05` | `ffff020507` + Stop | 🔵 Dark Blue |
| `0x03` | `TURN_LEFT` | Angle (`45°`, `90°`, `135°`, `180°`) | `0x08` | `ffff02080a` + Stop | 🔷 Cyan |
| `0x04` | `TURN_RIGHT` | Angle (`45°`, `90°`, `135°`, `180°`) | `0x02` | `ffff020204` + Stop | 🔷 Cyan |
| `0x07` | `MOVE_LEFT` | Side-steps (`1`–`5`) | `0x07` | `ffff020709` + Stop | 🟦 Sky Blue |
| `0x08` | `MOVE_RIGHT` | Side-steps (`1`–`5`) | `0x03` | `ffff020305` + Stop | 🟦 Sky Blue |
| `0x10` | `LEFT_PUNCH` | Style Variant | `0x17` | `"ProAction/Left Punch"` | 🔴 Red |
| `0x11` | `RIGHT_PUNCH` | Style Variant | `0x17` | `"ProAction/Right Punch"` | 🔴 Bright Red |
| `0x12` | `KUNG_FU` | Routine Variant | `0x17` | `"ProAction/Kung Fu"` | 🟠 Orange |
| `0x13` | `DANCE_BOOGALOO`| Track Variant | `0x17` | `"Action/Boogaloo"` | 🟣 Magenta |
| `0x14` | `PUSH_UPS` | Repetitions (`1`–`3`) | `0x17` | `"ProAction/Push Ups"` | 🟤 Amber |
| `0x15` | `HANDSTAND` | Duration | `0x17` | `"ProAction/Handstand"` | 🟤 Amber |
| `0x20` | `HEAD_MOVE` | Angle (`42`–`202`) | `0xE8` | 25-byte struct (Head: pan) | 🩵 Teal |
| `0x30` | `WAIT_DELAY` | Seconds (`1`–`5`s) | Master delay | Master sleep timer | 🟡 Yellow |
| `0x40` | `REPEAT_LOOP` | Iterations (`2x`–`5x`) | Master loop | Sub-queue repeat | 🟢 Lime |

