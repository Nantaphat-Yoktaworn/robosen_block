# RobosenJS & Tangible Coding Block System: Master Project Memory

> **System Overview:** Programmatic Control (Node.js & Python SDK), Custom Node-RED Tangible Block Simulator Palette, and Bluetooth Low Energy (BLE) Reverse Engineering for the **Robosen K1 / Interstellar Scout K1 Series** Humanoid Robot.  
> **Last Updated:** August 25, 2026  
> **FCC ID:** `2ATNWK1` | **Live Verified Robot ID:** `K1-00457` (`3C:A5:51:94:97:70`) | **Firmware:** `VER:3.03L`

---

## 1. Project Architecture & File Organization

```
robosen_block/
├── assignments/
│   ├── as01_เอกสารสรุปงานวิจัยที่เกี่ยวข้อง.pdf # Academic literature review (4 verified research papers)
│   └── RESEARCH_SUMMARY.md               # Presentation-ready markdown summary of AS01 research papers
├── bin/
│   └── k1.js                             # Node.js CLI executable wrapper
├── recordings/
│   └── K1/
│       └── test.json                     # Recorded joint keyframe motion sequences
├── scripts/
│   ├── control.js                        # Gamepad / Keyboard controller runner (Node.js)
│   ├── demo.js                           # Quick demo choreography script (Node.js)
│   ├── main.js                           # Standard startup & health check script (Node.js)
│   ├── program.js                        # Scripted robot movements & routines (Node.js)
│   ├── prompt.js                         # LLM natural language prompt runner (Node.js)
│   ├── repl.js                           # Interactive REPL session (Node.js)
│   ├── voice.js                          # Voice interaction session (Node.js)
│   ├── k1_ble_daemon.py                  # Persistent background BLE daemon with dynamic 100% progress ACK (Python/Bleak)
│   ├── k1_joint_controller.py            # Interactive 17-joint kinematics controller with safeguard limits (Python)
│   ├── k1_ble_tester.py                  # Live interactive BLE test menu & telemetry monitor (Python/Bleak)
│   ├── k1_action.py                      # Fast one-shot action execution CLI & status query (Python/Bleak)
│   └── set_volume.py                     # Direct speaker volume configuration utility (Python/Bleak)
├── src/
│   ├── K1/
│   │   ├── llm/
│   │   │   ├── command/
│   │   │   │   ├── systemPrompt.txt      # LLM prompt for mapping natural language to actions
│   │   │   │   └── userPrompt.txt        # User prompt wrapper with allowed actions catalog
│   │   │   └── joint/
│   │   │       ├── systemPrompt.txt      # LLM prompt for generating raw 17-servo keyframes
│   │   │       └── userPrompt.txt        # User prompt wrapper for joint kinematics
│   │   └── robot.json                    # Declarative K1 robot specification & kinematics limits
│   ├── K1.d.ts                           # TypeScript definitions for K1 class
│   ├── K1.js                             # K1 subclass inheriting from Robot base
│   ├── Robot.d.ts                        # TypeScript definitions for Robot base class
│   └── Robot.js                          # Core protocol, BLE transport, HID controller & LLM engine
├── test/
│   ├── __mocks__/@abandonware/noble.js   # Mock BLE hardware layer for offline unit testing
│   ├── K1.test.js                        # K1 integration unit tests
│   └── Robot.test.js                     # Robot protocol & packet encoder tests
├── node-red-contrib-robosen-block/       # Custom Node-RED palette simulating physical block daisy chain (v2.0)
│   ├── lib/
│   │   └── protocol.js                   # Protocol encoder/decoder, CRC-8, and token catalog
│   ├── nodes/
│   │   ├── robosen-master.js / .html     # Smart Master Block controller (2-Phase Binary V2, Start button & REST API)
│   │   ├── robosen-legacy-master.js / .html # Dedicated Legacy Master Block (CSV String V1, Start button & REST API)
│   │   ├── robosen-smart-block.js / .html# Smart Multi-Action Block (CH32V003 RISC-V with Button & Knob)
│   │   ├── robosen-smart-end.js / .html  # Smart Active Terminator Block with CRC-8 validation & loopback
│   │   ├── robosen-protocol-monitor.js / .html # Serial Protocol Bus Analyzer & Packet Sniffer
│   │   ├── robosen-tester.js / .html     # Standalone action tester & direct controller node
│   │   ├── robosen-instruction.js / .html# Legacy modular instruction blocks (V1 CSV mode)
│   │   └── robosen-end.js / .html        # Legacy passive loopback terminator block node (V1)
│   ├── examples/
│   │   ├── robosen_smart_block_flow.json # Ready-to-import 2-Phase Binary simulation flow
│   │   └── robosen_simulator_flow.json   # Legacy string simulation flow (uses Legacy Master)
│   ├── package.json                      # Node-RED palette package manifest (v2.0.0)
│   └── README.md                         # Detailed palette documentation & API guide
├── index.d.ts                            # Root TypeScript exports
├── index.js                              # Package entry point (exports K1 and Robot)
├── package.json                          # NPM dependencies and script definitions
├── README.md                             # Comprehensive project master README
├── PROJECT_SUMMARY.md                    # Executive project summary & scope
├── PHYSICAL_BLOCK_SYSTEM_SPEC.md         # Hardware & electrical spec for modular tangible coding blocks
├── IMPROVEMENT_PLAN.md                   # 5-Pillar master improvement plan & roadmap
├── ROBOSEN_K1_DOCUMENTATION.md           # Complete official K1 documentation & user manual
└── MEMORY.md                             # Master project memory & knowledge base (this file)
```

