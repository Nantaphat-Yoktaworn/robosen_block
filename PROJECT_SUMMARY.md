# Robosen Tangible Coding Block System: Comprehensive Project Summary & Scope

> **Project Name:** Tangible Modular Coding Block System for Robosen Robot  
> **Target Demographic:** Children aged 7 years old and under (Early Childhood / Kindergarten to Early Elementary)  
> **Core Purpose:** Screenless physical block-based coding to teach computational thinking, algorithm sequencing, and cause-and-effect through interactive humanoid robot control.  
> **Target Hardware:** Modular Physical Blocks (ESP32-S3 Master with E-Ink Config Dock + CH32V003 Slaves) $\longleftrightarrow$ Robosen K1 Humanoid Robot (Bluetooth Low Energy)  
> **Date:** August 2026  

---

## 1. Project Scope & Educational Mission

### 1.1 The Core Problem
Most modern coding curricula for children rely on tablets, smartphones, or computers (e.g., Scratch, Blockly). However, for **young children aged 7 and under**, screens present significant developmental hurdles:
- **Abstract vs. Concrete Cognition:** Children under 7 (Piaget’s Preoperational and early Concrete Operational stages) learn best through tactile, physical manipulation rather than abstract 2D screen coordinates.
- **Screen Fatigue & Distraction:** Excessive screen time can cause disengagement and cognitive overload.
- **Disconnected Output:** Controlling a virtual sprite on a screen does not provide the same visceral spatial awareness and excitement as watching a physical robot walk, punch, and balance in the real world.

### 1.2 The Project Solution: Tangible Modular Coding Blocks
This project creates a **tangible, screenless, modular programming system**. Children configure solid coding blocks on the Master's **Config Dock**, then snap them together in a line at the **Run Port**. When they press the **Green "Go / Confirm" Button** on the Master Block, the sequence compiles instantly and commands the **Robosen K1 humanoid robot** via Bluetooth Low Energy (BLE). Pressing the **Red "Stop / Cancel" Button** halts execution immediately or cancels the current action.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PHYSICAL TANGIBLE CODING CHAIN                                 │
│                                                                                                  │
│   [ MASTER BLOCK ] ──► [ WALK BLOCK ] ──► [ TURN BLOCK ] ──► [ PUNCH BLOCK ] ──► [ END BLOCK ]   │
│   (Brain, Battery,     (Param: 3 steps)   (Param: 90° Right) (Action: Left Hook) (Terminator)    │
│    E-Ink Display,                                                                                │
│    2 Config Knobs,                                                                               │
│    Dual UI Buttons)                                                                              │
│          │                                                                                       │
│          ▼ (Bluetooth BLE 4.2 / 5.0 Stream)                                                      │
│   [ ROBOSEN K1 HUMANOID ROBOT ] ─── Executes commands step-by-step with real-time feedback!      │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Key Foundational Coding Concepts Taught (Ages $\le 7$)
1. **Linear Sequence & Order of Execution:**  
   Children learn that computers/robots follow instructions strictly in order from left to right. Swapping the position of the *Walk* and *Punch* blocks changes what the robot does.
2. **Parameters & Modifiers (Master Block Rotary Dials & E-Ink):**  
   Children discover that actions have properties. Turning the physical dial on the Master dock updates the E-Ink display and flashes the block memory to set *how many steps* to walk (1 to 10), *what angle* to turn (45° to 180°), or *how many seconds* to wait.
3. **Real-Time Cause-and-Effect (Active Step Tracking):**  
   As the robot performs each action, the corresponding physical block **glows bright pulsating green**. The child can look at the glowing block, look at the robot moving, and instantly map the block to the physical motion.
4. **Debugging & Algorithmic Thinking:**  
   If the robot bumps into a toy or turns the wrong way, the child physically inspects the chain, identifies the incorrect block, snaps in the right one, and tries again.
5. **Loops & Repetition (Pattern Recognition):**  
   Introducing repeat blocks to understand that repeating an action is more efficient than chaining many identical blocks.

---

## 2. System Architecture & Physical Hardware Components

![Robosen Block System Diagram](docs/diagrams/robosen_system_block_diagram.png)


