# RobosenJS & Tangible Coding Block System: Master Project Memory

> **System Overview:** Programmatic Control (Node.js & Python SDK), Custom Node-RED Tangible Block Simulator Palette, and Bluetooth Low Energy (BLE) Reverse Engineering for the **Robosen K1 / Interstellar Scout K1 Series** Humanoid Robot.  
> **Last Updated:** August 29, 2026  
> **FCC ID:** `2ATNWK1` | **Live Verified Robot ID:** `K1-00457` (`3C:A5:51:94:97:70`) | **Firmware:** `VER:3.03L` (Build: `SH2022-07-23`)

---

## 1. Project Architecture & File Organization

```
robosen_block/
├── assignments/
│   ├── as01_เอกสารสรุปงานวิจัยที่เกี่ยวข้อง.pdf # Academic literature review (4 verified research papers)
│   └── RESEARCH_SUMMARY.md               # Presentation-ready markdown summary of AS01 research papers
├── bin/
│   └── k1.js                             # Node.js CLI executable wrapper
├── firmware/
│   ├── arduino_uno_ch32v003_programmer/
│   │   ├── arduino_uno_ch32v003_programmer.ino # Arduino Uno R3 Ardulink SWIO flasher
│   │   └── README.md
│   ├── ch32v003_action_block/
│   │   ├── main.c                        # Unified CH32V003 Action Block firmware (2-Phase Binary V2, Config Dock, WS2812B)
│   │   ├── funconfig.h                   # CH32V003 configuration header
│   │   ├── ch32fun.c / .h / .ld / hw.h   # Core register & startup layer
│   │   ├── build.ps1                     # Native RISC-V build script (2804-byte binary)
│   │   ├── action_block.bin              # Pre-compiled ready-to-flash binary
│   │   └── README.md
│   ├── ch32v003_end_block/
│   │   ├── main.c                        # Smart End Block RISC-V firmware (Active loopback line driver, CRC validation, WS2812B)
│   │   ├── funconfig.h                   # CH32V003 configuration header
│   │   ├── build.ps1                     # Native RISC-V build script (2016-byte binary)
│   │   ├── end_block.bin                 # Pre-compiled ready-to-flash binary (Token 0xEE)
│   │   └── README.md
│   ├── esp32_ch32v003_programmer/
│   │   ├── esp32_ch32v003_programmer.ino # ESP32 / ESP32-S3 SWIO programmer firmware
│   │   ├── dmi.cpp / .h, swio.cpp / .h, target.cpp / .h # DMI / SWIO physical protocol stack
│   │   ├── flash_tool.py                 # Python host CLI flasher with chunked flashing & verification
│   │   └── README.md
│   └── esp32_master/
│       └── esp32_master.ino              # Master Block C++ firmware (ESP32-S3 BLE Central, NVS flash, Dual-Knob UI, Run Chain Engine)
├── recordings/
│   └── K1/
│       └── test.json                     # Recorded joint keyframe motion sequences
├── scripts/
│   ├── control.js                        # Gamepad / Keyboard controller runner (Node.js)
│   ├── main.js                           # Unified startup, demo & health check runner (Node.js)
│   ├── program.js                        # Scripted robot movements & routines (Node.js)
│   ├── prompt.js                         # LLM natural language prompt runner (Node.js)
│   ├── repl.js                           # Interactive REPL session (Node.js)
│   ├── voice.js                          # Voice interaction session (Node.js)
│   ├── k1_ble_daemon.py                  # Persistent background BLE daemon with dynamic 100% progress ACK (Python/Bleak)
│   ├── k1_joint_controller.py            # Interactive 17-joint kinematics controller with safeguard limits (Python)
│   ├── k1_ble_tester.py                  # Live interactive BLE test menu & telemetry monitor (Python/Bleak)
│   └── k1_action.py                      # Fast one-shot action execution, status, and volume CLI (Python/Bleak)
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
│   │   ├── robosen-smart-block.js / .html# Smart Action Block (CH32V003 flash model & LED feedback)
│   │   ├── robosen-smart-end.js / .html  # Smart Active Terminator Block with CRC-8 validation & loopback
│   │   ├── robosen-protocol-monitor.js / .html # Serial Protocol Bus Analyzer & Packet Sniffer
│   │   └── robosen-tester.js / .html     # Standalone action tester & direct controller node
│   ├── examples/
│   │   └── robosen_smart_block_flow.json # Ready-to-import 2-Phase Binary simulation flow
│   ├── package.json                      # Node-RED palette package manifest (v2.0.0)
│   └── README.md                         # Detailed palette documentation & API guide
├── index.d.ts                            # Root TypeScript exports
├── index.js                              # Package entry point (exports K1 and Robot)
├── package.json                          # NPM dependencies and script definitions
├── note.md                               # Quick project guidelines & architecture cheat sheet
├── README.md                             # Comprehensive project master README
├── PROJECT_SUMMARY.md                    # Executive project summary & scope
├── PHYSICAL_BLOCK_SYSTEM_SPEC.md         # Hardware & electrical spec for modular tangible coding blocks (v3.0)
├── PROTOTYPE_01_SPEC.md                  # Comprehensive prototype #01 engineering specification & breadboard pinouts
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
| `0xE0` | `readEE` | TX/RX | String | Internal EEPROM read check |
| `0xE1` | `writeEE` | TX/RX | String | Internal EEPROM parameter write |
| `0xE2` | `dirList` | TX/RX | Path string / Results | Filesystem directory & file explorer (Discovered `/AppSysMS`, `/ProAction`, `/SpeActions`, `/SysCF`, `/SysMS`, `/SysOS`, `/WarnSysMS`) |
| `0xE3` | `fileCheck` | TX/RX | String / `OK` | File existence / checksum verification |
| `0xE6` | `program` | TX/RX | 25-byte struct | Enter kinesthetic programming timeline & read frames |
| `0xE7` | `programExit` | TX | None | Exit programming mode |
| `0xE8` | `jointMove` | TX | 25-byte struct | Direct 17-servo coordinate command + speed |
| `0xE9` | `jointSync` | TX/RX | 25-byte struct | Real-time live angle feedback of all 17 servos |
| `0xEA` | `jointUnlockAll` | TX | None | Release motor torque on all joints for manual posing |
| `0xEB` | `jointLockAll` | TX | None | Re-engage motor holding torque |
| `0xED` | `jointLock` | TX | 17-byte bitmask | Lock/unlock individual joints |
| `0xEE` | `play` | TX | Number | Trigger programmed sound index |
| `0xF0` | `imuStream` | RX | 50-byte struct | High-speed 6-axis IMU & joint telemetry packet |
| `0xF1` | `imuQuery` | TX | None | Query 50-byte IMU / sensor telemetry buffer |
| `0xF5` | `factoryTest` | TX/RX | Byte stream | Factory calibration & testing diagnostics |
| `0xF6` | `kind` | TX/RX | String | Returns model name (`"K1"`) |
| `0xF7` | `version` | TX/RX | String | Returns firmware version (`"VER:3.03L"`) |
| `0xF8` | `date` | TX/RX | String | Returns firmware build date (`"SH2022-07-23"`) |
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

3. **Pillar 3: Master ESP32-S3 BLE Firmware & Smart NVS Pairing**
   - **Smart NVS MAC Binding**: Stores target robot MAC in NVS; on boot, connects directly in $<500\,\text{ms}$ with zero classroom crosstalk.
   - **Teacher E-Ink Pairing Menu**: Long-press (3s) to scan and select nearby `K1-*` robots by RSSI proximity; selected robot becomes new persistent default MAC.
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

---

## 13. Project Workflow Guidelines & Core Architecture Summary

### 13.1 Agent Workflow & Interaction Rules
1. **Propose & Await Order:** Always discuss and propose design decisions/solutions first. Do **NOT** modify project files, commit, or push until explicitly ordered/confirmed by the user.
2. **Proactive Commit Reminders:** Whenever uncommitted changes exist, or before transitioning to a new topic/task, actively recommend and remind the user to commit and push to keep git history clean.
3. **Repository State:** The repository [`https://github.com/Nantaphat-Yoktaworn/robosen_block.git`](https://github.com/Nantaphat-Yoktaworn/robosen_block.git) is strictly **PRIVATE**.