---

## 2. Live Hardware Diagnostics & Verified Device State

Live hardware tests conducted directly over Windows Native BLE (`winrt-windows-devices-bluetooth` via `Bleak`):

| Property | Value / Live State | Verification Method |
| :--- | :--- | :--- |
| **Device Model** | `Robosen K1 (Interstellar Scout)` | Discovered over BLE Advertisement |
| **Local Device Name** | `K1-00457` | BLE Local Name Broadcast |
| **Bluetooth MAC Address**| `3C:A5:51:94:97:70` | Windows BLE Adapter Discovery |
| **Signal Strength (RSSI)**| `-63 dBm` | Live RSSI Measurement |
| **Firmware Version** | `VER:3.03L` | Queried via Opcode `0xF7` |
| **Service UUID** | `0000ffe0-0000-1000-8000-00805f9b34fb` (`0xFFE0` / `ffe0`) | GATT Service Discovery |
| **Characteristic UUID** | `0000ffe1-0000-1000-8000-00805f9b34fb` (`0xFFE1` / `ffe1`) | GATT Characteristic Discovery |
| **Live Battery Progress** | `40%` $\rightarrow$ `61%` $\rightarrow$ `64%` $\rightarrow$ `70%` $\rightarrow$ `90%+` (Actively Charging) | Decoded from State Packet `0x0F` |
| **Speaker Volume** | `140 / 140` (Max) | Decoded from State Packet `0x0F` |
| **Auto-Stand (Fall Recovery)** | **Disabled (`0x00`)** | Toggled via `0x11` (0x00) & verified in `0x0F` |
| **Auto-Turn (IMU Heading)** | **Enabled (`0x01`)** | Default factory state verified in `0x0F` |
| **Auto-Off (Sleep Timer)** | **Enabled (`0x01`)** | Factory power-saving timer verified in `0x0F` |
| **Auto-Pose (Idle Moves)** | *N/A (Removed from K1 UI)* | Unsupported by K1 bipedal firmware; removed from telemetry reader |

---

## 3. Power, Charging & Hardware Ports

### 3.1 Dual Port Functions
1. **DC Barrel Jack Charging Port (Torso):**
   - **Dedicated to charging ONLY.**
   - Uses the official AC/DC power brick (**Output: DC 8.4V, 2.0A**).
   - Battery is a **2-cell (7.4V nominal) 2000 mAh Li-ion pack**.
   - Charging indicator: **Solid Red** = Charging, **Solid Green / Off** = Fully Charged ($100\%$).
   - Spoken audio confirmation upon connection: *"Start to supply energy."*
2. **USB Type-C Port (Torso):**
   - **Data Transfer ONLY.**
   - Cannot charge the robot from a standard 5V phone charger (voltage mismatch & no internal USB-C charging circuitry).
   - Used for PC data connection, onboard filesystem exploration, and choreography file transfers.