The system is composed of four primary hardware elements:

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       HARDWARE COMPONENT OVERVIEW                                      │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│  1. MASTER BLOCK (The Brain, Config Dock & BLE Gateway)                                                │
│     • Microcontroller: ESP32-S3 with Native Bluetooth BLE 5.0, SPI for E-Ink, and Dual UARTs           │
│     • Display: High-contrast 2.13" E-Ink E-Paper screen showing action names, icons, & parameters       │
│     • Controls: Knob 1 (Action Selector), Knob 2 (Param Adjuster), Dual Buttons (Green Go & Red Stop)  │
│     • Dual Interfaces: (1) Config Dock Port (to flash 1 block) + (2) Run Chain Port (execution track) │
│     • Power Source: Rechargeable 18650 Li-ion battery with USB-C TP4056 BMS, 3.3V Buck-Boost & ADC Sense│
│     • Visual Feedback: Master RGB Status LED with expressive light choreography (No noisy buzzer!)    │
│                                                                                                        │
│  2. SOLID SMART ACTION BLOCKS (The Modular Code Blocks)                                                │
│     • Microcontroller: Ultra-low-cost WCH CH32V003 (32-bit RISC-V, ~$0.15 in SOP-8 package)            │
│     • Solid Shell Design: ZERO buttons or knobs on individual blocks (drop-proof, indestructible)      │
│     • Internal Wiring: 100% Planar (non-overlapping) PCB traces routing 3.3V, GND, UART, & LED data    │
│     • Memory: Stored Action Token ID & Parameter inside 192-byte internal non-volatile flash           │
│     • Visual Feedback: Addressable WS2812B RGB LED (indicates action color & glowing green execution)  │
│                                                                                                        │
│  3. END TERMINATOR BLOCK (The End of Code Marker)                                                      │
│     • Passive Bridge or Smart Terminator (with CH32V003 & green Ready LED)                             │
│     • Role: Loops downstream data back to the Master RX return rail to close the loop                  │
│                                                                                                        │
│  4. ROBOSEN K1 HUMANOID ROBOT (The Physical Avatar)                                                    │
│     • 17 high-precision digital servos, 6-axis gyroscope IMU, onboard speaker                          │
│     • Communicates wirelessly with Master Block via BLE Service 0xFFE0 / Char 0xFFE1                   │
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Standardized 4-Pin Magnetic Pogo Connector Pinout
All blocks connect using child-friendly, polarized magnetic pogo pins:

| Pin # | Signal Name | Type | Purpose in Config Port (Dock) | Purpose in Run Chain |
| :---: | :--- | :---: | :--- | :--- |
| **Pin 1** | **`V+` (3.3V)** | Power | Powers single docked block | Regulated 3.3V power supplied by Master Block |
| **Pin 2** | **`GND`** | Power | System ground | Common system ground reference |
| **Pin 3** | **`UART DATA`** | Bidirectional Point-to-Point | Master reads ACK from Block (`CFG_RX`) | Cascading downstream line (Master $\to$ B1 $\to$ B2 $\dots \to$ End) |
| **Pin 4** | **`PASS_THRU / RX_BUS`**| Bidirectional Bus | Master writes Config Command (`CFG_TX`) | Continuous return rail for compiled program & active step broadcast bus |

---

## 3. Communication Protocol & Signal Flow

