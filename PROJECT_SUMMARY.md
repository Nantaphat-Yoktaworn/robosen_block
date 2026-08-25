# Robosen Tangible Coding Block System: Comprehensive Project Summary & Scope

> **Project Name:** Tangible Modular Coding Block System for Robosen Robot  
> **Target Demographic:** Children aged 7 years old and under (Early Childhood / Kindergarten to Early Elementary)  
> **Core Purpose:** Screenless physical block-based coding to teach computational thinking, algorithm sequencing, and cause-and-effect through interactive humanoid robot control.  
> **Target Hardware:** Modular Physical Blocks (ESP32 Master + CH32V003 Slaves) $\longleftrightarrow$ Robosen K1 Humanoid Robot (Bluetooth Low Energy)  
> **Date:** August 2026  

---

## 1. Project Scope & Educational Mission

### 1.1 The Core Problem
Most modern coding curricula for children rely on tablets, smartphones, or computers (e.g., Scratch, Blockly). However, for **young children aged 7 and under**, screens present significant developmental hurdles:
- **Abstract vs. Concrete Cognition:** Children under 7 (Piaget’s Preoperational and early Concrete Operational stages) learn best through tactile, physical manipulation rather than abstract 2D screen coordinates.
- **Screen Fatigue & Distraction:** Excessive screen time can cause disengagement and cognitive overload.
- **Disconnected Output:** Controlling a virtual sprite on a screen does not provide the same visceral spatial awareness and excitement as watching a physical robot walk, punch, and balance in the real world.

### 1.2 The Project Solution: Tangible Modular Coding Blocks
This project creates a **tangible, screenless, modular programming system**. Children physically snap together magnetic coding blocks in a line on the floor or table to create a sequence of instructions. When they press the big **Green "Go" Button** on the Master Block, the connected sequence compiles instantly and commands the **Robosen K1 humanoid robot** via Bluetooth Low Energy (BLE).

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PHYSICAL TANGIBLE CODING CHAIN                                 │
│                                                                                                  │
│   [ MASTER BLOCK ] ──► [ WALK BLOCK ] ──► [ TURN BLOCK ] ──► [ PUNCH BLOCK ] ──► [ END BLOCK ]   │
│   (Brain, Battery,     (Param: 3 steps)   (Param: 90° Right) (Action: Left Hook) (Terminator)    │
│    Start Button,                                                                                 │
│    Buzzer Chime)                                                                                 │
│          │                                                                                       │
│          ▼ (Bluetooth BLE 4.2 Stream)                                                            │
│   [ ROBOSEN K1 HUMANOID ROBOT ] ─── Executes commands step-by-step with real-time feedback!      │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Key Foundational Coding Concepts Taught (Ages $\le 7$)
1. **Linear Sequence & Order of Execution:**  
   Children learn that computers/robots follow instructions strictly in order from left to right. Swapping the position of the *Walk* and *Punch* blocks changes what the robot does.
2. **Parameters & Modifiers (Rotary Knob Dials):**  
   Children discover that actions have properties. Turning the physical dial adjusts *how many steps* to walk (1 to 10), *what angle* to turn (45° to 180°), or *how many seconds* to wait.
3. **Real-Time Cause-and-Effect (Active Step Tracking):**  
   As the robot performs each action, the corresponding physical block **glows bright pulsating green** and the Master sounds an auditory tick. The child can look at the glowing block, look at the robot moving, and instantly map the block to the physical motion.
4. **Debugging & Algorithmic Thinking:**  
   If the robot bumps into a toy or turns the wrong way, the child physically inspects the chain, identifies the incorrect block, snaps in the right one, and tries again.
5. **Loops & Repetition (Pattern Recognition):**  
   Introducing repeat blocks to understand that repeating an action is more efficient than chaining many identical blocks.

---

## 2. System Architecture & Physical Hardware Components