---

## 4. Automation & Safety Modes Explained

1. **🛡️ Auto-Stand Mode (Opcode `0x11`):**
   - **Function:** Fall recovery. The 6-axis internal gyroscope detects if the robot has fallen flat on its chest or back.
   - **Behavior:** Robot automatically initiates an acrobatic push-up routine to stand back up on its feet.
   - **Control:** Toggled via Opcode `0x11` with payload `0x01` (enable) or `0x00` (disable).

2. **🔄 Auto-Turn Mode (Opcode `0x1A`):**
   - **Function:** Real-time IMU yaw drift & obstacle balance correction during locomotion.
   - **Behavior:** Automatically adjusts individual foot step angles if uneven carpet/floor friction causes heading deviation.
   - **Control:** Toggled via Opcode `0x1A` with payload `0x01` (enable) or `0x00` (disable).

3. **🧘 Auto-Pose Mode (Opcode `0x1B`):**
   - **Function:** Autonomous idle animations and subtle "breathing" posture shifts when waiting for commands.
   - **K1 Firmware Note:** On K1 firmware `VER:3.03L`, autonomous idle posing is locked off (`0x00`) by default to prevent bipedal balance loss while standing unattended. Removed from K1 telemetry display.

4. **⏱️ Auto-Off Timer (Opcode `0x13`):**
   - **Function:** Power management. Shuts down servos and powers down after extended idle periods to preserve battery.
   - **Control:** Toggled via Opcode `0x13` with payload `0x01` (enable) or `0x00` (disable).

---

## 5. Bluetooth Low Energy (BLE) Protocol Specification

### 5.1 Packet Frame Structure
All binary frames transmitted to Characteristic `0xFFE1` follow this structure:

```
┌──────────────┬──────────────────┬───────────────┬──────────────────────┬──────────────┐
│ Header       │ Length (N+2)     │ Opcode (Type) │ Payload / Data (N B) │ Checksum (1) │
│ 2 Bytes: FFFF│ 1 Byte           │ 1 Byte (Hex)  │ Optional Bytes       │ 1 Byte       │
└──────────────┴──────────────────┴───────────────┴──────────────────────┴──────────────┘
```

- **Header:** `0xFF 0xFF` (2 bytes)
- **Length (`numBytes`):** 1 byte = `1 (Opcode) + DataLength + 1 (Checksum)`
- **Opcode (`Type`):** 1 byte representing the command or query
- **Checksum Calculation:**
  $$\text{Checksum} = (\text{numBytes} + \text{Opcode} + \sum \text{PayloadBytes}) \pmod{256}$$

### 5.2 Decoded Protocol Opcode Catalog