```mermaid
sequenceDiagram
    autonumber
    participant Master as Master Block (ESP32-S3)
    participant Docked as Action Block (At Config Dock)
    participant B1 as Block 1 (Walk 3 Steps)
    participant B2 as Block 2 (Punch Left)
    participant EndBlock as End Block (Loopback)
    participant Robot as Robosen K1 Robot

    Note over Master,Docked: CONFIGURATION MODE (At Master Config Dock)
    Master->>Docked: Send Write Config [0xCF, 0x02, ActionID, Param, CRC, 0x55]
    Note over Docked: Saves [ActionID, Param] to Internal Flash Memory
    Docked-->>Master: Send ACK [0xCF, 0x06, CRC, 0x55]
    Note over Master,Docked: Block LED Pulses Emerald Green (Saved!)

    Note over Master,EndBlock: PHASE 1: DISCOVERY & COMPILATION (Press Green Start Button)
    Master->>B1: Frame [0xAA, Len=0, Count=0, CRC] (Pin 3 TX)
    Note over B1: Sets Index=1, appends Flash Token 0x01 (Walk) + Param=3, Count=1
    B1->>B2: Frame [0xAA, Len=2, Count=1, 0x01, 0x03, CRC]
    Note over B2: Sets Index=2, appends Flash Token 0x10 (Punch) + Param=1, Count=2
    B2->>EndBlock: Frame [0xAA, Len=4, Count=2, 0x01, 0x03, 0x10, 0x01, CRC]
    EndBlock->>Master: Return Program Frame over Pin 4 (Return RX Rail)
    Master->>Master: Validates CRC-8 Checksum & Queues Sequence

    Note over Master,Robot: PHASE 2: REAL-TIME EXECUTION & VISUAL STEP TRACKING
    Master-->>B1: Broadcast [0xBB, ActiveStep=1, CRC] (Pin 4 RX_BUS)
    Note over B1: MyIndex(1) == ActiveStep(1) -> GLOWS BRIGHT PULSING GREEN!
    Master->>Robot: Send BLE Walk Command (Opcode 0x01)
    Robot->>Master: Robot completes locomotion steps
    
    Master-->>B2: Broadcast [0xBB, ActiveStep=2, CRC] (Pin 4 RX_BUS)
    Note over B1: Reverts to Mode Color (Blue)
    Note over B2: MyIndex(2) == ActiveStep(2) -> GLOWS BRIGHT PULSING GREEN!
    Master->>Robot: Send BLE Action "ProAction/Left Punch" (Opcode 0x17)
    Robot->>Master: Robot streams progress -> reaches 100% ACK (0x64)

    Note over Master,EndBlock: PROGRAM COMPLETE
    Master-->>EndBlock: Broadcast [0xBB, 0xFF] (All Block LEDs sparkle rainbow victory!)
```

---

## 4. Current State of the Project

The project is currently in an **advanced software, protocol simulation, and live BLE validation stage**:

### 4.1 What Has Been Completed & Verified
1. **Full Robosen K1 BLE Protocol Reverse Engineering:**
   - Decoded 25+ opcodes on Service `0xFFE0` / Char `0xFFE1` (Locomotion `0x01-0x08`, Predefined Actions `0x17`, 17-Servo Joint Kinematics `0xE8/0xE9`, Telemetry `0x0F`, Keep-alive `0x0B`).
   - Discovered **dynamic 100% progress ACK resolution** on action streams, allowing instant, seamless action transitions without arbitrary delay timers.
   - Verified live with physical robot `K1-00457` (Firmware `VER:3.03L`, MAC `3C:A5:51:94:97:70`).

2. **Native Python BLE Control & Daemon Layer:**
   - [`scripts/k1_ble_daemon.py`](scripts/k1_ble_daemon.py): High-performance background daemon holding a persistent BLE connection with IPC JSON messaging.
   - [`scripts/k1_action.py`](scripts/k1_action.py): Instant action runner and telemetry inspector CLI.
   - [`scripts/k1_ble_tester.py`](scripts/k1_ble_tester.py): Interactive console telemetry and motion control suite.

3. **Complete Node-RED Tangible Block Simulator Suite (`node-red-contrib-robosen-block`):**
   - **`robosen-master`**: Simulates the Master Block, emits `0xAA` discovery seed, verifies CRC-8, coordinates BLE execution, and broadcasts `0xBB` real-time step frames.
   - **`robosen-smart-block`**: Simulates the CH32V003 Smart Block with flash parameter storage and dynamic WS2812B RGB LED color states.
   - **`robosen-smart-end`**: Simulates the active end terminator with CRC-8 validation, loopback return, and fault injection capabilities.
   - **`robosen-protocol-monitor`**: Real-time packet analyzer decoding binary hex frames, tokens, parameters, and checksum integrity.
   - **Ready-to-run simulation flows**: [`robosen_smart_block_flow.json`](node-red-contrib-robosen-block/examples/robosen_smart_block_flow.json) and [`robosen_simulator_flow.json`](node-red-contrib-robosen-block/examples/robosen_simulator_flow.json).

4. **Hardware & Electrical Architecture Specifications:**
   - Completed detailed hardware documentation ([`PHYSICAL_BLOCK_SYSTEM_SPEC.md`](PHYSICAL_BLOCK_SYSTEM_SPEC.md)) defining 4-pin pogo pinout, power consumption, CH32V003 SOP-8 pinouts, and CRC-8 algorithms.

---

## 5. Master Improvement Plan & Future Roadmap