### 13.2 Consolidated Hardware & Protocol Decisions
- **System Block Diagram:** Stored at `docs/diagrams/robosen_system_block_diagram.png` (`Robosen Block Diagram (1).png`).
- **Master Block (ESP32-S3):**
  - **Dual Interfaces:** (1) **Config Port (Dock)** to program 1 block via UART `0xCF`, (2) **Run Port (Chain)** to execute the multi-block sequence (`0xAA`/`0xBB`).
  - **Run Port Pinout (Right):** Pin 1 = `V+ (3.3V)`, Pin 2 = `GND`, Pin 3 = `TX` (Downstream Seed `0xAA`), Pin 4 = `RX` (Return Program `0xAA` & Step Broadcast `0xBB`).
  - **Config Port Pinout (Dock/Left):** Pin 1 = `V+ (3.3V)`, Pin 2 = `GND`, Pin 3 = `RX` (Reads `0x06` ACK), Pin 4 = `TX` (Writes `0xCF` Config).
  - **User Interface:** High-contrast 1.54"/2.13" E-Ink display, Dual EC11 Incremental Rotary Encoders with detent clicks (Knob 1 = Action, Knob 2 = Parameter with bidirectional stepping & firmware bounds clamping), large tactile Start button.
  - **Silent Classroom Feedback:** No buzzer; multi-state WS2812B RGB light choreography (cyan dock pulse, color morph, parameter flash count, emerald green save pulse, comet compilation wave, glowing green active step, rainbow victory sparkle).
  - **Smart NVS BLE Pairing:** Stores last manually paired robot MAC in NVS. Direct instant boot in $<500\,\text{ms}$ with zero classroom crosstalk. Long-press (3s) opens E-Ink Teacher Pairing Menu sorted by RSSI proximity.