| Opcode | Command Name | Direction | Payload Type | Description |
| :---: | :--- | :---: | :--- | :--- |
| `0x01` | `moveForward` | TX | None | Initiates forward walking |
| `0x02` | `turnRight` | TX | None | Initiates right turning step |
| `0x03` | `moveRight` | TX | None | Initiates right side-step |
| `0x04` | `moveSouthEast`| TX | None | Steps backward to the right |
| `0x05` | `moveBackward` | TX | None | Initiates backward walking |
| `0x06` | `moveSouthWest`| TX | None | Steps backward to the left |
| `0x07` | `moveLeft` | TX | None | Initiates left side-step |
| `0x08` | `turnLeft` | TX | None | Initiates left turning step |
| `0x0B` | `handshake` | TX/RX | None / 0x00 | Connection ping / alive handshake |
| `0x0C` | `stop` | TX/RX | None | Immediate halt for all motors |
| `0x0D` | `volume` | TX | Byte ($0-140$) | Sets speaker volume |
| `0x0F` | `state` | TX/RX | 8-byte struct | Telemetry query: pattern, battery, volume, progress, autoStand, autoTurn, autoPose, autoOff |
| `0x10` | `userNames` | TX/RX | String stream | List saved custom user choreography files |
| `0x11` | `autoStand` | TX | Boolean (`0x00`/`0x01`) | Toggle fall recovery get-up routine |
| `0x13` | `autoOff` | TX | Boolean (`0x00`/`0x01`) | Toggle sleep/auto power-down timer |
| `0x14` | `actionNames` | TX/RX | String stream | List built-in action catalog |
| `0x16` | `folderNames` | TX/RX | String stream | List audio & motion categories |
| `0x17` | `action` | TX/RX | String + Progress byte | Trigger predefined action (e.g. `"ProAction/Left Punch"`, `"Action/Boogaloo"`) |
| `0x18` | `audioNames` | TX/RX | String stream | List available audio track IDs |
| `0x19` | `audio` | TX | String | Play audio track (e.g. `"AppSysMS/101"`) |
| `0x1A` | `autoTurn` | TX | Boolean (`0x00`/`0x01`) | Toggle IMU yaw balance correction |
| `0x1B` | `autoPose` | TX | Boolean (`0x00`/`0x01`) | Toggle autonomous idle poses |
| `0xE6` | `program` | TX/RX | 25-byte struct | Enter programming mode & read initial pose |
| `0xE7` | `programExit` | TX | None | Exit programming mode |
| `0xE8` | `jointMove` | TX | 25-byte struct | Set 17 servos to target angles + speed |
| `0xE9` | `jointSync` | TX/RX | 25-byte struct | Read real-time live angles from all 17 servos |
| `0xEA` | `jointUnlockAll` | TX | None | Release motor torque on all joints for manual posing |
| `0xEB` | `jointLockAll` | TX | None | Engage motor holding torque |
| `0xED` | `jointLock` | TX | 17-byte bitmask | Lock/unlock individual joints |
| `0xEE` | `play` | TX | Number | Trigger programmed sound index |
| `0xF6` | `kind` | TX/RX | String | Returns model name (e.g. `"K1"`) |
| `0xF7` | `version` | TX/RX | String | Returns firmware version (`"VER:3.03L"`) |
| `0xF8` | `date` | TX/RX | String | Returns firmware build date |
| `0xFA` | `shutdown` / `done` | TX/RX | None | Completion delimiter / power down |

---

## 6. Joint Kinematics & Servo Coordinate Mapping

The K1 possesses **17 digital servos** mapped across 5 body groups ($0-255$ integer scale):

| Servo ID | Joint Name | Byte Index | Default Center | Min Limit | Max Limit | Body Group |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **0** | `leftThigh` | 0 | `126` | 29 | 229 | Left Leg |
| **1** | `leftCalf` | 1 | `65` | 10 | 220 | Left Leg |
| **2** | `leftAnkle` | 2 | `100` | 26 | 226 | Left Leg |
| **3** | `rightThigh` | 3 | `127` | 18 | 218 | Right Leg |
| **4** | `rightCalf` | 4 | `184` | 30 | 240 | Right Leg |
| **5** | `rightAnkle` | 5 | `141` | 26 | 226 | Right Leg |
| **6** | `leftShoulder` | 6 | `222` | 22 | 242 | Left Arm |
| **7** | `rightShoulder` | 7 | `26` | 6 | 226 | Right Arm |
| **8** | `leftHip` | 8 | `125` | 103 | 133 | Left Leg |
| **9** | `leftFoot` | 9 | `116` | 93 | 133 | Left Leg |
| **10** | `rightHip` | 10 | `135` | 119 | 149 | Right Leg |
| **11** | `rightFoot` | 11 | `120` | 105 | 145 | Right Leg |
| **12** | `leftArm` | 12 | `214` | 33 | 233 | Left Arm |
| **13** | `leftHand` | 13 | `146` | 16 | 216 | Left Arm |
| **14** | `rightArm` | 14 | `42` | 34 | 224 | Right Arm |
| **15** | `rightHand` | 15 | `99` | 26 | 226 | Right Arm |
| **16** | `head` | 16 | `123` | 42 (Left) | 202 (Right) | Head Pan |
| **17–23** | *Internal / Padding* | 17–23 | `125` / `100` | 100 | 125 | Padding |
| **24** | `speed` | 24 | `30` | 1 (Fastest) | 100 (Slowest) | Transition Speed |

---

## 7. Python BLE CLI & Persistent Daemon Tooling