```text
+---------------------------------------------------------------------------------------------------+
|                                    5-PILLAR IMPROVEMENT ROADMAP                                   │
+-----------------+-----------------+------------------+--------------------+-----------------------+
|   1. HARDWARE   |   2. PROTOCOL   |   3. MASTER BLE  |   4. CHILD UX &    |   5. SOLID BLOCKS     |
|   & POWER BOM   |  & RESILIENCE   |     FIRMWARE     |   LIGHT LANGUAGE   |  & CONFIG DOCK        |
+-----------------+-----------------+------------------+--------------------+-----------------------+
| • $0.15 RISC-V  | • CRC-8 Checks  | • Standalone C++ │ • E-Ink Display    | • Central Config Dock |
|   (CH32V003)    | • Hot-plug Safe │   ESP32-S3 app   │ • WS2812B RGB LEDs │ • Zero Moving Parts   |
| • LiPo + USB-C  | • RC Debouncing │ • 100% ACK Sync  │ • Friendly Icons   │ • Internal Flash Mem  |
| • Mag Snap Pins │ • Contact Noise │ • Fall Recovery  │ • Silent Classroom │ • Drop-Proof Enclosure|
+-----------------+-----------------+------------------+--------------------+-----------------------+
```

### Pillar 1: Hardware & Power BOM Optimization
- **Ultra-Low Cost Slave MCUs:** Transition all instruction blocks to **WCH CH32V003** 32-bit RISC-V microcontrollers in SOP-8 package (~$0.15 per block vs. $2.50+ for ESP32). Reduces block cost by 90% and idle current from 50 mA to $< 10\,\mu\text{A}$.
- **Rechargeable Master Power:** Single 3.7V LiPo/18650 cell with onboard TP4056 USB-C charging and battery management protection (BMS).
- **Polarized Magnetic Snap Pins:** Self-aligning magnetic pogo pin connectors that prevent reverse polarity connections and snap together effortlessly for little hands.

### Pillar 2: Protocol Resilience & Child-Proofing (Hot-Plug Tolerance)
- **Contact Bounce Suppression:** 10 kΩ pull-ups and 22 pF RC filtering on UART pins to eliminate electrical glitches when children wiggle blocks.
- **Graceful Error Recovery:** If a child unplugs a block mid-execution, the Master catches the break within 50 ms, stops the robot safely, and flashes the affected block red rather than crashing.

### Pillar 3: Master ESP32-S3 Standalone Embedded Firmware & Smart NVS Pairing
- **Full Embedded Port:** Flash the non-blocking command queue directly onto the Master ESP32-S3 in C++ (ESP-IDF / Arduino), eliminating the need for a laptop, Python script, or Node-RED in the final classroom setup.
- **Multi-Robot Smart NVS Binding:** Boots and connects directly to the last-paired robot MAC in $<500\,\text{ms}$, preventing classroom crosstalk.
- **Teacher E-Ink Pairing Menu:** Hold Start for 3 seconds to scan, sort nearby robots by RSSI proximity, select via Knob 1, and save as the new persistent default MAC.

### Pillar 4: Child-Centric UX, Light Language & Enclosures
- **Visual Color-Coded Actions:**
  - 🔵 **Blue:** Walk Forward / Backward
  - 🔷 **Cyan:** Turn Left / Right
  - 🔴 **Red:** Left / Right Punch
  - 🟠 **Orange:** Kung Fu Routine
  - 🟣 **Magenta:** Dance / Boogaloo
  - 🟡 **Yellow:** Wait Delay
  - 🟢 **Bright Pulsing Green:** Currently Executing Step!
- **E-Ink Display Visuals:** Shows text, large icons, and parameter counts in crystal-clear, sunlight-readable e-paper.
- **Expressive Light Choreography (No Buzzer):** Emerald green success pulse, data comet compilation wave, and rainbow celebration sparkle.
- **Drop-Proof Solid Enclosures:** 3D-printed / injection-molded ABS enclosures with soft rounded corners and zero mechanical dials to break.

---

## 6. Summary Comparison Table