- **Solid Action Blocks (WCH CH32V003):**
  - **Zero Moving Parts:** No buttons or potentiometers on individual blocks.
  - **Ultra-Low BOM:** CH32V003 (SOP-8, ~$0.15) + WS2812B RGB LED + 4-pin magnetic pogo connector (~$0.25–$0.35 total BOM).
  - **Non-Volatile Storage:** Action Token ID and Parameter stored inside internal 192-byte flash/EEPROM emulation; retains configuration indefinitely without battery power.
  - **100% Planar Non-Overlapping Wiring:**
    - Pin 1 (`V+ 3.3V`) $\rightarrow$ Top Rail straight pass-through $\rightarrow$ drops to `VDD` & `WS2812 VCC`.
    - Pin 2 (`GND`) $\rightarrow$ Second Rail straight pass-through $\rightarrow$ connects to `GND` & `WS2812 GND`.
    - Pin 3 (`UART In/Out`) $\rightarrow$ Upstream Pin 3 enters `PD6 (RX)`; `PD5 (TX)` exits to Downstream Pin 3.
    - `PA2 (GPIO Data)` $\rightarrow$ drops directly down into `WS2812 DIN`.
    - Pin 4 (`PASS_THRU / RX_BUS`) $\rightarrow$ Bottom Rail straight pass-through with zero line intersections.
  - **Pin 4 Multidrop Electrical Safety:** High-impedance (Hi-Z) input during Run Mode. End Block `TX` is the sole active driver on Pin 4 during return; Action Blocks ignore `0xAA` frames and process `0xBB` execution frames.

---

## 14. Physical Silicon Milestone: CH32V003 Action Block & ESP32-S3 Programmer