Because Node v24 on Windows requires MSVC C++ compilation for `@abandonware/noble`, a native Python BLE subsystem was built using `bleak` and Windows WinRT:

### 1. Persistent BLE Background Daemon ([`scripts/k1_ble_daemon.py`](file:///C:/Users/poomz/nnnn/robosen_block/scripts/k1_ble_daemon.py))
- **Persistent Connection:** Auto-connects to the robot on launch and keeps a long-lived BLE link active to eliminate reconnect latencies.
- **Dynamic 100% Telemetry ACK Resolution:** Actions resolve the exact millisecond the physical robot emits `action_progress: 100%`, enabling instant back-to-back chaining without hardcoded sleep delays.
- **Standing Posture Preservation (`move_head_only`):** Captures live standing angles of all 16 body/leg servos via `0xE9` (`jointSync`) so that neck/head articulations rotate smoothly without snapping leg angles or causing the robot to lose balance.
- **IPC Interface:** Accepts JSON commands via `stdin` (`{"cmd": "action", "action": "punch_left"}`) and streams events over `stdout` (`action_progress`, `action_completed`, `status_update`).

### 2. Quick Command-Line Execution ([`scripts/k1_action.py`](file:///C:/Users/poomz/nnnn/robosen_block/scripts/k1_action.py))
```powershell
# Query Live Telemetry & Battery Status
python scripts/k1_action.py status

# Test Head Servo Articulations & Posture
python scripts/k1_action.py default_stand # Resets all 17 servos to default standing posture
python scripts/k1_action.py head_left    # Turns head to the Left (angle 42)
python scripts/k1_action.py head_right   # Turns head to the Right (angle 202)
python scripts/k1_action.py head_center  # Returns head to Center (calibrated angle 123)
python scripts/k1_action.py head_pan     # Full Sweep (Left -> Right -> Center)

# Martial Arts & Punches
python scripts/k1_action.py punch_left   # ProAction/Left Punch
python scripts/k1_action.py punch_right  # ProAction/Right Punch
python scripts/k1_action.py kung_fu      # ProAction/Kung Fu
python scripts/k1_action.py single_kick  # ProAction/Left Kick

# Dance, Acrobatics & Stunts
python scripts/k1_action.py push_ups     # ProAction/Push Ups (Fixed path)
python scripts/k1_action.py handstand    # ProAction/Handstand
python scripts/k1_action.py boogaloo     # Action/Boogaloo
python scripts/k1_action.py say_hello    # ProAction/Say Hello
python scripts/k1_action.py celebrate    # ProAction/Celebrate
python scripts/k1_action.py do_squats    # ProAction/Do Squats

# Locomotion Steps
python scripts/k1_action.py walk
python scripts/k1_action.py turn_left
python scripts/k1_action.py turn_right
```

### 3. Interactive Joint Kinematics Controller ([`scripts/k1_joint_controller.py`](file:///C:/Users/poomz/nnnn/robosen_block/scripts/k1_joint_controller.py))
Real-time keyboard controller for all 17 digital servos with strict hardware safeguard limit enforcement, visual ASCII gauges, live telemetry, and zero-auto-connect on start:
```powershell
python scripts/k1_joint_controller.py
```
- **Connection:** `C` (Connect/Reconnect) | `D` (Disconnect cleanly)
- **Selection (Vertical):** `↑` / `↓` (or `[` / `]`) to navigate through the 17 servos.
- **Value Articulation (Horizontal):** `←` / `→` (or `PageDown` / `PageUp` for ±10) to adjust angle.
- **Step Size:** `+` / `-` ($1, 2, 5, 10, 20$).
- **Pose Resets:** `R` (selected joint) | `Shift+R` (ALL 17 calibrated standing posture).
- **Torque:** `U` (free joints for manual posing) | `L` (lock holding torque).

### 4. Direct Speaker Volume Utility ([`scripts/set_volume.py`](file:///C:/Users/poomz/nnnn/robosen_block/scripts/set_volume.py))
```powershell
python scripts/set_volume.py 20    # Sets volume to 20% (28/140)
```

### 5. Full Diagnostic Suite ([`scripts/k1_ble_tester.py`](file:///C:/Users/poomz/nnnn/robosen_block/scripts/k1_ble_tester.py))
```powershell
python scripts/k1_ble_tester.py
```

