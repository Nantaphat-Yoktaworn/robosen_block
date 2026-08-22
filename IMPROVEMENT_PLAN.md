# Tangible Modular Coding Block System: Master Improvement Plan

> **Project:** Physical Modular Programming Blocks $\longleftrightarrow$ Robosen K1 Humanoid Robot  
> **Goal:** High reliability, low-cost bill of materials (BOM), robust Bluetooth BLE execution, and engaging tactile STEM learning experience.

---

## 1. Executive Summary & Improvement Pillars

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    5-PILLAR IMPROVEMENT PLAN                                      │
├─────────────────┬─────────────────┬──────────────────┬────────────────────┬───────────────────────┤
│   1. HARDWARE   │   2. PROTOCOL   │   3. MASTER BLE  │   4. UX & VISUAL   │    5. NEW BLOCK       │
│   & POWER BOM   │  & RESILIENCE   │  FIRMWARE QUEUE  │     FEEDBACK       │      CATEGORIES       │
├─────────────────┼─────────────────┼──────────────────┼────────────────────┼───────────────────────┤
│ • $0.15 MCUs    │ • Binary Frames │ • Async Queue    │ • Real-time Active │ • Parameter Dials     │
│ • LiPo + BMS    │ • CRC8 / CRC16  │ • 100% Action Ack│   Step RGB LEDs    │ • Loop / Repeat 3x    │
│ • Magnetic Pogo │ • Auto-Discovery│ • Auto-Reconnect │ • Audio Buzzer     │ • Ultrasonic Sensors  │
│ • Reverse Diode │ • Bidirectional │ • Fall Recovery  │ • Error Indication │ • Direct Servo Blocks │
└─────────────────┴─────────────────┴──────────────────┴────────────────────┴───────────────────────┘
```

---

## 2. Pillar 1: Hardware & Electrical Optimization

### 1.1 Microcontroller Downsizing (BOM Cost & Power Reduction)
- **Current State**: Every instruction block uses an ESP32 ($~\$2.50–\$3.50$), consuming 50–100 mA each. A 10-block chain draws nearly 1 Amp of idle power.
- **Improved Design**:
  - **Master Block**: Keep **ESP32-C3 / ESP32-S3** ($~\$2.20$) for Bluetooth BLE central communication and queue management.
  - **Instruction Blocks**: Migrate to ultra-low-cost, low-power microcontrollers such as the **WCH CH32V003 (RISC-V)** ($~\$0.15$), **ATtiny85**, or **STM32C0** ($~\$0.40$).
  - **Power Savings**: Instruction MCUs stay in ultra-low-power sleep ($< 10\,\mu\text{A}$) and wake on UART pin change.

### 1.2 Power Supply & Battery Subsystem
- **Master Battery**: Single-cell LiPo/18650 battery ($3.7\text{V}$, $1500–2200\text{ mAh}$) with onboard TP4056 USB-C charging circuit and battery protection (BMS).
- **Power Rail Regulation**: High-efficiency synchronous buck-boost converter providing regulated $3.3\text{V}$ across `Pin 1 (V+)` to prevent brownouts across long chains.

### 1.3 Magnetic Pogo Connector & Mechanical Keying
- **Polarity Keying**: Asymmetrical magnetic attraction (North-South pairing) or keyed physical notches to prevent accidental reverse connection.
- **Electrical Protection**: Reverse-polarity Schottky diode on `V+` and $10\text{k}\Omega$ pull-up with $22\text{pF}$ RC noise filtering on UART data pins to eliminate contact bounce.

---

## 3. Pillar 2: Robust Communication Protocol & Bus Architecture

### 3.1 Binary Token Framing with CRC8
Replace plain text strings (`"start,move_forward,..."`) with structured binary packets:

```
┌─────────────┬────────────┬─────────────┬───────────┬─────────────┬───────────┬────────┬─────────────┐
│ HEADER      │ PACKET LEN │ BLOCK COUNT │ BLOCK 1   │ PARAMETER 1 │ BLOCK 2   │ CRC-8  │ FOOTER      │
│ 1 Byte: 0xAA│ 1 Byte     │ 1 Byte      │ 1 Byte    │ 1 Byte      │ ...       │ 1 Byte │ 1 Byte: 0x55│
└─────────────┴────────────┴─────────────┴───────────┴─────────────┴───────────┴────────┴─────────────┘
```

#### Token ID Mapping Table:
| Token ID | Command | Parameter (1 Byte) | Robosen Mapping |
| :---: | :--- | :--- | :--- |
| `0x01` | `MOVE_FORWARD` | Duration (e.g. $1–10\text{s}$ or steps) | Opcode `0x01` (Walk Forward) |
| `0x02` | `MOVE_BACKWARD` | Duration | Opcode `0x05` (Walk Backward) |
| `0x03` | `TURN_LEFT` | Angle / Time | Opcode `0x08` (Turn Left) |
| `0x04` | `TURN_RIGHT` | Angle / Time | Opcode `0x02` (Turn Right) |
| `0x10` | `LEFT_PUNCH` | None | Opcode `0x17` (`"ProAction/Left Punch"`) |
| `0x11` | `RIGHT_PUNCH` | None | Opcode `0x17` (`"ProAction/Right Punch"`) |
| `0x12` | `KUNG_FU` | None | Opcode `0x17` (`"ProAction/Kung Fu"`) |
| `0x13` | `DANCE_BOOGALOO`| None | Opcode `0x17` (`"Action/Boogaloo"`) |
| `0x20` | `HEAD_MOVE` | Angle ($42–202$) | Opcode `0xE8` (Servo index 16) |
| `0x30` | `WAIT_DELAY` | Seconds ($1–10$) | Master delay timer |

---

## 4. Pillar 3: Master ESP32 Firmware & Robosen BLE Engine

### 4.1 Non-Blocking Asynchronous Command Queue
The Master ESP32 handles commands sequentially with state synchronization:

```
[ Master Receives Return Program ]
               │
               ▼