| Metric / Feature | Current State (Software & Simulation) | Target Physical Hardware Product |
| :--- | :--- | :--- |
| **Execution Environment** | Node-RED & Python BLE Background Daemon | Standalone ESP32-S3 Master Block (No PC needed) |
| **Master UI & Display** | Node-RED Web Dashboard | E-Ink Display + Dual Rotary Dials + Start Button |
| **Instruction Blocks** | Simulated Node-RED Smart Block Nodes | Solid CH32V003 RISC-V Snap Blocks (No buttons/knobs) |
| **Configuration Method** | Node-RED UI Dropdowns | Master Block Config Dock (`0xCF` UART Flash) |
| **Inter-Block Bus** | Simulated 2-Phase Binary Frames (`0xAA`/`0xBB`) | 4-Pin Magnetic Pogo Pin UART Daisy-Chain |
| **Visual Feedback** | Node-RED UI Status Badges | Addressable WS2812B RGB LEDs (Light Choreography) |
| **Audio Feedback** | System Audio / Console Alerts | Silent Classroom (Robot's built-in speaker only) |
| **BOM Cost per Block** | N/A (Software) | **~$0.25 – $0.35** per physical block |
| **Target User Experience** | Technical Testing & Developer Prototyping | Screenless, Tactile STEM Toy for Kids $\le 7$ |

---

## 7. Recommended Next Steps

1. **Master Block PCB (Phase 1 Carrier):** ✅ **ORDERED & FABRICATION IN PROGRESS (Oct 2026):**
   - KiCad 10 project ([`hardware/master_block/`](hardware/master_block/)), $115.50 \times 62.00\text{ mm}$ outline with 4 M3 mounting holes.
   - Trace Routing & Power Planes: 100% routed (**0 unconnected items**), filled `GND` copper planes on both layers, $0.80\text{ mm}$ power traces, isolated `/VBAT_GND` BMS protection loop.
   - Production Gerbers & drill files: [`hardware/master_block/robosen_master_block_gerbers.zip`](hardware/master_block/robosen_master_block_gerbers.zip).
2. **Action Block PCB (Modular CH32V003 Carrier):** ✅ **ORDERED & FABRICATION IN PROGRESS (Oct 2026):**
   - KiCad 10 project ([`hardware/action_block/`](hardware/action_block/)), $32.00 \times 32.00\text{ mm}$ compact square carrier PCB.
   - Centered Pogo Ports: Both Upstream `IN` and Downstream `OUT` 4-pin pogo docks are mathematically centered at $Y = 72.50\text{ mm}$ for flush collinear docking.
   - 3-Pin RGB LED Header: Top-to-Bottom order `GND`, `VCC` (+3V3), `IN` (`/LED_DIN`).
   - Routing: 100% routed (**0 unconnected items, 0 copper clearance errors**), `/RETURN_BUS` detour below MCU ($Y = 87.25\text{ mm}$), $0.60\text{ mm}$ power traces, and continuous GND planes.
   - Dual-Agent Verified: Audited and cross-verified by Antigravity and Codex Astra (`gpt-6-astra`).
   - Production Gerbers & drill files: [`hardware/action_block/robosen_action_block_gerbers.zip`](hardware/action_block/robosen_action_block_gerbers.zip).
3. **C++ Master Firmware:** ✅ **COMPLETED & VERIFIED ON PHYSICAL HARDWARE (Sept 7–8, 2026):**
   - Implemented dual-knob rotary encoders, persistent BLE auto-reconnect, Config Dock UART driver, and Run Chain Engine (`0xAA`/`0xBB`/`0xFF`) on ESP32-S3 (`firmware/esp32_master`).
   - Verified live detection and non-volatile flash burning into docked CH32V003 Action Blocks.
   - Verified full daisy-chain discovery, cumulative CRC-8 validation, real-time step tracking, and rainbow celebration sparkle.
4. **CH32V003 Action Block & Smart End Block Firmware:** ✅ **COMPLETED & VERIFIED ON PHYSICAL HARDWARE (Sept 7–8, 2026):**
   - Built with native `riscv32-esp-elf-gcc` (`action_block.bin`: 2,804 bytes; `end_block.bin`: 2,016 bytes).
   - Implemented Config Port flash writer (`0xCF`), Phase 1 discovery relay (`0xAA`), and Phase 2 step tracking (`0xBB`) with downstream forwarding in RISC-V C.
   - Implemented Smart End Block active digital line driver with loopback, CRC-8 validation, and rainbow sparkle.
   - Verified byte-for-byte readback on physical TENSTAR CH32V003F4P6 chips via ESP32-S3 programmer on `COM3`.
   - Verified live 2-block run chain executing locomotion on Robosen K1 robot.
5. **3D Casing Prototypes:** 3D print initial snap-fit solid block shells with magnetic polarity channels and light pipes for the WS2812B LEDs.
6. **Classroom User Testing:** Pilot test 5-block sets with 5–7 year old children to validate physical usability and E-Ink dock ergonomics.