---

## 8. Node-RED Custom Palette: `node-red-contrib-robosen-block` (v2.0)

A dedicated Node-RED palette simulating the physical block-based tangible programming system:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       NODE-RED SIMULATED SIGNAL FLOW                                   │
│                                                                                                        │
│  [ Master Block ] ──Pin 3 (TX)──► [ Smart Block 1 ] ──Pin 3 (TX)──► [ Smart End Terminator ]           │
│  (Emits Seed 0xAA)                (+ Token 0x01, Param 3)           (Validates CRC-8 & Loops to Pin 4) │
│        ▲                                                                    │                          │
│        └──────────────────── Pin 4 Return RX & Broadcast Bus ───────────────┘                          │
│                     │                                                                                  │
│                     ├──────────────────────────────────────────────┐                                   │
│                     ▼ (Phase 1: Binary Return)                     ▼ (Phase 2: Live 0xBB Broadcast)    │
│             [ Master Parser & BLE Queue ]                 [ Smart Block 1 LED: Bright Green! ]         │
│                     │                                                                                  │
│                     ▼ (Bluetooth Low Energy 4.2)                                                       │
│           [ Robosen K1 Robot ]                                                                         │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Nodes in Palette (Version 2.0):
1. **`robosen-master` (Master Block Controller & Gateway):**
   - Supports 2-Phase Binary Protocol (`0xAA`/`0xBB`) with CRC-8 and legacy CSV strings.
   - Clickable canvas button sends `0xAA` seed frame down Pin 3.
   - Output 1: Pin 3 Downstream TX, Output 2: Telemetry, Output 3: Pin 4 RX Broadcast Bus.
   - Dispatches live BLE commands and broadcasts `0xBB` frames to trigger green active step LEDs on smart blocks in real time!
   - HTTP Admin REST Endpoints: `/trigger`, `/info`, `/connect`, `/disconnect`, `/status`.
2. **`robosen-smart-block` (Smart Multi-Action Block - CH32V003):**
   - Push Button action selector (cycles actions on button click).
   - Rotary Knob parameter adjuster (steps 1-10, angle 45°-180°, reps 1-5, delay 1-5s).
   - Dynamic WS2812B RGB LED state machine: turns **Bright Pulsing Green** when actively executing during Phase 2 broadcast.
3. **`robosen-smart-end` (Smart Active Terminator):**
   - Active end-of-chain terminator with CRC-8 validation, footer `0x55` framing, and return loopback into Pin 4.
   - Built-in fault injection toggle to simulate CRC corruption for error testing.
4. **`robosen-protocol-monitor` (Bus Analyzer & Packet Inspector):**
   - Live packet sniffer inspecting raw Hex frames, opcode decoding, parameter tables, and CRC status.
5. **`robosen-tester` (Action Tester / Direct Controller):**
   - Standalone testing node with direct BLE execution, properties dashboard card, and REST endpoints.
6. **`robosen-instruction` / `robosen-end` (Legacy V1 Blocks):**
   - Maintained for backwards compatibility with single-action CSV chains.

### Machine Symlink & Simulation Flows:
- Linked directly into machine's Node-RED via NTFS Directory Junction:
  `C:\Users\poomz\.node-red\node_modules\node-red-contrib-robosen-block` $\longleftrightarrow$ `C:\Users\poomz\nnnn\robosen_block\node-red-contrib-robosen-block`
- **V2 Smart Block Flow**: [`node-red-contrib-robosen-block/examples/robosen_smart_block_flow.json`](node-red-contrib-robosen-block/examples/robosen_smart_block_flow.json).
- **V1 Legacy Flow**: [`node-red-contrib-robosen-block/examples/robosen_simulator_flow.json`](node-red-contrib-robosen-block/examples/robosen_simulator_flow.json).

---

## 9. Tangible Modular Coding Block System Hardware Specification

Designed for screenless STEM learning, physical modular coding blocks snap together in a daisy-chain bus to control the Robosen K1:

### Standardized 4-Pin Pogo Connector Pinout:
* **Pin 1 (`V+`):** Regulated power rail supplied by Master Block ($3.3\text{V}$).
* **Pin 2 (`GND`):** Common system ground.
* **Pin 3 (`UART TX_DOWN`):** Downstream serial point-to-point transmit line (Master $\to$ Block $1 \to$ Block $2 \dots$) / Config Command TX line.
* **Pin 4 (`UART RX_BUS`):** Continuous return rail & live step broadcast bus (Loopback $\to$ Master RX, Master Step Broadcast $\to$ Blocks) / Config ACK response line.

---

## 10. 5-Pillar Master Improvement Plan & Protocol Architecture

1. **Pillar 1: Hardware & Power BOM**
   - **Master Controller**: Upgraded to **ESP32-S3** (Dual-Core Xtensa LX7, Native Bluetooth BLE 5.0, SPI for E-Ink, dual UARTs for Config Dock & Run Port).
   - **Solid Action Blocks**: Built with **$0.15 WCH CH32V003 (32-bit RISC-V)** in SOP-8 package.
   - **No Moving Parts on Action Blocks**: Buttons and potentiometers removed from individual blocks $\to$ BOM cost dropped to **~$0.25–$0.35/block** with $<10\,\mu\text{A}$ idle current.
   - Add magnetic polarity keying, TP4056 USB-C BMS charging, and RC debouncing filters on UART pins.

2. **Pillar 2: Dual-Port Communication Protocol & Resilience**
   - **Config Dock UART (`0xCF`)**: Master flashes action ID and parameter into docked block's internal non-volatile EEPROM/Flash.
   - **Phase 1 (Discovery & Compilation - `0xAA`)**: Forward pipeline token-passing with dynamic index auto-discovery ($1..N$) reading saved flash tokens and CRC-8 protection.
   - **Phase 2 (Execution & Live Feedback - `0xBB`)**: Master broadcasts `[0xBB, StepIndex, TotalSteps, CRC]` across Pin 4 so the active block's WS2812B LED turns bright pulsating green in real time.

3. **Pillar 3: Master ESP32-S3 BLE Firmware**
   - Implement an asynchronous non-blocking command execution queue with $100\%$ action ACK confirmation (`0x17` progress byte `0x64`).
   - Keep-alive pings (`0x0B`), automatic reconnection, and battery telemetry monitoring (`0x0F`).

4. **Pillar 4: Visual UX & Light Choreography (No Buzzer)**
   - **E-Ink Display**: High-contrast, sunlight-readable e-paper screen on Master showing action names, icons, and parameter values.
   - **Silent Classroom Light Language**: Removed noisy piezo buzzers; feedback provided via WS2812B RGB LEDs (cyan dock pulse, color morph, parameter flash count, emerald green save pulse, comet compilation wave, glowing green active step, rainbow victory sparkle).

5. **Pillar 5: Master Config Dock & Solid Action Blocks**
   - **Master UI Controls**: Knob 1 (Action Selector), Knob 2 (Parameter Adjuster), Large tactile Start button.
   - **Non-Volatile Memory**: 192-byte flash on CH32V003 retains action settings indefinitely across power-downs.
   - **Smart End Block**: Active loopback with CRC-8 calculation and green ready indicator.

---

## 11. Academic Research & Coursework Assignments (`assignments/`)

The `assignments/` folder stores academic project coursework, literature reviews, and research summaries assigned by professors:

### 11.1 Assignment 01: Literature Review on Related Research
* **File:** [`assignments/as01_เอกสารสรุปงานวิจัยที่เกี่ยวข้อง.pdf`](assignments/as01_เอกสารสรุปงานวิจัยที่เกี่ยวข้อง.pdf)
* **Summary:** [`assignments/RESEARCH_SUMMARY.md`](assignments/RESEARCH_SUMMARY.md)
* **Status:** Verified live against all publisher sources. 100% accurate summaries with strong theoretical and pedagogical alignment to the Tangible Robosen Block project.