[ Parse Command Queue ]
               │
               ▼
┌──────────────┴────────────────────────────────────────────────────────┐
│ FOR EACH COMMAND IN QUEUE:                                            │
│                                                                       │
│  1. Send Robosen BLE Command Packet                                   │
│  2. If Action (Opcode 0x17):                                          │
│     - Listen on Characteristic 0xFFE1 for progress packet             │
│     - Wait until Progress Byte === 100% (0x64)                        │
│  3. If Locomotion (Opcodes 0x01-0x08):                                │
│     - Start non-blocking hardware timer for duration parameter        │
│     - When timer expires, send Stop Packet (0x0C)                     │
│  4. Apply 300-500ms stabilization buffer before next command          │
└──────────────┬────────────────────────────────────────────────────────┘
               │
               ▼
   [ All Blocks Completed ]
```

### 4.2 BLE Connection Management
- Auto-discovery on Service `0xFFE0` with Local Name filter (`"K1"`).
- Automatic reconnection on signal drop.
- Battery telemetry monitoring via `0x0F` state queries.

---

## 5. Pillar 4: Visual & Auditory User Experience (UX)

### 5.1 Real-Time Step-by-Step LED Tracking
- Add a **WS2812B RGB LED** to each block:
  - **Connected / Idle**: Soft color coded by category (Locomotion = Blue, Action = Orange, Logic = Purple).
  - **Currently Executing**: **Bright pulsating Green** on the block currently being performed by the robot.
  - **Error State**: Flashing Red on communication fault.

### 5.2 Audio Chimes & Haptic Feedback (Master Block)
- Miniature piezo buzzer providing feedback:
  - Connect click sound when a block is snapped in.
  - 3-tone ascending start chime on Start button press.
  - Cheerful victory fanfare on program completion.
  - Low-battery warning buzz.

---

## 6. Pillar 5: Next-Generation Physical Block Modules

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              NEW PHYSICAL BLOCK MODULES                                │
├──────────────────────────┬───────────────────────────┬─────────────────────────────────┤
│ 1. PARAMETER DIAL BLOCKS │ 2. CONTROL FLOW & LOOPS   │ 3. SENSOR TRIGGER BLOCKS        │
├──────────────────────────┼───────────────────────────┼─────────────────────────────────┤
│ • Walk Step Dial (1-5)   │ • Repeat 2x / 3x / 5x     │ • Ultrasonic Obstacle (Distance)│
│ • Turn Angle (45°-180°)  │ • Loop Start & Loop End   │ • Clapping / Sound Sensor       │
│ • Speed Selector Switch  │ • Random Action Module    │ • Tilt / Orientation Sensor     │
└──────────────────────────┴───────────────────────────┴─────────────────────────────────┘
```

1. **Parameter / Selector Dial Blocks**:
   - Integrated 3-way slider switch or potentiometer to adjust parameters (e.g. `Walk: 1 step / 3 steps / 5 steps`, `Head: -45° / 0° / +45°`).
2. **Loop & Branching Logic Blocks**:
   - `Repeat [N]x` block: Master executes enclosed block sub-sequences $N$ times.
3. **Interactive Sensor Blocks**:
   - `Ultrasonic Obstacle Block`: Reads distance; Master triggers conditional avoidance maneuvers if an obstacle is closer than $20\text{ cm}$.

---

## 7. Phased Implementation Roadmap

| Phase | Milestone | Focus Areas | Deliverables |
| :---: | :--- | :--- | :--- |
| **Phase 1** | **Protocol & Master BLE Firmware** | Master ESP32 async queue, BLE ACK listener, binary framing | Complete ESP32 Arduino/IDF firmware |
| **Phase 2** | **Instruction Block MCU Migration** | Port instruction code to CH32V003/ATtiny, sleep power modes | C firmware + breadboard test bench |
| **Phase 3** | **PCB & Hardware Reliability** | Magnetic 4-pin pogo, debouncing, reverse protection, BMS | Custom PCB layout files (Gerbers) |
| **Phase 4** | **Interactive UX & Feedback** | Active-step RGB LED animations, buzzer sound effects | Integrated LED protocol |
| **Phase 5** | **Advanced Blocks & Enclosure** | Parameter dial blocks, Repeat loops, 3D snap enclosures | 3D CAD (.STL/.STEP) + Logic firmware |