- **Flashing Date:** September 7, 2026
- **Target Microcontroller:** TENSTAR CH32V003F4P6 (TSSOP-20 breakout, 32-bit RISC-V QingKe V2A core @ 24MHz).
- **Physical Programmer:** ESP32-S3 DevKit on `COM3` running [`esp32_ch32v003_programmer.ino`](file:///C:/Users/nnnn/Projects/robosen_block/firmware/esp32_ch32v003_programmer/esp32_ch32v003_programmer.ino).
- **Wiring Setup:**
  - ESP32-S3 `GPIO 10` $\longleftrightarrow$ CH32V003 `PD1 (SWIO)` with 4.7kΩ–10kΩ pull-up to 3.3V.
  - ESP32-S3 `3.3V` & `GND` $\longleftrightarrow$ CH32V003 `V` & `G`.
- **Toolchain Environment:**
  - Local `riscv32-esp-elf-gcc` (v14.2.0) compiling bare-metal with `-march=rv32ec_zicsr -mabi=ilp32e`.
  - Binary size: `2,380 bytes` (out of 16,384 bytes flash capacity).
- **Verification Results:**
  - SWIO 1-wire synchronization: `0x5AA50401`
  - Chip ID readback: `0xF8076713`
  - Memory write: 10 chunks (256 bytes each) programmed into flash `0x08000000`.
  - Byte-for-byte readback verification: **100% MATCH (0 mismatches)**.
  - Target execution resumed via `targetResetRun()`.
- **Firmware Capabilities:**
  - Config Port Protocol (`0xCF`): Non-volatile flash parameter storage at `0x08003FC0`, ACK transmission, and emerald green save animation.
  - Run Chain Phase 1 (`0xAA`): Dynamic discovery, indexing (`g_my_index`), token appending, and CRC-8 recalculation.
  - Run Chain Phase 2 (`0xBB`): Real-time step tracking (bright green pulse when active), idle action colors, and rainbow victory sparkle on `0xFF`.

---

## 15. Master Config Dock Live Action Block Detection & Query

- **Config Port Interface:** Master `Serial1` on `GPIO 17` (`CFG_TX`) and `GPIO 18` (`CFG_RX`) @ 115200 baud.
- **Protocol Subcommands (`0xCF`):**
  - **Read Stored Config Query (`0x01`):** Master sends `[0xCF, 0x01, 0x07, 0x55]`. Action Block replies with `[0xCF, 0x81, ACTION_ID, PARAM_VAL, CRC8, 0x55]`.
  - **Write New Config (`0x02`):** Master sends `[0xCF, 0x02, ACTION_ID, PARAM_VAL, CRC8, 0x55]`. Action Block writes to flash, flashes WS2812B emerald green, and replies with ACK `[0xCF, 0x06, CRC8, 0x55]`.
- **Master UI Display:**
  - When docked: `║ Config Dock: DOCKED 🟢 [0x01] Walk Forward (1 Steps) ║`
  - When empty: `║ Config Dock: EMPTY ⚪ (No Action Block Connected) ║`
- **Knob 1 Interaction:** When a block is docked, clicking Knob 1 burns the Master's selected action & parameter directly into that block.
- **Hardware Verification (September 7, 2026):**
  - ✅ **Physical Silicon End-to-End Success:** Verified live detection of TENSTAR CH32V003 (`[0x10] Left Punch`), burning new action (`0x14: Push-ups, 1 Reps`), receiving flash write ACK `0x06`, and real-time Master UI update to `Config Dock: DOCKED 🟢 [0x14] Push-ups (1 Reps)`.
  - **Linker Script Bug Resolution:** Identified and resolved memory map collision in bare-metal toolchain where unpreprocessed `ch32fun.ld` assigned `sp = 0x20180000` (causing immediate HardFault on boot). Implemented automated preprocessor stage in `build.ps1` generating `ch32fun_003.ld` with valid 2KB SRAM boundaries (`0x20000000 - 0x20000800`).
  - **AFIO Peripheral Clock:** Enabled `RCC_APB2Periph_AFIO` to ensure alternate function multiplexer routes USART1 TX/RX cleanly to `PD5` / `PD6`.

---

## 16. CH32V003 Smart End Block Firmware Architecture & Silicon Flash

- **Flashing Date:** September 7, 2026
- **Firmware Location:** [`firmware/ch32v003_end_block/`](firmware/ch32v003_end_block/) (`main.c`, `build.ps1`, `end_block.bin` = 2016 bytes).
- **Architecture & Electrical Design:**
  - Unlike a passive U-turn copper bridge (which suffers from cumulative contact resistance over $2 \times N$ magnetic pogo joints), the **Smart End Block** functions as an **active digital line driver**.
  - Internal pull-up role select: `PD0` tied to `GND` configures the chip as End Terminator (Token `0xEE`).
  - Validates cumulative CRC-8 checksum of incoming Phase 1 (`0xAA`) frames before retransmitting them onto Pin 4 Return Rail directly to Master.
  - Visual Feedback: Calm emerald green glow on boot and valid loopback; synchronized rainbow sparkle upon receiving Phase 3 (`0xBB 0xFF`) completion broadcast.
- **Config Dock Recognition:** Docked End Block is immediately identified by Master UI as `Config Dock: DOCKED 🟢 [0xEE] End Terminator (0 Cap)`.
- **Silicon Flash Verification:** Flashed onto IC #2 via `flash_tool.py` on `COM3`. 100% byte-for-byte readback verification confirmed.

---

## 17. Run Chain Engine End-to-End Hardware Verification

- **Verification Date:** September 8, 2026
- **Hardware Topology:**
  - ESP32-S3 Master: `GPIO 15` (Chain TX) and `GPIO 16` (Chain RX) @ 115200 baud.
  - Action Block 1 (IC #1): `PD6` (RX) $\longleftarrow$ Master `GPIO 15`; `PD5` (TX) $\longrightarrow$ End Block `PD6`.
  - Smart End Block (IC #2): `PD6` (RX) $\longleftarrow$ Block 1 `PD5`; `PD5` (TX) $\longrightarrow$ Master `GPIO 16`.
  - Common 3.3V & GND across breadboards.
- **Verified Protocol Execution:**
  1. **Phase 1: Discovery & Compilation (`0xAA`):**
     - Master emits seed `[0xAA, Len=0, Count=0, CRC=0x00, 0x55]`.
     - Block 1 appends stored action `0x14` (Push-ups) and param `1`, increments count to 1, updates CRC-8.
     - Smart End Block validates cumulative CRC-8 and actively transmits sequence over Pin 4 return rail to Master `GPIO 16`.
     - Master logs: `🟢 Loopback Verified! Sequence Compiled: 1 Steps, CRC: 0xXX (VALID ✓)`.
  2. **Phase 2: Real-Time Step Execution (`0xBB`):**
     - Master broadcasts active step frame `[0xBB, ActiveStep=1, Total=1, CRC8, 0x55]`.
     - Block 1 WS2812B illuminates in **Bright Pulsating Green (100% brightness)**.
     - Master dispatches BLE motion packet to Robosen K1 robot over persistent BLE link.
  3. **Phase 3: Mission Complete Celebration (`0xBB 0xFF`):**
     - Master broadcasts completion frame `[0xBB, ActiveStep=0xFF, Total=1, CRC8, 0x55]`.
     - Block 1, Smart End Block, and Master onboard WS2812B simultaneously trigger synchronized **Rainbow Victory Sparkle**!
- **Control Interface:**
  - Single tap on physical Start Button (`GPIO 14`) probes the Run Chain; aborts and warns if chain is open-circuit.
  - Manual `'r'` / `'R'` command in Serial Monitor enables interactive diagnostic testing.

---

## 18. Multi-Block Daisy Chain Silicon Verification & Silent Bus

- **Verification Date:** September 8, 2026
- **Topology:** Master (ESP32-S3) $\longrightarrow$ Action Block 1 (`0x01` Walk Forward, 1 step) $\longrightarrow$ Action Block 2 (`0x10` Left Punch, 2 reps) $\longrightarrow$ Smart End Block (`0xEE`) $\longrightarrow$ Master Return Rail (`GPIO 16`).
- **Compiled Sequence on Silicon:**
  ```text
  ╔════════════════════════════════════════════════════════════════════════╗
  ║                 [RUN CHAIN ENGINE] PHASE 1: DISCOVERY                  ║
  ╠════════════════════════════════════════════════════════════════════════╣
  ║ Emitting Discovery Seed [0xAA, 0, 0, 0, 0x55] on GPIO 15 (TX)...       ║
  ║ 🟢 Loopback Verified! Sequence Compiled: 2 Steps, CRC: 0x44 (VALID ✓) ║
  ╠════════════════════════════════════════════════════════════════════════╣
  ║  Step 1: [0x01] Walk Forward         Parameter:   1 Steps         ║
  ║  Step 2: [0x10] Left Punch           Parameter:   2 Reps          ║
  ╚════════════════════════════════════════════════════════════════════════╝
  ```
- **Silent Bus Architecture:**
  - Eliminated periodic 1000ms `0xCF` broadcast announcement frames and boot spam from both Action Block and End Block firmware.
  - UART TX lines remain 100% silent during idle periods, preventing bus contention and corruption when multiple blocks are connected in series.
  - Blocks transmit on TX *only* when queried by Master (`0xCF`) or when forwarding/terminating Run Chain packets (`0xAA` / `0xBB`).
- **Strict Chain Verification:**
  - Master strictly requires a valid loopback packet from the return rail. If open-circuit or corrupted, Master aborts execution and flashes status LED red (single-knob fallback removed).

---

## 19. CH32V003 Non-Volatile Flash Memory Persistence Fix

- **Root Cause Analysis:**
  - In `firmware/ch32v003_action_block/main.c`, a custom `FlashController` struct omitted a 4-byte `RESERVED` register at offset `0x18`.
  - This shifted `MODEKEYR` to offset `0x28` (`BOOT_MODEKEYR`) instead of `0x24` (`MODEKEYR`). As a result, `MODEKEYR` was never unlocked (`FLASH->CTLR & 0x8080` remained locked), causing all flash writes to be silently discarded.
  - Furthermore, CH32V003 64-byte Fast Page Programming requires loading all 16 words into the hardware row buffer accompanied by `FLASH_CTLR_PAGE_PG | FLASH_CTLR_BUF_LOAD` before triggering `FLASH_CTLR_STRT`.
- **Silicon Fix Applied:**
  - Migrated to the native `FLASH` peripheral defined in `ch32v003hw.h`.
  - Proper unlock sequence: write `FLASH_KEY1` and `FLASH_KEY2` to both `FLASH->KEYR` and `FLASH->MODEKEYR`.
  - Implemented full FPEC sequence: Page Erase (`FLASH_CTLR_PAGE_ER`) $\longrightarrow$ Buffer Reset (`FLASH_CTLR_BUF_RST`) $\longrightarrow$ 16-word Row Buffer Load (`FLASH_CTLR_BUF_LOAD`) $\longrightarrow$ Page Write (`FLASH_CTLR_STRT`) $\longrightarrow$ Re-lock (`FLASH_CTLR_LOCK`).
  - Storage location: Top 64-byte page of 16KB flash (`0x08003FC0`).
- **Verification:** Verified live on silicon across full power-cycles (unplugging 3.3V/GND and reconnecting); Action Block permanently retains burned action and parameter.

---

## 20. Robot Locomotion Settling & Full Multi-Action Timing Calibration

- **Root Cause of Skipped Action in Multi-Step Chains:**
  - When transitioning from a locomotion command (e.g. `Walk Forward`) to a predefined motion (e.g. `Left Punch`), Master sent `Locomotion Stop` (`0x0C`: Gait Stand & Lock), but had 0ms settling delay after transmitting the stop packet.
  - The bipedal robot's physical gait requires ~1000–1200ms to decelerate, place swinging foot flat on the floor, and engage standing balance PID.
  - Receiving an action command (`0x17`) while the robot is still transitioning from gait to stand causes the K1's onboard firmware to **silently drop/reject** the action command.
  - In a 2-rep punch sequence, Rep 1 was dropped while the robot finished stopping; Rep 2 was sent 4000ms later when the robot was idle, causing the robot to execute only Rep 2 (skipping Rep 1).
- **Engine Resolution in `esp32_master.ino`:**
  1. **Post-Locomotion Settling Delay:**
     - Added **1200ms delay** after `stopPacket` (`0x0C`) in `isWalk` (Walk Forward, Walk Backward, Side-step Left, Side-step Right).
     - Added **1000ms delay** after `stopPacket` (`0x0C`) in `isTurn` (Turn Left, Turn Right).
  2. **Inter-Repetition Pause:**
     - Added **400ms settling pause** between consecutive repetitions of predefined actions.
  3. **Action Duration Calibration:**
     - `Left Punch` / `Right Punch`: 2500ms
     - `Single Kick` / `Left Kick`: 7000ms
     - `Push Ups`: 12000ms
     - `Handstand`: 18000ms
     - `Kung Fu`: 11000ms
     - `Boogaloo` (Dance): 55000ms (or 10000ms)
     - `Do Squats`: 20000ms
     - `Say Hello` (Wave Hand): 8500ms
     - `Celebrate`: 8000ms
  4. **Payload & Opcode Corrections:**
     - Added lateral side-step opcodes `0x07` (Move Left) and `0x03` (Move Right) to the locomotion handler with proper `0x0C` stop and 1200ms settling delay.
     - Corrected string payloads in `getActionObjByToken()`: Dance $\longrightarrow$ `"Action/Boogaloo"`, Single Kick $\longrightarrow$ `"ProAction/Left Kick"`, Squats $\longrightarrow$ `"ProAction/Do Squats"`.
  5. **Chain Inter-Step Settling:** Increased inter-step delay in `executeRunChain()` to **500ms**.
- **Live Hardware Verification:** Walk Forward 1 step followed by Left Punch 2 reps confirmed executing flawlessly on physical Robosen K1 robot.

---

## 21. Master Block Battery & Power Management Subsystem Architecture

- **Documentation Date:** September 22, 2026
- **Subsystem Scope:** Standalone battery power supply, USB-C charging, BMS protection, and regulated 3.3V DC-DC power delivery for the Master Block (ESP32-S3), Config Dock, and Run Chain daisy-bus.

### 21.1 Selected Bill of Materials (BOM)

| Item # | Component | Specification | Qty | Role & Electrical Notes |
| :---: | :--- | :--- | :---: | :--- |
| **1** | **TP4056 USB-C Charger Board with Protection** | 5V 1A Li-ion charger with integrated **DW01A** + **FS8205A** | 1 | Handles USB-C charging, overcharge ($4.28\text{V}$), overdischarge ($2.4\text{V}$), and short-circuit cutoff. (No need for discrete DW01/FS8205A chips). |
| **2** | **LG Chem INR18650-MJ1 Cell** | 3.7V nominal, 3500mAh, 10A discharge | 1 | High-capacity power source providing ~25 to 45+ hours of continuous classroom operation. |
| **3** | **TPS63020 Buck-Boost Module** | Synchronous DC-DC regulator, 1.8V–5.5V input $\to$ **3.3V fixed output** (up to 2A buck / 1.2A boost) | 1 | Seamlessly bucks down (4.2V $\to$ 3.3V) and boosts up (3.0V $\to$ 3.3V), eliminating ESP32-S3 brownouts during BLE RF bursts. |
| **4** | **18650 Battery Holder** | Single-slot 18650 holder with pre-soldered wire leads | 1 | Safe mechanical battery mounting without soldering directly onto cell terminals. |
| **5** | **SPST Slide / Toggle Switch** | Mini 2-position slide switch ($\ge 0.5\text{A}$) | 1 | System Power ON/OFF switch placed between TP4056 `OUT+` and TPS63020 `VIN`. |
| **6** | **Hookup Wire** | 22–24 AWG stranded copper wire (Red & Black) | ~1m | Power rail connections between modules and to ESP32-S3. |

### 21.2 Power Budget & Runtime Analysis (3500mAh @ 3.3V)

- **Total Usable Energy at 3.3V:** $\approx \frac{3.7\text{V} \times 3500\text{mAh} \times 0.90}{3.3\text{V}} \approx \mathbf{3{,}530\text{ mAh}}$.
- **Average Current Draw:**
  - **Idle / Config Mode:** ~80 mA (ESP32-S3 BLE idle + 1 docked block + E-Ink static) $\longrightarrow$ **~44 Hours**.
  - **Typical Classroom Use (5-Block Chain):** ~140 mA (ESP32-S3 + 5 Action Blocks + Smart End Block + LEDs) $\longrightarrow$ **~25 Hours** (~4 full school days).
  - **Heavy / Continuous Execution (8-Block Chain):** ~220 mA (Continuous BLE stream + 8 blocks + max LED pulse) $\longrightarrow$ **~16 Hours**.
  - **Deep Sleep:** $< 50\,\mu\text{A}$ $\longrightarrow$ **> 2 Years** shelf life.

### 21.3 Full System Wiring & Schematic Diagram

```text
====================================================================================================
                                      MASTER BLOCK FULL WIRING
====================================================================================================

 [ 18650 LG MJ1 3500mAh ]
    (+) Red wire   (-) Black wire
     │                 │
     ▼                 ▼
   [ B+ ]            [ B- ]
 ┌───────────────────────────────┐
 │ TP4056 + DW01A + FS8205A      │◄─── [ USB-C 5V Input ] (Charging Port)
 │ (Protected Charger Board)     │
 └───────┬───────────────┬───────┘
       [OUT+]          [OUT-] (BMS GND)
         │               │
         ▼               │
  [SPST Power Switch]    │
         │               │
         ▼               ▼
       [VIN]           [GND]
 ┌───────────────────────────────┐
 │ TPS63020 Buck-Boost Module    │
 │ (Tie EN -> VIN to enable)     │
 │ (Tie PS -> GND for power save)│
 └───────┬───────────────┬───────┘
       [VOUT]          [GND]
         │ (Clean 3.3V)  │ (Common Ground)
         │               │
 ════════╪═══════════════╪═════════════════════════════════════════════════════════════════════════
         │               │                     COMMON POWER RAILS (+3.3V & GND)
 ════════╪═══════════════╪═════════════════════════════════════════════════════════════════════════
         │               │
         ├───────────────┼──────────────────────┐
         │               │                      │
         ▼               ▼                      │
    ┌─────────┐     ┌─────────┐                 │
    │   3V3   │     │   GND   │                 │
 ┌──┴─────────┴─────┴─────────┴────────────────┐│
 │                                             ││
 │         ESP32-S3 MASTER CONTROLLER          ││
 │                                             ││
 │   GPIO 8  (PIN_K1_CLK) ──► Knob 1 CLK       ││
 │   GPIO 9  (PIN_K1_DT)  ──► Knob 1 DT        ││
 │   GPIO 10 (PIN_K1_SW)  ──► Knob 1 Switch    ││
 │                                             ││
 │   GPIO 11 (PIN_K2_CLK) ──► Knob 2 CLK       ││
 │   GPIO 12 (PIN_K2_DT)  ──► Knob 2 DT        ││
 │   GPIO 13 (PIN_K2_SW)  ──► Knob 2 Switch    ││
 │                                             ││
 │   GPIO 14 (PIN_START)  ──► Start Button (NO)││
 │                                             ││
 │   GPIO 17 (CFG_TX) ────┐                    ││
 │   GPIO 18 (CFG_RX) ──┐ │                    ││
 │                      │ │                    ││
 │   GPIO 15 (CHAIN_TX) ┼─┼───────┐            ││
 │   GPIO 16 (CHAIN_RX) ┼─┼─────┐ │            ││
 └──────────────────────┼─┼─────┼─┼────────────┘│
                        │ │     │ │             │
                        │ │     │ │             ▼
 ┌──────────────────────┼─┼─────┼─┼─────────────┐
 │                      │ │     │ │             │
 │   KNOBS & BUTTON:    │ │     │ │             │
 │   • Knob 1 VCC / + ──┼─┼─────┼─┼─────────────┼──► +3.3V Rail
 │   • Knob 1 GND ──────┼─┼─────┼─┼─────────────┴──► GND Rail
 │   • Knob 2 VCC / + ──┼─┼─────┼─┼─────────────┬──► +3.3V Rail
 │   • Knob 2 GND ──────┼─┼─────┼─┼─────────────┴──► GND Rail
 │   • Start Btn Return ┼─┼─────┼─┼────────────────► GND Rail
 │                      │ │     │ │
 │   CONFIG DOCK PORT:  │ │     │ │
 │   • Pin 1 (V+) ──────┼─┼─────┼─┼─────────────┬──► +3.3V Rail
 │   • Pin 2 (GND) ─────┼─┼─────┼─┼─────────────┴──► GND Rail
 │   • Pin 3 (CFG_RX) ◄─┘ │     │ │                  (Receives ACK from docked block)
 │   • Pin 4 (CFG_TX) ◄───┘     │ │                  (Flashes config to docked block)
 │                              │ │
 │   RUN CHAIN PORT:            │ │
 │   • Pin 1 (V+) ──────────────┼─┼─────────────┬──► +3.3V Rail (Powers whole chain)
 │   • Pin 2 (GND) ─────────────┼─┼─────────────┴──► GND Rail
 │   • Pin 3 (CHAIN_TX) ◄───────┘ │                  (Sends 0xAA discovery seed)
 │   • Pin 4 (CHAIN_RX) ◄─────────┘                  (Receives loopback from End Block)
 └──────────────────────────────────────────────┘
```

### 21.4 Pin-to-Pin Reference Table

| Subsystem | Source Component & Pin | Target Pin | Wire Color / Notes |
| :--- | :--- | :--- | :--- |
| **Battery In** | 18650 Battery (+) | TP4056 **`B+`** | 🔴 Red |
| | 18650 Battery (-) | TP4056 **`B-`** | ⚫ Black |
| **Power Switch**| TP4056 **`OUT+`** | SPST Switch Terminal 1 | 🔴 Red |
| | SPST Switch Terminal 2 | TPS63020 **`VIN`** & **`EN`** | 🔴 Red *(Tying EN to VIN turns regulator on with switch)* |
| **Regulator In**| TP4056 **`OUT-`** | TPS63020 **`GND`** | ⚫ Black *(Protected ground)* |
| | TPS63020 **`PS`** | TPS63020 **`GND`** | 🔵 Blue *(Enables Power Save Mode)* |
| **Regulator Out**| TPS63020 **`VOUT`** | ESP32-S3 **`3V3`** & Common Rail | 🔴 Red *(Regulated 3.3V DC)* |
| | TPS63020 **`GND`** | ESP32-S3 **`GND`** & Common Rail | ⚫ Black |
| **Knob 1 (Action)**| `PIN_K1_CLK` | ESP32-S3 **GPIO 8** | 🟡 Yellow |
| | `PIN_K1_DT` | ESP32-S3 **GPIO 9** | 🟢 Green |
| | `PIN_K1_SW` | ESP32-S3 **GPIO 10** | 🔵 Blue |
| **Knob 2 (Param)** | `PIN_K2_CLK` | ESP32-S3 **GPIO 11** | ⚪ White |
| | `PIN_K2_DT` | ESP32-S3 **GPIO 12** | 🟤 Brown |
| | `PIN_K2_SW` | ESP32-S3 **GPIO 13** | 🔘 Gray |
| **Start Button** | `PIN_START_BTN` | ESP32-S3 **GPIO 14** & `GND` | 🟠 Orange *(Active LOW)* |
| **Config Dock** | `PIN_CFG_TX` | Dock Pin 4 (`CFG_TX`) | ESP32-S3 **GPIO 17** |
| | `PIN_CFG_RX` | Dock Pin 3 (`CFG_RX`) | ESP32-S3 **GPIO 18** |
| | Power Rails | Dock Pin 1 (`V+`) & Pin 2 (`GND`) | Connected to 3.3V & GND |
| **Run Port** | `PIN_CHAIN_TX` | Run Pin 3 (`DATA`) | ESP32-S3 **GPIO 15** |
| | `PIN_CHAIN_RX` | Run Pin 4 (`PASS_THRU`) | ESP32-S3 **GPIO 16** |
| | Power Rails | Run Pin 1 (`V+`) & Pin 2 (`GND`) | Connected to 3.3V & GND |