| Paper # | Citation & Source | Core Focus & Findings | Project Alignment & Pedagogical Justification |
| :---: | :--- | :--- | :--- |
| **1** | **ELLA: Generative AI-Powered Social Robots for Early Language Development at Home**<br>*(Antony et al., arXiv:2603.12508 / IDC 2026)* | Evaluated in-home social robot with 10 families & kids aged 4–6. Yielded +2.8 target words and high emotional engagement. | Highlights the power of screenless physical social robot interaction for young children (ages 4–6 / 5–7), contrasting LLM storytelling with our computational logic focus. |
| **2** | **Evaluation of the Efficacy of Fine Motor Skill Practice by Using Tangible User Interface through Educational Games in Children with Intellectual Disability**<br>*(Teekeng et al., RMUTSVRJ 2020)* | Experimental study ($N=60$) comparing TUI manipulation against conventional therapy. Found significant hand grip gains ($p<0.05$) and superior motivation. | Provides empirical proof that physical Tangible User Interfaces (TUIs) overcome 2D touchscreen fatigue, boosting physical coordination and sustained attention. |
| **3** | **หุ่นยนต์สื่อการเรียนรู้ปฐมวัย: กรณีศึกษา โรงเรียนเทศบาล 4 ฉลองรัตน (Kinder Bot)**<br>*(Phanpakdee et al., JSET 2025)* | Evaluated Thai early childhood teaching robot with Kindergarten 2 students. Demonstrated 100% functional reliability and top-tier user satisfaction. | Serves as a local Thai classroom benchmark; contrasts Kinder Bot's touchscreen/cloud architecture against our 100% screenless, local BLE closed-loop paradigm. |
| **4** | **Early Childhood Computational Thinking through Tangible Floor-Robot Programming in an eTwinning Community of Practice**<br>*(Foti & Bratitsis, EJEL 2026)* | 24-week DBR study ($N=473$ Greek educators) on floor-robot programming for ages 4–6. Discovered 3 core design principles. | **Direct Pedagogical Justification:** Directly validates our system architecture: (1) physical magnetic blocks = *explicit sequencing supports*, (2) live pulsing green LED feedback = *testing and debugging cycles*. |

---

## 12. Open Source Licensing, Legal Memory & Compliance (Apache 2.0)

### 12.1 Project Origin & Base License
- **Origin / Upstream Base:** Core reverse-engineered Robosen BLE protocol parser derived from [`RobosenJS`](https://github.com/oklemenz/RobosenJS) by Oliver Klemenz.
- **License Type:** **Apache License 2.0** (Open Source, Permissive, Commercial-Friendly).
- **Public Fork / Repo Location:** [`https://github.com/Nantaphat-Yoktaworn/robosen_block.git`](https://github.com/Nantaphat-Yoktaworn/robosen_block.git)

### 12.2 What You CAN Do (Permissions Granted by Apache 2.0)
1. **Public Ownership & Forking:** You can publish and host this repository publicly on GitHub under your name/organization.
2. **Package Publishing:** You can publish npm packages (`node-red-contrib-robosen-block`) and Python modules.
3. **Commercial Exploitation:** You can sell physical tangible blocks, manufacture hardware, or sell software/services built on this repository.
4. **Modifications & Extensions:** You own the copyright to your own original additions (physical block specs, Node-RED nodes, Python daemons, joint controllers, 2-phase CRC-8 protocol).
5. **Private & Educational Use:** Free use for university research, coursework, and public demos without royalty fees.

### 12.3 What You MUST Do (Compliance Obligations)
1. **Retain `LICENSE` File:** Keep the root `LICENSE` file (Apache 2.0) in all distributions.
2. **Maintain `NOTICE` File:** Retain the `NOTICE` file providing attribution to Oliver Klemenz for the original base and Nantaphat Yoktaworn for modular block extensions.
3. **Notice of Modification:** Modified files and git history must indicate changes made to original files.
4. **Include Disclaimer:** Provide software "AS IS" without warranty or contributor liability.

### 12.4 What You CANNOT Do (Strict Prohibitions)
1. **Do NOT Delete Copyright Notices:** Never remove existing copyright headers from inherited upstream source files.
2. **Do NOT Claim Creation of the Base from Scratch:** Always acknowledge `RobosenJS` as the protocol origin while highlighting your own original architecture.
3. **Do NOT Violate Trademarks:** Robosen is a registered trademark of Robosen Robotics. Software must be marketed as an independent compatible system, never as an official Robosen brand product.