The system is composed of four primary hardware elements:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       HARDWARE COMPONENT OVERVIEW                                      │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│  1. MASTER BLOCK (The Brain & Gateway)                                                                 │
│     • Microcontroller: ESP32-C3 / ESP32-S3 with Bluetooth BLE 4.2 / 5.0                                │
│     • Power Source: Rechargeable 3.7V LiPo battery with USB-C TP4056 BMS charging                      │
│     • User Interface: Large tactile "Start / Go" button, power switch, and audio piezo buzzer         │
│     • Role: Drives 2-Phase UART bus, compiles chain, transmits BLE commands to Robosen K1              │
│                                                                                                        │
│  2. SMART INSTRUCTION BLOCKS (The Modular Code Blocks)                                                 │
│     • Microcontroller: Ultra-low-cost WCH CH32V003 (32-bit RISC-V, ~$0.15)                             │
│     • Action Selector: Big clicky push-button to cycle actions (Walk, Turn, Punch, Kung Fu, Dance)     │
│     • Parameter Adjuster: Rotary potentiometer knob (sets steps, angles, reps, delays)                 │
│     • Visual Feedback: Addressable WS2812B RGB LED (indicates action color & glowing green execution)  │
│                                                                                                        │
│  3. END TERMINATOR BLOCK (The End of Code Marker)                                                      │
│     • Passive Bridge or Smart Terminator (with CH32V003 & green Ready LED)                             │
│     • Role: Loops the downstream data line back to the Master RX return rail to close the loop         │
│                                                                                                        │
│  4. ROBOSEN K1 HUMANOID ROBOT (The Physical Avatar)                                                    │
│     • 17 high-precision digital servos, 6-axis gyroscope IMU, onboard speaker                          │
│     • Communicates wirelessly with Master Block via BLE Service 0xFFE0 / Char 0xFFE1                   │
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Standardized 4-Pin Magnetic Pogo Connector Pinout
All blocks connect using child-friendly, polarized magnetic pogo pins:

| Pin # | Signal Name | Type | Purpose |
| :---: | :--- | :---: | :--- |
| **Pin 1** | **`V+` (3.3V)** | Power | Regulated 3.3V power supplied by Master Block |
| **Pin 2** | **`GND`** | Power | System common ground |
| **Pin 3** | **`UART TX_DOWN`** | Data (Out) | Cascading downstream line (Master $\to$ Block 1 $\to$ Block 2 $\dots \to$ End) |
| **Pin 4** | **`UART RX_BUS`** | Bidirectional Bus | Continuous return rail for compiled program & active step broadcast bus |

---

## 3. Communication Protocol & Signal Flow

To provide instant physical feedback for kids without needing complex wiring, the system runs an **Enhanced 2-Phase Bi-Directional UART Protocol**:

```mermaid
sequenceDiagram
    autonumber
    participant Master as Master Block (ESP32)
    participant B1 as Block 1 (Walk 3 Steps)
    participant B2 as Block 2 (Punch Left)
    participant End as End Block (Loopback)
    participant Robot as Robosen K1 Robot

    Note over Master,End: PHASE 1: DISCOVERY & COMPILATION (Press Green Start Button)
    Master->>B1: Frame [0xAA, Len=0, Count=0, CRC] (Pin 3 TX)
    Note over B1: Sets Index=1, appends Token 0x01 (Walk) + Param=3, Count=1
    B1->>B2: Frame [0xAA, Len=2, Count=1, 0x01, 0x03, CRC]
    Note over B2: Sets Index=2, appends Token 0x10 (Punch) + Param=1, Count=2
    B2->>End: Frame [0xAA, Len=4, Count=2, 0x01, 0x03, 0x10, 0x01, CRC]
    End->>Master: Return Program Frame over Pin 4 (Return RX Rail)
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

    Note over Master,End: PROGRAM COMPLETE
    Master->>Master: Victory Fanfare on Piezo Buzzer!
    Master-->>End: Broadcast [0xBB, 0xFF] (All Block LEDs flash celebratory green)
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
   - [`scripts/k1_ble_daemon.py`](file:///C:/Users/poomz/nnnn/robosen_block/scripts/k1_ble_daemon.py): High-performance background daemon holding a persistent BLE connection with IPC JSON messaging.
   - [`scripts/k1_action.py`](file:///C:/Users/poomz/nnnn/robosen_block/scripts/k1_action.py): Instant action runner and telemetry inspector CLI.
   - [`scripts/k1_ble_tester.py`](file:///C:/Users/poomz/nnnn/robosen_block/scripts/k1_ble_tester.py): Interactive console telemetry and motion control suite.

3. **Complete Node-RED Tangible Block Simulator Suite (`node-red-contrib-robosen-block`):**
   - **`robosen-master`**: Simulates the Master Block, emits `0xAA` discovery seed, verifies CRC-8, coordinates BLE execution, and broadcasts `0xBB` real-time step frames.
   - **`robosen-smart-block`**: Simulates the CH32V003 Smart Block with interactive push button cycling, rotary dial adjustments, and dynamic WS2812B RGB LED color states (pulsing bright green on active execution).
   - **`robosen-smart-end`**: Simulates the active end terminator with CRC-8 validation, loopback return, and fault injection capabilities.
   - **`robosen-protocol-monitor`**: Real-time packet analyzer decoding binary hex frames, tokens, parameters, and checksum integrity.
   - **Ready-to-run simulation flows**: [`robosen_smart_block_flow.json`](file:///C:/Users/poomz/nnnn/robosen_block/node-red-contrib-robosen-block/examples/robosen_smart_block_flow.json) and [`robosen_simulator_flow.json`](file:///C:/Users/poomz/nnnn/robosen_block/node-red-contrib-robosen-block/examples/robosen_simulator_flow.json).

4. **Hardware & Electrical Architecture Specifications:**
   - Completed detailed hardware documentation ([`PHYSICAL_BLOCK_SYSTEM_SPEC.md`](file:///C:/Users/poomz/nnnn/robosen_block/PHYSICAL_BLOCK_SYSTEM_SPEC.md)) defining 4-pin pogo pinout, power consumption, CH32V003 SOP-8 pinouts, and CRC-8 algorithms.

---

## 5. Master Improvement Plan & Future Roadmap

To transition this system from a working simulation/software stack into a mass-producible, durable, child-friendly commercial product, the improvement roadmap is divided into **5 Core Pillars** plus **Pedagogical Curriculum**:

```
+---------------------------------------------------------------------------------------------------+
│                                    5-PILLAR IMPROVEMENT ROADMAP                                   │
+-----------------+-----------------+------------------+--------------------+-----------------------+
│   1. HARDWARE   │   2. PROTOCOL   │   3. MASTER BLE  │   4. CHILD UX &    │   5. SMART BLOCKS     │
│   & POWER BOM   │  & RESILIENCE   │     FIRMWARE     │  TACTILE DESIGN    │  & UNIFIED FIRMWARE   │
+-----------------+-----------------+------------------+--------------------+-----------------------+
│ • $0.15 RISC-V  │ • CRC-8 Checks  │ • Standalone C++ │ • WS2812B RGB LEDs │ • Unified Single FW   │
│   (CH32V003)    │ • Hot-plug Safe │   ESP32 BLE app  │ • Friendly Icons   │ • Button Cycling      │
│ • LiPo + USB-C  │ • RC Debouncing │ • 100% ACK Sync  │ • Buzzer Chimes    │ • Knob Hysteresis     │
│ • Mag Snap Pins │ • Contact Noise │ • Fall Recovery  │ • Drop-Proof Cases │ • Smart Terminator    │
+-----------------+-----------------+------------------+--------------------+-----------------------+
```

### Pillar 1: Hardware & Power BOM Optimization
- **Ultra-Low Cost Slave MCUs:** Transition all instruction blocks to **WCH CH32V003** 32-bit RISC-V microcontrollers in SOP-8 package (~$0.15 per block vs. $2.50+ for ESP32). Reduces block cost by 90% and idle current from 50 mA to $< 10\,\mu\text{A}$.
- **Rechargeable Master Power:** Single 3.7V LiPo/18650 cell with onboard TP4056 USB-C charging and battery management protection (BMS).
- **Polarized Magnetic Snap Pins:** Self-aligning magnetic pogo pin connectors that prevent reverse polarity connections and snap together effortlessly for little hands.

### Pillar 2: Protocol Resilience & Child-Proofing (Hot-Plug Tolerance)
- **Contact Bounce Suppression:** 10 kΩ pull-ups and 22 pF RC filtering on UART pins to eliminate electrical glitches when children wiggle blocks.
- **Graceful Error Recovery:** If a child unplugs a block mid-execution, the Master catches the break within 50 ms, stops the robot safely, sounds a soft error chime, and flashes the affected block red rather than crashing.

### Pillar 3: Master ESP32 Standalone Embedded Firmware
- **Full Embedded Port:** Flash the non-blocking command queue directly onto the Master ESP32-C3/S3 in C++ (ESP-IDF / Arduino), eliminating the need for a laptop, Python script, or Node-RED in the final classroom setup.
- **Automatic BLE Pairing:** Master automatically scans for `"K1"` advertising packets and pairs instantly on power-up.

### Pillar 4: Child-Centric UX, Tactile Design & Enclosures
- **Visual Color-Coded Actions:**
  - 🔵 **Blue:** Walk Forward / Backward
  - 🔷 **Cyan:** Turn Left / Right
  - 🔴 **Red:** Left / Right Punch
  - 🟠 **Orange:** Kung Fu Routine
  - 🟣 **Magenta:** Dance / Boogaloo
  - 🟡 **Yellow:** Wait Delay
  - 🟢 **Bright Pulsing Green:** Currently Executing Step!
- **Tactile Icons & Large Controls:** Large embossed symbols (arrows, fist, music note, timer clock) on each block casing so pre-literate children can code without reading text.
- **Playful Sound Design:** Master piezo buzzer plays ascending start chords, subtle step ticks, and celebratory victory fanfares.
- **Drop-Proof Rounded Enclosures:** 3D-printed / injection-molded ABS enclosures with soft rounded corners, child-safe matte textures, and recessed knobs.

### Pillar 5: Smart Multi-Action Blocks & Unified Firmware
- **Single Firmware Binary:** One compiled RISC-V firmware flashed across all instruction and end blocks.
- **Dual Hardware Modality:**
  - *Multi-Action Blocks:* Read button and knob to allow flexible action configuration.
  - *Dedicated 1-Action Blocks:* Read a fixed resistor divider on boot to permanently lock into a specific role (ideal for younger 4–5 year olds who need simpler single-action blocks).

### Pedagogical Expansion: Early Childhood Curriculum Kit
- **Story Challenge Cards:** "Help the K1 robot deliver the package: Walk 3 steps, turn right, punch the obstacle, and celebrate!"
- **Grid Maze Activity Floor Mats:** Physical canvas mats with 30 cm step grids where children plan and execute robotic navigation algorithms.
- **Progressive Difficulty Stages:**
  - *Stage 1 (Ages 4–5):* Basic 3-block linear chains (Forward $\to$ Punch $\to$ End).
  - *Stage 2 (Ages 5–6):* Multi-action sequences with parameter dials (Turn 90°, Walk 4 steps, Delay 2s).
  - *Stage 3 (Ages 6–7):* Repeat loops, complex obstacle mazes, and choreographed dance routines.

---

## 6. Summary Comparison Table

| Metric / Feature | Current State (Software & Simulation) | Target Physical Hardware Product |
| :--- | :--- | :--- |
| **Execution Environment** | Node-RED & Python BLE Background Daemon | Standalone ESP32 Master Block (No PC needed) |
| **Instruction Blocks** | Simulated Node-RED Smart Block Nodes | Physical CH32V003 RISC-V Plastic Snap Blocks |
| **Inter-Block Bus** | Simulated 2-Phase Binary Frames (`0xAA`/`0xBB`) | 4-Pin Magnetic Pogo Pin UART Daisy-Chain |
| **Visual Feedback** | Node-RED UI Status Badges (Green / Red) | Physical Addressable WS2812B RGB LEDs |
| **Audio Feedback** | System Audio / Console Alerts | Master Block Piezo Buzzer Chimes & Fanfares |
| **BOM Cost per Block** | N/A (Software) | $< \$0.80$ per physical block |
| **Target User Experience** | Technical Testing & Developer Prototyping | Screenless, Tactile STEM Toy for Kids $\le 7$ |

---

## 7. Recommended Next Steps

1. **PCB Schematic & Layout:** Design the 4-pin magnetic PCB for the ESP32 Master Block and CH32V003 Smart Instruction Block.
2. **C++ Master Firmware:** Port the Node-RED / Python asynchronous queue engine into an ESP-IDF / Arduino firmware for ESP32.
3. **CH32V003 Slave Firmware:** Implement the debounced button state machine, ADC knob reading, and 2-phase UART parser in RISC-V C.
4. **3D Casing Prototypes:** 3D print initial snap-fit block shells with magnetic polarity channels and light pipes for the WS2812B LEDs.
5. **Classroom User Testing:** Pilot test 5-block sets with 5–7 year old children to validate physical usability and parameter knob ergonomics.
